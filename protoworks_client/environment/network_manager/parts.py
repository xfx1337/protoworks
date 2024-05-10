import requests
from requests_toolbelt import MultipartEncoder

import json
import os, shutil
import numpy as np
import time

from singleton import singleton

import exceptions

import utils

from environment.config_manager.config_manager import Config

from environment.file_manager.File import File

import defines

@singleton
class Parts:
    def __init__(self, net_manager):
        self.net_manager = net_manager
        self.env = self.net_manager.env
    
    def get_parts(self, project_id):
        r = self.net_manager.request("/api/parts/get_parts", {"project_id": project_id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return json.loads(r.text)["parts"]

    def register_parts(self, project_id, parts):
        r = self.net_manager.request("/api/parts/register_parts", {"project_id": project_id, "parts": parts})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        
        return json.loads(r.text)
    
    def update_parts(self, project_id, parts):
        r = self.net_manager.request("/api/parts/update_parts", {"project_id": project_id, "parts": parts})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

    def delete_parts(self, project_id, parts_ids):
        r = self.net_manager.request("/api/parts/delete_parts", {"project_id": project_id, "parts": parts_ids})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

    def indentify_parts(self, pathes):
        r = self.net_manager.request("/api/parts/indentify_parts", {"pathes": pathes})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        
        return json.loads(r.text)["parts"]

    # def confirm_parts(self, project_id, ids):
    #     r = self.net_manager.request("/api/parts/confirm_parts", {"project_id": project_id, "parts_ids": ids})
    #     if r.status_code != 200:
    #         raise exceptions.REQUEST_FAILED(r.text)