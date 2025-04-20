#!/usr/bin/env python3

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.client.models.v1_pod_log_options import V1PodLogOptions

import time 
import sys
import os 
import argparse

from structa.utils.logging import get_logger

class PodStreamer:
    def __init__(self, namespace: str, pod_name: str):
        self.namespace = namespace
        self.pod_name = pod_name
        self.core_v1_api = client.CoreV1Api()
        self.log_options = V1PodLogOptions(
            follow=True,
            tail_lines=100,
            since_seconds=1000
        )
        self.logger = get_logger(__name__)

    def stream_pod_logs(self):
        while True:
            try:
                self.logger.info(f"Starting to stream logs for pod {self.pod_name} in namespace {self.namespace}")
                logs = self.core_v1_api.read_namespaced_pod_log(
                    name=self.pod_name,
                    namespace=self.namespace,
                    _preload_content=False,
                    **self.log_options.to_dict()
                )
                
                for line in logs:
                    if line:
                        print(line.decode('utf-8'), end='')
                        sys.stdout.flush()
                        
            except ApiException as e:
                self.logger.error(f"Error streaming logs: {e}")
                if e.status == 404:
                    self.logger.warning(f"Pod {self.pod_name} not found in namespace {self.namespace}")
                    return
                
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                
            self.logger.info("Connection lost, retrying in 5 seconds...")
            time.sleep(5)


def main():
    """
    Main entry point for running the pod_streamer as a standalone script.
    
    Usage:
        python -m structa.k8.pod_streamer --namespace default --pod my-pod
    """
    parser = argparse.ArgumentParser(description="Stream logs from a Kubernetes pod")
    parser.add_argument("--namespace", "-n", required=True, help="Kubernetes namespace")
    parser.add_argument("--pod", "-p", required=True, help="Kubernetes pod name")
    
    args = parser.parse_args()
    
    # Load kube config
    try:
        config.load_kube_config()
    except Exception:
        # If running in-cluster
        config.load_incluster_config()
        
    logger = get_logger(__name__)
    logger.info(f"Starting pod streamer for pod {args.pod} in namespace {args.namespace}")
    
    streamer = PodStreamer(args.namespace, args.pod)
    streamer.stream_pod_logs()


if __name__ == "__main__":
    main()

