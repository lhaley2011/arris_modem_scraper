FROM python:3.7.1-alpine

ENV DESTINATION influxdb
ENV SLEEP_INTERVAL 300
ENV MODEM_STATUS_URL http://192.168.100.1/cgi-bin/status
ENV MODEM_PRODUCT_URL http://192.168.100.1/cgi-bin/swinfo
ENV MODEM_MODEL sb6190
ENV INFLUXDB_HOST localhost
ENV INFLUXDB_PORT 8086
ENV INFLUXDB_DATABASE cable_modem_stats
ENV INFLUXDB_USE_SSL False
ENV INFLUXDB_VERIFY_SSL False

ADD src/ /src
COPY requirements.txt /src/requirements.txt
WORKDIR /src

RUN apk add --update --no-cache g++ gcc libxml2-dev libxslt-dev && \
    pip install -r requirements.txt

ENTRYPOINT python3 arris_stats.py
