FROM python:3.15-slim

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y \
    certbot \
    python3-certbot-dns-cloudflare \
    curl \
    && apt-get clean

RUN curl https://get.docker.com | sh \
    && apt-get clean

ARG PIP_NO_CACHE_DIR=1
ARG PIP_DISABLE_PIP_VERSION_CHECK=1
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY src/ /app

ENTRYPOINT ["python3", "-u"]
CMD ["/app/certbot.py"]
