import requests

from singleton import singleton

from environment.network_manager.auth import Auth
from environment.network_manager.projects import Projects
from environment.network_manager.files import Files

import exceptions

@singleton
class NetworkManager:
    def __init__(self, env):
        self.host = ""
        self.username = ""
        self.password = ""
        self.token = ""
    
        self.env = env

        self.auth = Auth(self)
        self.projects = Projects(self)
        self.files = Files(self)

        self._auto_login = False

    def request(self, url, data={}):
        data["token"] = self.token
        try: return requests.post(self.host + url, json = data)
        except: raise exceptions.REQUEST_FAILED

    def set_host(self, host):
        self.host = host

