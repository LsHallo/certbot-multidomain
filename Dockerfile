FROM python:3.11-slim

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

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY src/* /app

ENTRYPOINT ["python3", "-u"]
CMD ["/app/certbot.py"]

