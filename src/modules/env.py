import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true', help="Enable debug output and generate only staging certificates")
parser.add_argument('-c', '--config_path', type=str, help="Path to config.yml")
parser.add_argument('-o', '--cert_output_path', type=str, help="Path to cert output")
parser.add_argument('-n', '--nginx_container_name', type=str, help="Name of the nginx container that should be reloaded to load new certs")
args = parser.parse_args()

IS_DEBUG = args.debug or bool(os.getenv('DEBUG'))
CONFIG_PATH = args.config_path or os.getenv('CONFIG_PATH') or '/app/config.yml'
CERT_OUTPUT_PATH = args.cert_output_path or os.getenv('CERT_OUTPUT_PATH') or '/app/certs'
NGINX_CONTAINER_NAME = args.nginx_container_name or os.getenv('NGINX_CONTAINER_NAME') or 'nginx'

if not os.path.exists(CONFIG_PATH): raise FileNotFoundError(f"Config file not found! ({CONFIG_PATH})")
if not os.path.exists(CERT_OUTPUT_PATH): raise FileNotFoundError(f"Output path not found! ({CERT_OUTPUT_PATH})")
if not os.path.isdir(CERT_OUTPUT_PATH): raise FileNotFoundError(f"Output path is not a directory! ({CERT_OUTPUT_PATH})")