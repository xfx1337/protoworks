import requests

from singleton import singleton

from environment.network_manager.auth import Auth
from environment.network_manager.projects import Projects
from environment.network_manager.files import Files
from environment.network_manager.audit import Audit
from environment.network_manager.parts import Parts
from environment.network_manager.materials import Materials
from environment.network_manager.hardware import Hardware

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
        self.audit = Audit(self)
        self.parts = Parts(self)
        self.materials = Materials(self)
        self.hardware = Hardware(self)

        self._auto_login = False

    def request(self, url, data={}):
        data["token"] = self.token
        try: return requests.post(self.host + url, json = data)
        except: raise exceptions.REQUEST_FAILED

    def set_host(self, host):
        self.host = host

