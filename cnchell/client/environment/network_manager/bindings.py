import requests
import hashlib

from singleton import singleton

import exceptions

@singleton
class Bindings:
    def __init__(self, net_manager):
        self.net_manager = net_manager

    def get_event_by_action(self, action):
        r = self.net_manager.request("/api/bindings/get_event_by_action", {"action": action})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

        return r.json()["event"]

    def remove(self, event, action):
        r = self.net_manager.request("/api/bindings/remove", {"event": event, "action": action})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
    
    def add(self, event, action):
        r = self.net_manager.request("/api/bindings/add", {"event": event, "action": action})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)