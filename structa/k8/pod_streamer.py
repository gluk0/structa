#!/usr/bin/env python3

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.client.models.v1_pod_log_options import V1PodLogOptions
from kubernetes.client.models.v1_pod_log_options import V1PodLogOptions

import time 
import sys
import os 
import logging 

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
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def stream_pod_logs(self):
        while True:
            
            print("Streaming logs...")
