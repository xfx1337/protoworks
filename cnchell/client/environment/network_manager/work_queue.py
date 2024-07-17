import requests
from requests_toolbelt import MultipartEncoder

import json
import os, shutil
import time

from singleton import singleton

import exceptions

import utils

from environment.config_manager.config_manager import Config

from environment.file_manager.File import File
from environment.file_manager.ChunkReader import ChunkReader

import defines

@singleton
class WorkQueue:
    def __init__(self, net_manager):
        self.net_manager = net_manager
        self.env = self.net_manager.env

    def get_queue(self, machine_id):
        r = self.net_manager.request("/api/work_queue/get_jobs", {"id": machine_id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        return json.loads(r.text)["queue"]
    
    def add_jobs(self, jobs, files):
        files_real = []
        files_delete = []
        if len(files) != 0:
            for f in files:
                to = os.path.join(self.env.config_manager["path"]["temp_path"], list(f.keys())[0])
                shutil.copyfile(f[list(f.keys())[0]], to)
                files_real.append(File(to, f_type=defines.FILE))
                files_delete.append(to)
                src_path = self.env.file_manager.make_data_zip(files_real)
        else:
            src_path = "additional\\data_zip_bypass.zip"
        size = os.path.getsize(src_path)
        cr = ChunkReader(src_path, int(self.env.config_manager["server"]["chunk_size"]))

        filename = src_path.split("\\")[-1]


        encoder = MultipartEncoder(fields={'file': ("data_zip", cr, 'application/octet-stream'), 
            "json": ('payload.json', json.dumps({"jobs": jobs, "token": self.net_manager.token, "size": size, "filename": filename}), "application/json")}
        )
        
        
        r = requests.post(
            self.net_manager.host + "/api/work_queue/add_jobs", data=encoder, headers={'Content-Type': encoder.content_type}
        )

        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text, no_message=True)
        
        cr.close_file_handler()
        for f in files_delete:
            os.remove(f)
        if src_path != "additional\\data_zip_bypass.zip":
            self.env.file_manager.delete_file(src_path)
        return r.text
    
    def delete_jobs(self, indexes, machine_id):
        r = self.net_manager.request("/api/work_queue/delete_jobs", {"indexes": indexes, "machine_id": machine_id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

    def get_job_by_id(self, idx):
        r = self.net_manager.request("/api/work_queue/get_job_by_id", {"id": idx})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        
        return json.loads(r.text)["job"]

    def move_job(self, fr, to, machine_id):
        r = self.net_manager.request("/api/work_queue/move_job", {"from": fr, "to": to, "machine_id": machine_id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
    
    def overwrite_job(self, idx, job):
        r = self.net_manager.request("/api/work_queue/overwrite_job", {"job": json.dumps(job), "id": idx})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

    def overwrite_job_files(self, idx, job, files):
        files_real = []
        files_delete = []
        for f in files:
            to = os.path.join(self.env.config_manager["path"]["temp_path"], list(f.keys())[0])
            shutil.copyfile(f[list(f.keys())[0]], to)
            files_real.append(File(to, f_type=defines.FILE))
            files_delete.append(to)
        src_path = self.env.file_manager.make_data_zip(files_real)
        size = os.path.getsize(src_path)
        cr = ChunkReader(src_path, int(self.env.config_manager["server"]["chunk_size"]))

        filename = src_path.split("\\")[-1]

        encoder = MultipartEncoder(fields={'file': ("data_zip", cr, 'application/octet-stream'), 
            "json": ('payload.json', json.dumps({"id": idx, "job": json.dumps(job), "token": self.net_manager.token, "size": size, "filename": filename}), "application/json")}
        )
        
        r = requests.post(
            self.net_manager.host + "/api/work_queue/overwrite_job_files", data=encoder, headers={'Content-Type': encoder.content_type}
        )

        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text, no_message=True)
        
        cr.close_file_handler()
        for f in files_delete:
            os.remove(f)

        self.env.file_manager.delete_file(src_path)
        return r.text
    
    def find_jobs_by_parts(self, jobs_to_search, ignore_machine_equal=False):
        r = self.net_manager.request("/api/work_queue/find_jobs_by_parts", {"parts": jobs_to_search, "ignore_machine_equal": ignore_machine_equal})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        
        return json.loads(r.text)["jobs_equals"]
    
    def find_jobs_by_files(self, jobs_to_search, ignore_machine_equal=False):
        r = self.net_manager.request("/api/work_queue/find_jobs_by_files", {"files": jobs_to_search, "ignore_machine_equal": ignore_machine_equal})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        
        return json.loads(r.text)["jobs_equals"]