import requests

from singleton import singleton

from network_manager.server import Server

import hashlib
import json

@singleton
class NetworkManager:
    def __init__(self):
        self.host = "http://127.0.0.1:5000"
        self.username = "telegram_front"
        self.password = "TelegramFrontFlvbybcnhfnjh1337"
        self.token = ""
    
        self.server = Server(self)
        

    def request(self, url, data={}):
        data["token"] = self.token
        try: return requests.post(self.host + url, json = data)
        except: raise exceptions.REQUEST_FAILED

    def set_host(self, host):
        self.host = host

    def login(self):
        r = requests.post(self.host + "/api/login", json={"username": self.username, "password": hashlib.md5(self.password.encode()).hexdigest()})
        
        if r.status_code == 200:
            data = r.json()
            if "token" in data:
                self.token = data["token"]
                return 0