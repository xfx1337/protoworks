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
        self.net_manager.request("/api/parts/get_parts", {"project_id": project_id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return json.loads(r.text)["parts"]
