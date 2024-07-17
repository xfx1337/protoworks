import os, time

import json

from defines import *
import requests

import subprocess

class Server:
    def __init__(self):
        self.id = -1
        pass

    def run(self):
        pass
    
    def stop(self):
        pass
    
    def status(self):
        pass
    
    def set_id(self, id):
        self.id = id

class FakeOctoServer(Server):
    def __init__(self, port, username, password, machine_id, config_path):
        super().__init__()
        self.port = port
        self.username = username
        self.password = password
        self.machine_id = machine_id
        self.config_path = config_path
        self.host = "http://127.0.0.1"

    def run(self):
        subprocess.Popen(f'fake_octo_server.exe {self.port} {self.machine_id} "{self.config_path}" {self.username} {self.password}')
    
    def stop(self):
        requests.get(self.host + ":" + str(self.port) + "/api/shutdown_server")
    
    def status(self):
        return "runnning"