import requests
from requests_toolbelt import MultipartEncoder
import hashlib

from singleton import singleton

import exceptions

from environment.config_manager.config_manager import Config
from environment.file_manager.ChunkReader import ChunkReader

import os

import defines
import utils

import json

@singleton
class Configs:
    def __init__(self, net_manager):
        self.net_manager = net_manager
        self.env = self.net_manager.env

    def get_sync_data(self):
        r = self.net_manager.request("/api/configs/get_sync", {})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

        return r.json()["sync_data"]

    def upload_zip(self, src_path, program_name, program_user_alias):
        size = os.path.getsize(src_path)
        cr = ChunkReader(src_path, int(self.env.config_manager["server"]["chunk_size"]))

        filename = src_path.split("\\")[-1]

        encoder = MultipartEncoder(fields={'file': ("data_zip", cr, 'application/octet-stream'), 
            "json": ('payload.json', json.dumps({"token": self.net_manager.token, "size": size, "filename": filename, "program_name": program_name, "program_user_alias": program_user_alias}), "application/json")}
        )
        
        r = requests.post(
            self.net_manager.host + "/api/configs/upload_zip", data=encoder, headers={'Content-Type': encoder.content_type}
        )

        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text, no_message=True)
        
        cr.close_file_handler()

        data = json.loads(r.text)

        self.env.file_manager.delete_file(src_path)
        return data["sync_data"]

    def delete(self, program_name):
        r = self.net_manager.request("/api/configs/delete", {"program_name": program_name})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

    def get_zip(self, program_name):
        cfg = self.env.config_manager
        local_filename = utils.get_unique_id()
        local_filename = os.path.join(cfg["path"]["temp_path"], local_filename) + ".zip"
        url = "/api/configs/get_zip"
        data = {"program_name": program_name, "token": self.net_manager.token}
        with requests.post(self.net_manager.host+url, stream=True, 
            data = data, 
            headers = {'Content-type':'application/json'}) as r:
            r.raise_for_status()
            progress.full = int(r.headers["Content-Length"])
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(defines.CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
        return local_filename