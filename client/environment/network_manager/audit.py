import requests
import hashlib

from singleton import singleton

import exceptions

@singleton
class Audit:
    def __init__(self, net_manager):
        self.net_manager = net_manager

    def get_projects_sync_data(self):
        r = self.net_manager.request("/api/audit/get_projects_sync_data", {})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

        return r.json()["projects"]
    
    def get_project_audit(self, project_id, from_id, to_id):
        r = self.net_manager.request("/api/audit/get_project_audit", {"project_id": project_id, "from_id": from_id, "to_id": to_id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

        return r.json()["audit"]