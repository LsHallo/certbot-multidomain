# Certbot Multi Domain Docker Container
![](https://github.com/LsHallo/certbot-multidomain/actions/workflows/docker-image.yml/badge.svg)

Requests certificates for multiple domains using certbot and letsencrypt.  
Currently only dns-cloudflare plugin is supported to generate certificates.

Subdomains can be specified per domain. Wildcard certificates are also possible.  
Will create separate certificates for each domain. No pollution of the alternative name in your certs.  

## Environment Variables

| Variable Name        | Example         | Description                                                           |
|----------------------|-----------------|-----------------------------------------------------------------------|
| CONFIG_PATH          | /app/config.yml | Path to config.yml                                                    |  
| CERT_OUTPUT_PATH     | /app/certs      | Path to cert output                                                   |  
| NGINX_CONTAINER_NAME | nginx           | Name of the nginx container that should be reloaded to load new certs |  
| DEBUG                |                 | Enable debug output and generate only staging certificates            |  

## Example Configuration
Example config.yml can be found [here](config.example.yml)  
`cert_name` defines the path the cert will be available under afterward.  
In combination with the env variable `CONFIG_PATH` the cert path will be as follows:
`${CONFIG_PATH}/live/${CERT_NAME}/fullchain.pem`

`dns_credentials_file` defines the location of the credential file for cloudflare *inside* the container.  
**Example**:  
Mounted `/home/foo/certbot/dns` as `/app/dns` inside the docker container.  
The `dns_credential_file` should then be specified as `/app/dns/foo.com.ini`

## Example docker-compose.yml
Example docker-compose.yml can be found [here](docker-compose.example.yml)  