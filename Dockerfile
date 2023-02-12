FROM alpine
RUN apk update && apk add py3-prometheus-client
COPY prometheus_frigate_exporter.py /var/python_scripts/prometheus_frigate_exporter.py
CMD  /usr/bin/python3 /var/python_scripts/prometheus_frigate_exporter.py $FRIGATE_STATS_URL

# docker build -t prometheus_frigate_exporter .