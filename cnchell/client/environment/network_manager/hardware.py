import requests
from requests_toolbelt import MultipartEncoder

import json
import os, shutil
import numpy as np
import time

from singleton import singleton

import exceptions

import utils

from environment.config_manager.config_manager import Config

from environment.file_manager.File import File

import defines

@singleton
class Hardware:
    def __init__(self, net_manager):
        self.net_manager = net_manager
        self.env = self.net_manager.env
    
    def paper_print(self, path):
        r = self.net_manager.request("/api/hardware/paper_print", {"path": path})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
    
    def paper_print_from_file(self, local_path):
        filename = local_path.split("\\")[-1]
        encoder = MultipartEncoder(fields={'file': (filename, open(local_path, "rb"), 'application/octet-stream'), 
            "json": ('payload.json', json.dumps({"token": self.net_manager.token, "filename": filename}), "application/json")}
        )
        
        r = requests.post(
            self.net_manager.host + "/api/hardware/paper_print_from_upload", data=encoder, headers={'Content-Type': encoder.content_type}
        )

        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
    
    def paper_print_text(self, text):
        r = self.net_manager.request("/api/hardware/paper_print_text", {"text": text})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
    
    def paper_print_get_jobs(self):
        r = self.net_manager.request("/api/hardware/paper_print_get_jobs", {})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return json.loads(r.text)["jobs"]
    
    def cancel_paper_printing(self, jobId):
        r = self.net_manager.request("/api/hardware/cancel_paper_printing", {"JobId": jobId})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

    def get_hub_info(self):
        r = self.net_manager.request("/api/hardware/get_hub_info")
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return json.loads(r.text)
    
    def ping(self, host, is_hostname=False):
        r = self.net_manager.request("/api/hardware/ping", {"host": host, "is_hostname": is_hostname})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return json.loads(r.text)["ping"]
    
    def send_get_request(self, host, is_hostname=False):
        r = self.net_manager.request("/api/hardware/send_get_request", {"host": host, "is_hostname": is_hostname})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return r.text
    
    def set_hub(self, hostname, ip):
        r = self.net_manager.request("/api/hardware/set_hub_info", {"hostname": hostname, "ip": ip})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        
    def restart_hub(self):
        r = self.net_manager.request("/api/hardware/restart_hub")
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
    
    def restart_all(self):
        r = self.net_manager.request("/api/hardware/restart_all")
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)