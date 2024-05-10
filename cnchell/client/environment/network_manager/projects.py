import hashlib

from singleton import singleton

import exceptions

@singleton
class Projects:
    def __init__(self, net_manager):
        self.net_manager = net_manager

    def get_projects(self):
        r = self.net_manager.request("/api/projects/get_projects")
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

        return r.json()

    def get_project_info(self, project_id):
        r = self.net_manager.request("/api/projects/get_project_info", {"project_id": project_id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

        return r.json()

    def create(self, name, customer, description, deadline):
        r = self.net_manager.request("/api/projects/create", {"name": name, "customer": customer, "description": description, 
            "deadline": deadline})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return int(r.text)
    
    def delete(self, id):
        r = self.net_manager.request("/api/projects/delete", {"id": id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return 0
    
    def pass_(self, id):
        r = self.net_manager.request("/api/projects/pass", {"id": id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return 0