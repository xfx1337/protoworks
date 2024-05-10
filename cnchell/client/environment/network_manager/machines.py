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
class Machines:
    def __init__(self, net_manager):
        self.net_manager = net_manager
        self.env = self.net_manager.env
    
    def add_machine(self, name, slave_id, unique_info, plate, delta, gcode_manager, baudrate):
        r = self.net_manager.request("/api/machines/add", {"name": name, "slave_id": slave_id, "unique_info": unique_info, "plate": plate,
        "delta": delta, "gcode_manager": gcode_manager, "baudrate": baudrate})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

        return r.text

    def edit_machine(self, idx, name, unique_info, plate, delta, gcode_manager, baudrate):
        r = self.net_manager.request("/api/machines/edit", {"id": idx, "name": name, "unique_info": unique_info, "plate": plate,
        "delta": delta, "gcode_manager": gcode_manager, "baudrate": baudrate})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

        return r.text
    
    def check_online(self, idx):
        r = self.net_manager.request("/api/machines/check_online", {"id": idx})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

        return r.json()

    def get_machines_list(self, slave_idx=-1):
        r = self.net_manager.request("/api/machines/list", {"slave_id": slave_idx})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

        return r.json()
    
    def restart_handler(self, slave_id, machine_id):
        r = self.net_manager.request("/api/machines/restart_handler", {"slave_id": slave_id, "machine_id": machine_id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
    
    def reconnect(self, slave_id, machine_id):
        r = self.net_manager.request("/api/machines/reconnect", {"slave_id": slave_id, "machine_id": machine_id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

    def send_gcode_command(self, slave_id, machine_id, command):
        r = self.net_manager.request("/api/machines/send_gcode", {"slave_id": slave_id, "machine_id": machine_id, "gcode": command})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

    def upload_gcode_file(self, slave_id, machine_id, file):
        filename = file.split("\\")[-1]
        encoder = MultipartEncoder(fields={'file': (filename, open(file, "rb"), 'application/octet-stream'), 
            "json": ('payload.json', json.dumps({"token": self.net_manager.token, "filename": filename, "slave_id": slave_id, "machine_id": machine_id}), "application/json")}
        )
        
        r = requests.post(
            self.net_manager.host + "/api/machines/upload_gcode", data=encoder, headers={'Content-Type': encoder.content_type}
        )

        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

    def cancel_job(self, slave_id, machine_id):
        r = self.net_manager.request("/api/machines/cancel_job", {"slave_id": slave_id, "machine_id": machine_id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

    def start_job(self, slave_id, machine_id, file):
        r = self.net_manager.request("/api/machines/start_job", {"slave_id": slave_id, "machine_id": machine_id, "file": file})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)