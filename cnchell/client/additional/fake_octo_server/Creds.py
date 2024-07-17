from singleton import singleton

import requests
import hashlib

@singleton
class Creds():
    def __init__(self):
        self.config_manager = None
        self.token = None
        self.host = None
        self.username = None
        self.password = None

    def auth(self):
        self.host = self.config_manager["server"]["host"]
        r = requests.post(self.host + "/api/login", json={"username": self.username, "password": hashlib.md5(self.password.encode()).hexdigest()})
        
        if r.status_code == 200:
            data = r.json()
            if "token" in data:
                self.token = data["token"]
                return 0
        else:
            exit()