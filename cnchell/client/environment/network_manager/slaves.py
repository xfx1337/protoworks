import requests
from requests_toolbelt import MultipartEncoder

import json
import os, shutil
import time

from singleton import singleton

import exceptions

import utils

from environment.config_manager.config_manager import Config

import defines

@singleton
class Slaves:
    def __init__(self, net_manager):
        self.net_manager = net_manager
        self.env = self.net_manager.env
    
    def add_slave(self, ip, hostname, s_type):
        r = self.net_manager.request("/api/slaves/add", {"ip": ip, "hostname": hostname, "type": s_type})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

        return r.text
    
    def get_slaves_list(self, type_s=-1):
        r = self.net_manager.request("/api/slaves/list", {"type": type_s})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        
        return r.json()

    def get_slave(self, idx):
        r = self.net_manager.request("/api/slaves/get", {"id": idx})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        
        return r.json()

    def edit_slave(self, idx, ip, hostname):
        r = self.net_manager.request("/api/slaves/edit", {"id": idx, "ip": ip, "hostname": hostname})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        
    def restart(self, idx):
        r = self.net_manager.request("/api/slaves/restart", {"id": idx})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
    
    def get_devices(self, idx):
        r = self.net_manager.request("/api/slaves/send_request", {"id": idx, "link": "/api/machines/get_available_machines", "method": "GET"})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return r.json()
    
    def get_unique_info(self, idx, device):
        r = self.net_manager.request("/api/slaves/send_request", {"id": idx, "link": "/api/machines/get_unique_info", "method": "POST", "data": {"port": device}})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return r.json()