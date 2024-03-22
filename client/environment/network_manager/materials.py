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
class Materials:
    def __init__(self, net_manager):
        self.net_manager = net_manager
        self.env = self.net_manager.env
    
    def add_materials_by_files(self, project_id, files, material_type):
        r = self.net_manager.request("/api/materials/add", {"project_id": project_id, "files": files, "type": material_type})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
    
    def get_materials(self, project_id, material_type):
        r = self.net_manager.request("/api/materials/get", {"project_id": project_id, "type": material_type})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        
        return json.loads(r.text)["materials"]