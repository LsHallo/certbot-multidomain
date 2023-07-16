import os
import random
import sys
import time
import schedule
import yaml
import shlex
import logging
import subprocess


config: dict = None


def parse_config(path: str):
    global config
    logging.debug(f"Opening config file f{path}")
    with open(path, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logging.error(repr(e))


def request_initial_certs():
    global config
    for key, domain in config.get("domains").items():
        cert_path = os.path.join(os.getenv("CERT_OUTPUT_PATH", "/app/certs"), 'live',  domain.get("cert_name", key), 'fullchain.pem')
        logging.debug(f"Checking for existing cert {cert_path}")
        if check_cert_exists(cert_path):
            logging.info(f"Cert for {key} exists. Just creating renew job.")
            continue
        else:
            logging.info(f"Requesting new certificate for {key}.")

            domain_list = generate_domain_list(key, domain)
            certbot_cmd = f"certbot certonly --non-interactive --no-autorenew {'-v --test-cert' if os.getenv('DEBUG') is not None else ''} --dns-cloudflare --dns-cloudflare-credentials {domain.get('dns_credentials_file')} --dns-cloudflare-propagation-seconds 25 --email {domain.get('email')} --no-eff-email --agree-tos --config-dir {os.getenv('CERT_OUTPUT_PATH', '/app/certs')} --rsa-key-size 4096 --cert-name {domain.get('cert_name', key)} {domain_list}"
            logging.debug(f"Certbot command line: {certbot_cmd}")

            certbot_cmd = shlex.split(certbot_cmd)
            # Certbot log output will indicate that a cron has been created.
            # This job will not run in the docker container
            certbot_process = subprocess.Popen(certbot_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            certbot_process.wait()
            stdout, stderr = certbot_process.communicate()
            logging.info(stdout)
            logging.error(stderr)


def renew():
    certbot_cmd = f"certbot renew --config-dir {os.getenv('CERT_OUTPUT_PATH', '/app/certs')} {'--dry-run' if os.getenv('DEBUG') is not None else ''}"
    certbot_cmd = shlex.split(certbot_cmd)
    certbot_process = subprocess.Popen(certbot_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    certbot_process.wait()
    stdout, stderr = certbot_process.communicate()
    logging.info(stdout)
    logging.error(stderr)

    # Check for valid config and reload nginx
    logging.debug("Reloading nginx container configuration to apply certs.")
    ret_code = os.system(f"docker exec {os.getenv('NGINX_CONTAINER_NAME', 'nginx')} sh -c 'nginx -t && nginx -s reload'")
    if ret_code == 0:
        logging.debug("Reload successful")
    else:
        logging.error("nginx reload failed! See above for details.")
        logging.debug(f"exit code: {ret_code}")


def check_cert_exists(path: str):
    return os.path.isfile(path)


def generate_domain_list(key: str, domain: dict):
    subdomains = domain['subdomains'] if isinstance(domain['subdomains'], list) else [domain['subdomains']]

    # For forgetful people
    if len(subdomains) == 0:
        logging.warning(f"No subdomains specified. Requesting wildcard cert!")
        subdomains = ['wildcard']

    if subdomains[0].lower() == 'wildcard':
        return f'-d {key} -d *.{key}'

    return f'-d {key} -d ' + ' -d '.join([f'{domain}.{key}' for domain in subdomains])


if __name__ == '__main__':
    if os.getenv('DEBUG', None) is not None:
        level = logging.DEBUG
        frmt = "[%(asctime)s] [%(levelname)s]: %(message)s (%(funcName)s)"
    else:
        level = logging.INFO
        frmt = "[%(asctime)s] [%(levelname)s]: %(message)s"
    logging.basicConfig(stream=sys.stdout, level=level, format=frmt, datefmt="%H:%M:%S")
    logging.debug("DEBUG MODE ENABLED!")

    logging.debug("Application start")
    parse_config(os.getenv("CONFIG_PATH", "/app/config.yml"))

    logging.debug("Initial certs")
    request_initial_certs()

    # renew between 02:00 and 04:59
    schedule.every().day.at(f"{random.randint(2, 4):02d}:{random.randint(0, 59):02d}").do(renew)

    while True:
        schedule.run_pending()
        time.sleep(15)
