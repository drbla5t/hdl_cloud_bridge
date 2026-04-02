FROM ghcr.io/home-assistant/amd64-base:latest

RUN apk add --no-cache python3 py3-pip
WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY app /app/app
COPY run.sh /run.sh
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]