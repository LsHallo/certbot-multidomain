# Certbot Multi Domain Docker Container

Requests certificates for multiple domains using certbot and letsencrypt.  
Currently only dns-cloudflare plugin is supported to generate certificates.

Subdomains can be specified per domain. Wildcard certificates are also possible.

## Environment Variables

| Variable Name        | Example         | Description                                                           |
|----------------------|-----------------|-----------------------------------------------------------------------|
| CONFIG_PATH          | /app/config.yml | Path to config.yml                                                    |  
| CERT_OUTPUT_PATH     | /app/certs      | Path to cert output                                                   |  
| NGINX_CONTAINER_NAME | nginx           | Name of the nginx container that should be reloaded to load new certs |  
| DEBUG                |                 | Enable debug output and generate only staging certificates            |  

## Example Configuration
config.yml
```yml
domains:
  foo.com:
    subdomains: wildcard # generate cert for *.foo.com and foo.com
    provider: cloudflare # dns plugin to use. only cloudflare supported (for now)
    email: admin@foo.com  # used for cert expiry notifications by letsencrypt
    dns_credentials_file: /app/dns/foo.com.ini # path to mounted file with cloudflare api key

  bar.net:
    subdomains:
      - www
      - demo
      - dev
      - test
    cert_name: bar.net # cert name (optional); defaults to domain name
    provider: cloudflare  # dns plugin to use. only cloudflare supported (for now)
    email: admin@bar.net # used for cert expiry notifications by letsencrypt
    dns_credentials_file: /app/dns/bar.net.ini  # path to mounted file with cloudflare api key
```
`cert_name` defines the path the cert will be available under afterward.  
In combination with the env variable `CONFIG_PATH` the cert path will be as follows:
`${CONFIG_PATH}/live/${CERT_NAME}/fullchain.pem`

`dns_credentials_file` defines the location of the credential file for cloudflare *inside* the container.  
**Example**:  
Mounted `/home/foo/certbot/dns` as `/app/dns` inside the docker container.  
The `dns_credential_file` should then be specified as `/app/dns/foo.com.ini`

## Example docker-compose.yml
```yml
version: '3'

services:
  certbot:
    image: lshallo/certbot-multidomain
    container_name: certbot
    restart: unless-stopped
    volumes:
      - ./config.yml:/app/config.yml
      - ./dns:/app/dns
      - ./certs:/app/certs
      - /var/run/docker.sock:/var/run/docker.sock

  nginx:
    image: linuxserver/nginx
    container_name: nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
```