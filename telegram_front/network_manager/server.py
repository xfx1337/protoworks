import requests
from requests_toolbelt import MultipartEncoder

import hashlib

from singleton import singleton

import exceptions

import json

@singleton
class Server:
    def __init__(self, net_manager):
        self.net_manager = net_manager

    def get_status(self):
        r = self.net_manager.request("/api/status")
        
        if r.status_code == 200:
            data = r.json()
            return data
        else:
            raise exceptions.REQUEST_FAILED(r.text)

    def get_lan_clients(self):
        r = self.net_manager.request("/api/get_lan_clients")
        
        if r.status_code == 200:
            data = r.json()
            return data["clients"]
        else:
            raise exceptions.REQUEST_FAILED(r.text)

    def get_users_list(self):
        r = self.net_manager.request("/api/users/get_users_list")
        
        if r.status_code == 200:
            data = r.json()
            return data["users"]
        else:
            raise exceptions.REQUEST_FAILED(r.text)

    def register_user(self, username, password):
        r = self.net_manager.request("/api/users/register_user", {"username": username, "password": password})
        
        if r.status_code == 200:
            return
        else:
            raise exceptions.REQUEST_FAILED(r.text)

    def remove_user(self, username):
        r = self.net_manager.request("/api/users/remove_user", {"username": username})
        
        if r.status_code == 200:
            return
        else:
            raise exceptions.REQUEST_FAILED(r.text)

    def get_projects(self):
        r = self.net_manager.request("/api/projects/get_projects")
        
        if r.status_code == 200:
            return r.json()["projects"]
            return
        else:
            raise exceptions.REQUEST_FAILED(r.text)

    def get_project_info(self, id):
        r = self.net_manager.request("/api/projects/get_project_info", {"project_id": int(id)})
        
        if r.status_code == 200:
            return r.json()
        else:
            raise exceptions.REQUEST_FAILED(r.text)

    def make_project_done(self, id):
        r = self.net_manager.request("/api/projects/pass", {"id": id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return 0

    def get_project_audit(self, id):
        r = self.net_manager.request("/api/audit/get_project_audit", {"project_id": id, "from_id": 0, "to_id": 10})
        if r.status_code == 200:
            return r.json()["audit"]
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return 0

    def restart(self):
        try:
            r = self.net_manager.request("/api/restart_self")
            if r.status_code == 200:
                return
            if r.status_code != 200:
                return
            return 0
        except:
            pass

    def get_machines_list(self):
        r = self.net_manager.request("/api/machines/list")
        if r.status_code == 200:
            return r.json()["machines"]
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return 0

    def send_action(self, action):
        r = self.net_manager.request("/api/actions/execute", {"action": action})
        if r.status_code == 200:
            return
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return 0

    def paper_print(self, local_path):
        filename = local_path.split("\\")[-1]
        encoder = MultipartEncoder(fields={'file': (filename, open(local_path, "rb"), 'application/octet-stream'), 
            "json": ('payload.json', json.dumps({"token": self.net_manager.token, "filename": filename}), "application/json")}
        )
        
        r = requests.post(
            self.net_manager.host + "/api/hardware/paper_print_from_upload", data=encoder, headers={'Content-Type': encoder.content_type}
        )

        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

    def send_voice(self, local_path, VOICE_PLAYBACK_SERVER):
        filename = local_path.split("\\")[-1]
        encoder = MultipartEncoder(fields={'file': (filename, open(local_path, "rb"), 'application/octet-stream'), 
            "json": ('payload.json', json.dumps({"filename": filename}), "application/json")}
        )
        
        r = requests.post(
            VOICE_PLAYBACK_SERVER + "/api/play_sound", data=encoder, headers={'Content-Type': encoder.content_type}
        )

        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)