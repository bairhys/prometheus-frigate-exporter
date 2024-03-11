# Prometheus Frigate stats exporter 

This is a docker container that runs a Prometheus exporter for [Frigate](https://frigate.video/) stats.

Tested with 0.12.0 and 0.13.2 Frigate docker images.

Exports from Frigate API:

- Inference Speed
- CPU and MEM process stats
- Camera, detection and skipped FPS 
- Camera audio stats
- Storage total, used and free
- Device Temperature (Coral temp)
- Event counters for detected labels on each camera

[Docker Hub](https://hub.docker.com/r/rhysbailey/prometheus-frigate-exporter)

[GitHub](https://github.com/bairhys/prometheus-frigate-exporter)

[Grafana Dashboard](https://grafana.com/grafana/dashboards/18226-frigate/)

![Grafana](https://raw.githubusercontent.com/bairhys/prometheus-frigate-exporter/main/grafana-screenshot.png)

## Run the exporter

Modify the `FRIGATE_STATS_URL` environment variable below to point to your [Frigate API stats](https://docs.frigate.video/integrations/api#get-apistats) (replace `<your-frigate-ip>` with your Frigate docker container IP address). Then run the container:

```bash
docker run \
    -d \
    --restart unless-stopped \
    -p 9100:9100 \
    -e "FRIGATE_STATS_URL=http://<your-frigate-ip>:5000/api/stats" \
    --name prometheus_frigate_exporter \
    rhysbailey/prometheus-frigate-exporter
```

The default internal exporter port can be modified with `-e "PORT=9100"`

Metrics are available at http://localhost:9100/metrics

If you want to export network bandwidth stats, include the section below in your Frigate config (see [here](https://docs.frigate.video/configuration/reference)): 

```yml
telemetry:
  stats:
    network_bandwidth: True
```

### Setup Prometheus

If you don't already have Prometheus set up to scrape the `prometheus-frigate-exporter` metrics,

- create Prometheus config file `prometheus.yml`
- copy example below into `prometheus.yml`, replacing `<your-prometheus-frigate-exporter-ip>` with the IP address of your `prometheus_frigate_exporter` docker container. `<your-prometheus-frigate-exporter-ip>` is likely the same IP address as your Frigate docker containers `<your-frigate-ip>` if running in the same docker instance 
  ```yaml
  # my global config
  global:
    scrape_interval: 15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
    evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
    # scrape_timeout is set to the global default (10s).
   
  # A scrape configuration containing exactly one endpoint to scrape:
  # Here it's Prometheus itself.
  scrape_configs:
    # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
    - job_name: "prometheus"
      static_configs:
        - targets: ["localhost:9090"]
  
    - job_name: "prometheus_frigate_exporter"
      static_configs:
        - targets: [
                      "<your-prometheus-frigate-exporter-ip>:9100"
                   ]
  ```

- Run Prometheus docker container by replacing `/path/to/prometheus.yml` to point to the `prometheus.yml` just created

  ```bash
  docker run \
      -d \
      --restart unless-stopped \
      -p 9090:9090 \
      -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
      prom/prometheus
  ```

To see if Prometheus is scraping the Frigate exporter, go to Prometheus targets page [http://your-prometheus-ip:9090/targets](http://your-prometheus-ip:9090/targets) and look for `UP` for `prometheus_frigate_exporter` job.

### Setup Grafana

If you don't already have Grafana set up, 

- run Grafana

    ```bash
    docker run \
        -d \
        --restart unless-stopped \
        -p 3000:3000 \
        grafana/grafana-oss
    ```

- Go to Grafana [http://your-grafana-ip:3000](http://your-grafana-ip:3000) (might take a few minutes first run). Use admin:admin to log in
- Go to [http://your-grafana-ip:3000/datasources](http://your-grafana-ip:3000/datasources)
  - add Prometheus datasource
  - Set Prometheus URL `http://<your-prometheus-frigate-exporter-ip>:9090`
  - Click `Save and Test` to check if connected
- Go to [http://your-grafana-ip:3000/dashboards](http://your-grafana-ip:3000/dashboards)
  - New -> Import
  - Enter in `Import via grafana.com`: `18226` (id can be found at [Grafana Dashboard](https://grafana.com/grafana/dashboards/18226-frigate/)) and click Load
  - Set the datasource as Prometheus instance set up before then click Import
- Should now be able to see Frigate time series metrics in the Grafana dashboard

## Example metrics

Metrics at `<your-prometheus-frigate-exporter-ip>:9100` should look similar to this

```python
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 225.0
python_gc_objects_collected_total{generation="1"} 156.0
python_gc_objects_collected_total{generation="2"} 0.0
# HELP python_gc_objects_uncollectable_total Uncollectable object found during GC
# TYPE python_gc_objects_uncollectable_total counter
python_gc_objects_uncollectable_total{generation="0"} 0.0
python_gc_objects_uncollectable_total{generation="1"} 0.0
python_gc_objects_uncollectable_total{generation="2"} 0.0
# HELP python_gc_collections_total Number of times this generation was collected
# TYPE python_gc_collections_total counter
python_gc_collections_total{generation="0"} 42.0
python_gc_collections_total{generation="1"} 3.0
python_gc_collections_total{generation="2"} 0.0
# HELP python_info Python platform information
# TYPE python_info gauge
python_info{implementation="CPython",major="3",minor="10",patchlevel="10",version="3.10.10"} 1.0
# HELP process_virtual_memory_bytes Virtual memory size in bytes.
# TYPE process_virtual_memory_bytes gauge
process_virtual_memory_bytes 2.6222592e+07
# HELP process_resident_memory_bytes Resident memory size in bytes.
# TYPE process_resident_memory_bytes gauge
process_resident_memory_bytes 1.9456e+07
# HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
# TYPE process_start_time_seconds gauge
process_start_time_seconds 1.67807825501e+09
# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
# TYPE process_cpu_seconds_total counter
process_cpu_seconds_total 0.19
# HELP process_open_fds Number of open file descriptors.
# TYPE process_open_fds gauge
process_open_fds 6.0
# HELP process_max_fds Maximum number of open file descriptors.
# TYPE process_max_fds gauge
process_max_fds 1.048576e+06
# HELP frigate_camera_fps Frames per second being consumed from your camera.
# TYPE frigate_camera_fps gauge
frigate_camera_fps{camera_name="Camera1"} 25.0
frigate_camera_fps{camera_name="Camera2"} 5.0
frigate_camera_fps{camera_name="Camera3"} 5.0
frigate_camera_fps{camera_name="Camera4"} 5.0
# HELP frigate_detection_fps Number of times detection is run per second.
# TYPE frigate_detection_fps gauge
frigate_detection_fps{camera_name="Camera1"} 4.0
frigate_detection_fps{camera_name="Camera2"} 5.0
frigate_detection_fps{camera_name="Camera3"} 0.0
frigate_detection_fps{camera_name="Camera4"} 0.0
# HELP frigate_process_fps Frames per second being processed by frigate.
# TYPE frigate_process_fps gauge
frigate_process_fps{camera_name="Camera1"} 25.0
frigate_process_fps{camera_name="Camera2"} 5.0
frigate_process_fps{camera_name="Camera3"} 5.0
frigate_process_fps{camera_name="Camera4"} 5.0
# HELP frigate_skipped_fps Frames per second skip for processing by frigate.
# TYPE frigate_skipped_fps gauge
frigate_skipped_fps{camera_name="Camera1"} 0.0
frigate_skipped_fps{camera_name="Camera2"} 0.0
frigate_skipped_fps{camera_name="Camera3"} 0.0
frigate_skipped_fps{camera_name="Camera4"} 0.0
# HELP frigate_detection_enabled Detection enabled for camera
# TYPE frigate_detection_enabled gauge
frigate_detection_enabled{camera_name="Camera1"} 1.0
frigate_detection_enabled{camera_name="Camera2"} 1.0
frigate_detection_enabled{camera_name="Camera3"} 1.0
frigate_detection_enabled{camera_name="Camera4"} 1.0
# HELP frigate_detection_total_fps Sum of detection_fps across all cameras and detectors.
# TYPE frigate_detection_total_fps gauge
frigate_detection_total_fps 10.5
# HELP frigate_detector_inference_speed_seconds Time spent running object detection in seconds.
# TYPE frigate_detector_inference_speed_seconds gauge
frigate_detector_inference_speed_seconds{name="ov"} 0.011
# HELP frigate_detection_start Detector start time (unix timestamp)
# TYPE frigate_detection_start gauge
frigate_detection_start{name="ov"} 0.0
# HELP frigate_cpu_usage_percent Process CPU usage %
# TYPE frigate_cpu_usage_percent gauge
frigate_cpu_usage_percent{name="Camera1",pid="296",process="ffmpeg",type="Camera"} 24.3
frigate_cpu_usage_percent{name="Camera1",pid="289",process="capture",type="Camera"} 29.7
frigate_cpu_usage_percent{name="Camera1",pid="285",process="detect",type="Camera"} 29.7
frigate_cpu_usage_percent{name="Camera2",pid="556",process="ffmpeg",type="Camera"} 6.0
frigate_cpu_usage_percent{name="Camera2",pid="292",process="capture",type="Camera"} 5.7
frigate_cpu_usage_percent{name="Camera2",pid="286",process="detect",type="Camera"} 10.3
frigate_cpu_usage_percent{name="Camera3",pid="309",process="ffmpeg",type="Camera"} 1.7
frigate_cpu_usage_percent{name="Camera3",pid="295",process="capture",type="Camera"} 0.3
frigate_cpu_usage_percent{name="Camera3",pid="287",process="detect",type="Camera"} 1.0
frigate_cpu_usage_percent{name="Camera4",pid="310",process="ffmpeg",type="Camera"} 6.7
frigate_cpu_usage_percent{name="Camera4",pid="299",process="capture",type="Camera"} 1.0
frigate_cpu_usage_percent{name="Camera4",pid="288",process="detect",type="Camera"} 0.7
frigate_cpu_usage_percent{name="ov",pid="280",process="detect",type="Detector"} 30.0
frigate_cpu_usage_percent{pid="1"} 0.0
frigate_cpu_usage_percent{pid="100"} 0.0
frigate_cpu_usage_percent{pid="105"} 11.0
frigate_cpu_usage_percent{pid="111"} 0.0
frigate_cpu_usage_percent{pid="128"} 0.0
frigate_cpu_usage_percent{pid="129"} 0.0
frigate_cpu_usage_percent{pid="130"} 0.0
frigate_cpu_usage_percent{pid="131"} 0.0
frigate_cpu_usage_percent{pid="15"} 0.0
frigate_cpu_usage_percent{pid="17"} 0.0
frigate_cpu_usage_percent{pid="24"} 0.0
frigate_cpu_usage_percent{pid="25"} 0.0
frigate_cpu_usage_percent{pid="26"} 0.0
frigate_cpu_usage_percent{pid="27"} 0.0
frigate_cpu_usage_percent{pid="273"} 0.0
frigate_cpu_usage_percent{pid="279"} 1.0
frigate_cpu_usage_percent{pid="28"} 0.0
frigate_cpu_usage_percent{pid="282"} 4.0
frigate_cpu_usage_percent{pid="29"} 0.0
frigate_cpu_usage_percent{pid="293"} 0.0
frigate_cpu_usage_percent{pid="30"} 0.0
frigate_cpu_usage_percent{pid="300"} 0.0
frigate_cpu_usage_percent{pid="308"} 0.0
frigate_cpu_usage_percent{pid="31"} 0.0
frigate_cpu_usage_percent{pid="313"} 0.0
frigate_cpu_usage_percent{pid="314"} 0.0
frigate_cpu_usage_percent{pid="322030"} 0.0
frigate_cpu_usage_percent{pid="322038"} 0.0
frigate_cpu_usage_percent{pid="40"} 0.0
frigate_cpu_usage_percent{pid="41"} 0.0
frigate_cpu_usage_percent{pid="78"} 0.0
frigate_cpu_usage_percent{pid="80"} 0.0
frigate_cpu_usage_percent{pid="81"} 0.0
# HELP frigate_mem_usage_percent Process memory usage %
# TYPE frigate_mem_usage_percent gauge
frigate_mem_usage_percent{name="Camera1",pid="296",process="ffmpeg",type="Camera"} 1.1
frigate_mem_usage_percent{name="Camera1",pid="289",process="capture",type="Camera"} 0.6
frigate_mem_usage_percent{name="Camera1",pid="285",process="detect",type="Camera"} 1.2
frigate_mem_usage_percent{name="Camera2",pid="556",process="ffmpeg",type="Camera"} 0.7
frigate_mem_usage_percent{name="Camera2",pid="292",process="capture",type="Camera"} 0.8
frigate_mem_usage_percent{name="Camera2",pid="286",process="detect",type="Camera"} 1.2
frigate_mem_usage_percent{name="Camera3",pid="309",process="ffmpeg",type="Camera"} 0.2
frigate_mem_usage_percent{name="Camera3",pid="295",process="capture",type="Camera"} 0.5
frigate_mem_usage_percent{name="Camera3",pid="287",process="detect",type="Camera"} 0.6
frigate_mem_usage_percent{name="Camera4",pid="310",process="ffmpeg",type="Camera"} 0.1
frigate_mem_usage_percent{name="Camera4",pid="299",process="capture",type="Camera"} 0.5
frigate_mem_usage_percent{name="Camera4",pid="288",process="detect",type="Camera"} 0.6
frigate_mem_usage_percent{name="ov",pid="280",process="detect",type="Detector"} 1.9
frigate_mem_usage_percent{pid="1"} 0.0
frigate_mem_usage_percent{pid="100"} 0.0
frigate_mem_usage_percent{pid="105"} 5.0
frigate_mem_usage_percent{pid="111"} 0.0
frigate_mem_usage_percent{pid="128"} 0.0
frigate_mem_usage_percent{pid="129"} 0.0
frigate_mem_usage_percent{pid="130"} 0.0
frigate_mem_usage_percent{pid="131"} 0.0
frigate_mem_usage_percent{pid="15"} 0.0
frigate_mem_usage_percent{pid="17"} 0.0
frigate_mem_usage_percent{pid="24"} 0.0
frigate_mem_usage_percent{pid="25"} 0.0
frigate_mem_usage_percent{pid="26"} 0.0
frigate_mem_usage_percent{pid="27"} 0.0
frigate_mem_usage_percent{pid="273"} 0.0
frigate_mem_usage_percent{pid="279"} 0.0
frigate_mem_usage_percent{pid="28"} 0.0
frigate_mem_usage_percent{pid="282"} 0.0
frigate_mem_usage_percent{pid="29"} 0.0
frigate_mem_usage_percent{pid="293"} 0.0
frigate_mem_usage_percent{pid="30"} 0.0
frigate_mem_usage_percent{pid="300"} 0.0
frigate_mem_usage_percent{pid="308"} 0.0
frigate_mem_usage_percent{pid="31"} 0.0
frigate_mem_usage_percent{pid="313"} 0.0
frigate_mem_usage_percent{pid="314"} 0.0
frigate_mem_usage_percent{pid="322030"} 0.0
frigate_mem_usage_percent{pid="322038"} 0.0
frigate_mem_usage_percent{pid="40"} 0.0
frigate_mem_usage_percent{pid="41"} 0.0
frigate_mem_usage_percent{pid="78"} 0.0
frigate_mem_usage_percent{pid="80"} 0.0
frigate_mem_usage_percent{pid="81"} 0.0
frigate_mem_usage_percent{pid="Tasks:"} 0.0
# HELP frigate_gpu_usage_percent GPU utilisation %
# TYPE frigate_gpu_usage_percent gauge
frigate_gpu_usage_percent{gpu_name="intel-qsv"} 13.0
# HELP frigate_gpu_mem_usage_percent GPU memory usage %
# TYPE frigate_gpu_mem_usage_percent gauge
# HELP frigate_service_info Frigate version info
# TYPE frigate_service_info gauge
frigate_service_info{latest_version="0.11.1",version="0.12.0-27a31e7"} 1.0
# HELP frigate_service_uptime_seconds Uptime seconds
# TYPE frigate_service_uptime_seconds gauge
frigate_service_uptime_seconds 227029.0
# HELP frigate_service_last_updated_timestamp Stats recorded time (unix timestamp)
# TYPE frigate_service_last_updated_timestamp gauge
frigate_service_last_updated_timestamp 1.678078264e+09
# HELP frigate_storage_free_bytes Storage free bytes
# TYPE frigate_storage_free_bytes gauge
frigate_storage_free_bytes{storage="/dev/shm"} 2e+09
frigate_storage_free_bytes{storage="/media/frigate/clips"} 2e+09
frigate_storage_free_bytes{storage="/media/frigate/recordings"} 2e+09
frigate_storage_free_bytes{storage="/tmp/cache"} 2e+09
# HELP frigate_storage_mount_type_info Storage mount type
# TYPE frigate_storage_mount_type_info gauge
frigate_storage_mount_type_info{mount_type="tmpfs",storage="/"} 1.0
frigate_storage_mount_type_info{mount_type="ext4",storage="/"} 1.0
frigate_storage_mount_type_info{mount_type="ext4",storage="/"} 1.0
frigate_storage_mount_type_info{mount_type="overlay",storage="/"} 1.0
# HELP frigate_storage_total_bytes Storage total bytes
# TYPE frigate_storage_total_bytes gauge
frigate_storage_total_bytes{storage="/dev/shm"} 3e+09
frigate_storage_total_bytes{storage="/media/frigate/clips"} 3e+09
frigate_storage_total_bytes{storage="/media/frigate/recordings"} 3e+09
frigate_storage_total_bytes{storage="/tmp/cache"} 3e+09
# HELP frigate_storage_used_bytes Storage used bytes
# TYPE frigate_storage_used_bytes gauge
frigate_storage_used_bytes{storage="/dev/shm"} 1e+09
frigate_storage_used_bytes{storage="/media/frigate/clips"} 1e+09
frigate_storage_used_bytes{storage="/media/frigate/recordings"} 1e+09
frigate_storage_used_bytes{storage="/tmp/cache"} 1e+09
```
