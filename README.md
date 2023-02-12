# Prometheus Frigate stats exporter 

This is a docker container that runs a Prometheus exporter for [Frigate](https://frigate.video/) stats.

Tested with ghcr.io/blakeblackshear/frigate:0.12.0-beta6 docker image with a single Intel OpenVINO detector.

[Docker Hub](https://hub.docker.com/r/rhysbailey/prometheus-frigate-exporter)

[GitHub](https://github.com/bairhys/prometheus-frigate-exporter)

![Grafana](https://raw.githubusercontent.com/bairhys/prometheus-frigate-exporter/main/grafana-screenshot.png)

## Run the exporter

Modify the `FRIGATE_STATS_URL` environment variable below to point to your [Frigate API stats](https://docs.frigate.video/integrations/api#get-apistats). Then run the container:

```bash
docker run -d -p 9100:9100 -e "FRIGATE_STATS_URL=http://<your-frigate-ip>:5000/api/stats" --name prometheus_frigate_exporter rhysbailey/prometheus-frigate-exporter
```

Metrics are available at http://localhost:9100/metrics