import os, shutil, sys, subprocess
import requests

from flask import Flask, Response, request
from flask import stream_with_context

import utils

import json
from urllib.parse import unquote

from database.database import Database
db = Database()

from config import Config
config = Config("config.ini")

from common import *

from file_manager.file_manager import FileManager
file_manager = FileManager()

from file_manager.File import File

def get_jobs(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    idx = int(data["id"])
    ret = db.work_queue.get_jobs(idx)

    return json.dumps({"queue": ret}), 200

def add_jobs(request):
    data = request.files['json']
    obj = json.loads(unquote(data.read()))

    ret = db.users.valid_token(obj["token"])
    if not ret:
        return "Токен не валиден", 403

    bytes_left = obj["size"]

    with open(os.path.join(config["path"]["temp_path"], obj["filename"]), 'wb') as upload:
        chunk_size = int(config["networking"]["chunk_size"])
        while bytes_left > 0:
            chunk = request.files['file'].stream.read(chunk_size)
            upload.write(chunk)
            bytes_left -= len(chunk)

    machines_work_dir = os.path.join(config["path"]["machines_path"], "WorkingDirectory")
    data_file = file_manager.unzip_data_archive(os.path.join(config["path"]["temp_path"], obj["filename"]), direct_folder=machines_work_dir)

    utils.delete_file(os.path.join(config["path"]["temp_path"], obj["filename"]))

    jobs = obj["jobs"]
    for job in jobs:
        if "index" in job:
            db.work_queue.insert_job(job, job["index"])
        else:
            db.work_queue.insert_job(job)

    return "Добавлены", 200

def delete_jobs(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    indexes = data["indexes"]
    machine_id = data["machine_id"]
    db.work_queue.delete_jobs(indexes, machine_id)

    return "", 200