from singleton import singleton

import requests
from requests_toolbelt import MultipartEncoder

from common import *

from config import Config
config = Config("config.ini")

from database.database import Database
db = Database()

import json

import utils
import os
import shutil

import services.machines

from FakeFlaskRequest import FakeFlaskRequest

@singleton
class ActionManager:
    def __init__(self):
        pass
    
    def execute(self, action):
        print(f"executing {json.dumps(action)}")
        if action["action"] == "CANCEL_JOB":
            for d in action["devices"]:
                services.machines.cancel_job(FakeFlaskRequest({"machine_id": int(d.replace("MACHINE", "")), "token": db.users.get_token("BYPASS")}))
        
        if action["action"] == "NEXT_JOB":
            for d in action["devices"]:
                services.machines.cancel_job(FakeFlaskRequest({"machine_id": int(d.replace("MACHINE", "")), "token": db.users.get_token("BYPASS")}))
                #db.work_queue.delete_jobs([0], int(d.replace("MACHINE", "")))
                try:
                    jobs = db.work_queue.get_jobs(int(d.replace("MACHINE", "")))

                    if len(jobs) < 1:
                        return
                    
                    if jobs[0]["status"] == "В работе":
                        db.work_queue.delete_jobs([0], int(d.replace("MACHINE", "")))
                        jobs = db.work_queue.get_jobs(int(d.replace("MACHINE", "")))

                    if len(jobs) < 1:
                        return
                    
                    job = jobs[0]

                    path = os.path.join(config["path"]["machines_path"], "WorkingDirectory")
                    shutil.copy(os.path.join(path, job["unique_info"]["job_send_filename"]), os.path.join(path, job["unique_info"]["job_filename"]))
                    
                    send_path = os.path.join(path, job["unique_info"]["job_filename"])

                    idx = int(d.replace("MACHINE", ""))

                    machine = db.machines.get_machine(int(idx))
                    slave = db.slaves.get_slave(machine["slave_id"])
                    

                    encoder = MultipartEncoder(fields={'file': (job["unique_info"]["job_filename"], open(send_path, "rb"), 'application/octet-stream'), 
                        "json": ('payload.json', json.dumps({"filename": job["unique_info"]["job_filename"], "unique_info":json.loads(machine["unique_info"].replace("'", '"')), "id": machine["id"]}), "application/json")}
                    )
                    
                    r = requests.post(
                        slave["ip"] + "/api/machines/upload_gcode", data=encoder, headers={'Content-Type': encoder.content_type}
                    )

                    services.machines.start_job(FakeFlaskRequest({"machine_id": idx, "file": job["unique_info"]["job_filename"], "token": db.users.get_token("BYPASS")}))
                    job["status"] = "В работе"
                    job["work_start"] = utils.time_now()
                    db.work_queue.overwrite_job(job["id"], job)

                except Exception as e:
                    print(e)