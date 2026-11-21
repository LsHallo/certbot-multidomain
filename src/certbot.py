# Custom logging setup
from datetime import datetime, timezone, timedelta
from typing import Literal, LiteralString

from cryptography import x509

from modules.logging import setup_logging, get_logger
setup_logging()

# Parse & get environment variables
from modules.env import *

# Library imports
import subprocess
import schedule
import random
import shlex
import time
import yaml
import os


# Create application logger
logger = get_logger('Certbot Multidomain', IS_DEBUG)
logger.debug("DEBUG MODE ENABLED!")


# Load & parse config file
config: dict = None
logger.debug(f"Opening & parsing config file '{CONFIG_PATH}'...")
with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)


def is_valid(cert_path: LiteralString | str | bytes) -> bool:
    with open(cert_path, "rb") as cert_file:
        certs = x509.load_pem_x509_certificates(cert_file.read())

    if not certs:
        raise ValueError("No certificates found in PEM file")

    # Find the leaf certificate (CA:FALSE).
    leaf_certs = []

    for cert in certs:
        try:
            constraints = cert.extensions.get_extension_for_class(
                x509.BasicConstraints
            ).value
        except x509.ExtensionNotFound:
            continue

        if not constraints.ca:
            leaf_certs.append(cert)

    if len(leaf_certs) != 1:
        raise ValueError(
            f"Expected exactly one leaf certificate, found {len(leaf_certs)}"
        )

    cert = leaf_certs[0]

    logger.debug(f"Cert expiry: {cert.not_valid_after_utc}")

    return cert.not_valid_after_utc > (
        datetime.now(timezone.utc) + timedelta(days=30)
    )


def request_initial_certs():
    """
    Request initial certificates for configured domains.
    If the certificate file doesn't already exist, certbot will be called to request new certificates.

    """
    for key, domain in config.get("domains").items():
        cert_path = os.path.join(CERT_OUTPUT_PATH, 'live', domain.get("cert_name", key), 'fullchain.pem')
        logger.debug(f"Checking for existing cert {cert_path}")
        if os.path.isfile(cert_path) and is_valid(cert_path):
            logger.info(f"Cert for {key} exists. Just creating renew job.")
            continue

        else:
            logger.info(f"Requesting new certificate for {key}.")
            domain_list = generate_domain_list(key, domain)
            certbot_cmd = f"certbot certonly --non-interactive {'-v --test-cert' if IS_DEBUG else ''} --dns-cloudflare --dns-cloudflare-credentials {domain.get('dns_credentials_file')} --dns-cloudflare-propagation-seconds 25 --email {domain.get('email')} --no-eff-email --agree-tos --config-dir {CERT_OUTPUT_PATH} --rsa-key-size 4096 --cert-name {domain.get('cert_name', key)} {domain_list}"
            logger.debug(f"Certbot command line: {certbot_cmd}")
            certbot_cmd = shlex.split(certbot_cmd)
            
            # Certbot log output will indicate that a cron has been created.
            # This job will not run in the docker container
            certbot_process = subprocess.Popen(certbot_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            certbot_process.wait()
            stdout, stderr = certbot_process.communicate()
            logger.info(stdout)
            logger.error(stderr)


def renew_certs():
    """
    Renew existing certificates.
    Certbot will be called to renew all certificates in the output directory.
    
    """
    logger.info("Renewing certs that will expire soon.")
    certbot_cmd = f"certbot renew --config-dir {CERT_OUTPUT_PATH} {'--dry-run' if IS_DEBUG else ''}"
    logger.debug(f"Certbot command line: {certbot_cmd}")
    certbot_cmd = shlex.split(certbot_cmd)
    certbot_process = subprocess.Popen(certbot_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    certbot_process.wait()
    stdout, stderr = certbot_process.communicate()
    logger.info(stdout)
    logger.error(stderr)

    # Check for valid config and reload nginx
    logger.debug(f"Reloading Nginx configuration for container '{NGINX_CONTAINER_NAME}' to apply certs.")
    ret_code = os.system(f"docker exec {NGINX_CONTAINER_NAME} sh -c 'nginx -t && nginx -s reload'")
    if ret_code == 0:
        logger.debug("Reload successful!")
    else:
        logger.error("Nginx reload failed! See above for details.")
        logger.debug(f"Exit code: {ret_code}")
    logger.info("Renew complete.")


def generate_domain_list(key: str, domain: dict):
    """
    Generates domain list string for certbot request command.

    """
    subdomains = domain['subdomains'] if isinstance(domain['subdomains'], list) else [domain['subdomains']]

    # For forgetful people
    if len(subdomains) == 0:
        logger.warning(f"No subdomains specified. Requesting wildcard cert!")
        subdomains = ['wildcard']

    if subdomains[0].lower() == 'wildcard':
        return f'-d {key} -d *.{key}'

    return f'-d {key} -d ' + ' -d '.join([f'{domain}.{key}' for domain in subdomains])


if __name__ == '__main__':
    logger.debug("Requesting initial certs...")
    request_initial_certs()

    # Renew between 02:00 and 04:59
    logger.debug("Scheduling renew task at random time in the morning...")
    schedule.every().day.at(f"{random.randint(2, 4):02d}:{random.randint(0, 59):02d}").do(renew_certs)

    # Main loop
    while True:
        schedule.run_pending()
        time.sleep(60)
