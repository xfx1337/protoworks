import requests
import hashlib

from singleton import singleton

import exceptions

@singleton
class Auth:
    def __init__(self, net_manager):
        self.net_manager = net_manager

    def login(self, username, password):
        self.host = self.net_manager.host
        self.net_manager.username = username
        self.net_manager.password = password
        r = requests.post(self.host + "/api/login", json={"username": username, "password": hashlib.md5(password.encode()).hexdigest()})
        
        if r.status_code == 200:
            data = r.json()
            if "token" in data:
                self.net_manager.token = data["token"]
                return 0
        else:
            raise exceptions.REQUEST_FAILED(r.text)

        