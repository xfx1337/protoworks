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
class Hardware:
    def __init__(self, net_manager):
        self.net_manager = net_manager
        self.env = self.net_manager.env
    
    def paper_print(self, path):
        r = self.net_manager.request("/api/hardware/paper_print", {"path": path})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)