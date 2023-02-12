from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily, REGISTRY
from prometheus_client import start_http_server
from urllib.request import urlopen
import json
import re
import time
import sys
import logging

class CustomCollector(object):

    def __init__(self, url):
        self.url = url

    def collect(self):
        data = json.loads(urlopen(self.url).read())

        # camera stats
        ffmpeg_pid = GaugeMetricFamily('frigate_ffmpeg_pid', 'PID for ffmpeg process', labels=['camera'])
        capture_pid = GaugeMetricFamily('frigate_capture_pid', 'PID for the ffmpeg process that consumes this camera', labels=['camera'])
        detect_pid = GaugeMetricFamily('frigate_detect_pid', 'PID for the process that runs detection for this camera', labels=['camera'])     
        camera_fps = GaugeMetricFamily('frigate_camera_fps', 'Frames per second being consumed from your camera.', labels=['camera'])
        detection_fps = GaugeMetricFamily('frigate_detection_fps', 'Number of times detection is run per second.', labels=['camera'])
        process_fps = GaugeMetricFamily('frigate_process_fps', 'Frames per second being processed by frigate.', labels=['camera'])
        skipped_fps = GaugeMetricFamily('frigate_skipped_fps', 'Frames per second skip for processing by frigate.', labels=['camera'])
        detection_enabled = GaugeMetricFamily('frigate_detection_enabled', 'Detection enabled for camera', labels=['camera'])

        for d in data:
            try:
                ffmpeg_pid.add_metric([d], float(data[d]['ffmpeg_pid']))
                detect_pid.add_metric([d], float(data[d]['pid']))
                capture_pid.add_metric([d], float(data[d]['capture_pid']))
                camera_fps.add_metric([d], (data[d]['camera_fps']))
                detection_fps.add_metric([d], float(data[d]['detection_fps']))
                process_fps.add_metric([d], float(data[d]['process_fps']))
                skipped_fps.add_metric([d], float(data[d]['skipped_fps']))
                detection_enabled.add_metric([d], float(data[d]['detection_enabled']))
            except (AttributeError, TypeError, KeyError):
                pass

        yield ffmpeg_pid
        yield capture_pid
        yield detect_pid
        yield camera_fps
        yield detection_fps
        yield process_fps
        yield skipped_fps
        yield detection_enabled

        # detector stats
        yield GaugeMetricFamily('frigate_detection_total_fps', 'Sum of detection_fps across all cameras and detectors.', value=data['detection_fps'])

        detector_inference_speed = GaugeMetricFamily('frigate_detector_inference_speed_seconds', 'Time spent running object detection in seconds.', labels=['name'])
        detector_pid = GaugeMetricFamily('frigate_detector_pid', 'PID for the shared process that runs object detection on the detector', labels=['name'])
        
        for d in data['detectors']:
            detector_inference_speed.add_metric([d], data['detectors'][d]['inference_speed']/1000.0) # ms to seconds
            detector_pid.add_metric([d], data['detectors'][d]['pid'])

        yield detector_inference_speed
        yield detector_pid

        # process stats
        cpu_usages = GaugeMetricFamily('frigate_cpu_usage_percent', 'Process CPU usage %', labels=['pid'])
        mem_usages = GaugeMetricFamily('frigate_mem_usage_percent', 'Process memory usage %', labels=['pid'])

        data['cpu_usages'].pop('Tasks:')
        for d in data['cpu_usages']:
            cpu_usages.add_metric([d], float(data['cpu_usages'][d]['cpu']))
            mem_usages.add_metric([d], float(data['cpu_usages'][d]['mem']))

        yield cpu_usages
        yield mem_usages

        # gpu stats
        gpu_usages = GaugeMetricFamily('frigate_gpu_usage_percent', 'GPU utilisation %', labels=['gpu'])
        gpu_mem_usages = GaugeMetricFamily('frigate_gpu_mem_usage_percent', 'GPU memory usage %', labels=['gpu'])

        for d in data['gpu_usages']:
            try:
                gpu_usages.add_metric([d], float(re.findall(r'\d+', data['gpu_usages'][d]['gpu'])[0]))
                mem_usages.add_metric([d], float(re.findall(r'\d+', data['gpu_usages'][d]['mem'])[0])) # no value for me
            except IndexError:
                pass
        
        yield gpu_usages
        yield gpu_mem_usages

        # service stats
        yield GaugeMetricFamily('frigate_service_last_updated_timestamp', 'Stats recorded time (unix timestamp)', value=data['service']['last_updated'])
        info = {'latest_version': data['service']['latest_version'], 'version': data['service']['version']}
        yield InfoMetricFamily('frigate_service', 'Frigate version info', value=info)
        yield GaugeMetricFamily('frigate_service_uptime_seconds', 'Uptime seconds', value=data['service']['uptime'])
        # temperatures: no data for me

        storage_free = GaugeMetricFamily('frigate_storage_free_bytes', 'Storage free bytes', labels=['storage'])
        storage_mount_type = InfoMetricFamily('frigate_storage_mount_type', 'Storage mount type', labels=['storage'])
        storage_total = GaugeMetricFamily('frigate_storage_total_bytes', 'Storage total bytes', labels=['storage'])
        storage_used = GaugeMetricFamily('frigate_storage_used_bytes', 'Storage used bytes', labels=['storage'])

        for d in data['service']['storage']:
            storage_free.add_metric([d], data['service']['storage'][d]['free']*1e6) #MB to bytes
            storage_total.add_metric([d], (data['service']['storage'][d]['total']*1e6))
            storage_used.add_metric([d], (data['service']['storage'][d]['used']*1e6))
            storage_mount_type.add_metric([d],  {'mount_type': data['service']['storage'][d]['mount_type']})

        yield storage_free
        yield storage_mount_type
        yield storage_total
        yield storage_used


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    if len(sys.argv) < 1:
        logging.info("Provide Frigate stats url, e.g. http://<your-frigate-ip>:5000/api/stats")

    REGISTRY.register(CustomCollector(sys.argv[1]))
    start_http_server(9100)

    logging.info('Started: ' + sys.argv[1])
    
    while True: time.sleep(1)

    logging.info("Finished")