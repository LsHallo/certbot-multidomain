# Certbot Multi Domain Docker Container
![](https://github.com/LsHallo/certbot-multidomain/actions/workflows/docker-image.yml/badge.svg) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

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

## Known Issues
The container will log the following message when renewing a cert:
```
dns_cloudflare.py:108: PendingDeprecationWarning:
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!   WARNING  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!! You're seeing this warning because you've upgraded the Python package 'cloudflare' to version  !!
!! 2.20.* via an automated upgrade without version pinning. Version 2.20.0 exists to catch any    !!
!! of these upgrades before Cloudflare releases a new major release under the release number 3.x. !!
!!                                                                                                !!
!! Should you determine that you need to revert this upgrade and pin to v2.19.* it is recommended !!
!! you do the following: pip install --upgrade cloudflare==2.19.* or equivilant.                  !!
!!                                                                                                !!
!! Or you can upgrade to v3.x. NOTE: Release 3.x will not be code-compatible or call-compatible   !!
!! with previous releases. To see more about upgrading to next major version, please see:         !!
!! https://github.com/cloudflare/python-cloudflare/discussions/191                                !!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```
This is expected and just a warning about an upcoming version change of cloudflare python package.  
This will be resolved with debian sid (14) in the future.