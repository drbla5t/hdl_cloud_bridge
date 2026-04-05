ARG BUILD_FROM=ghcr.io/hassio-addons/base-python:3.11-alpine3.19
FROM ${BUILD_FROM}

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app
COPY run.sh /app/run.sh

RUN sed -i 's/\r$//' /app/run.sh && chmod +x /app/run.sh