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

    if obj["filename"] != "data_zip_bypass.zip":
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

def get_job_by_id(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    idx = data["id"]
    ret = db.work_queue.get_job_by_id(idx)

    return json.dumps({"job": ret}), 200

def move_job(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    machine_id = data["machine_id"]
    fr = data["from"]
    to = data["to"]
    db.work_queue.move_job(fr, to, machine_id)

    return "Изменено", 200

def overwrite_job(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    job = data["job"]
    idx = data["id"]
    db.work_queue.overwrite_job(idx, json.loads(job))

    return "Изменено", 200

def overwrite_job_files(request):
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

    job = obj["job"]
    idx = obj["id"]
    db.work_queue.overwrite_job(idx, json.loads(job))

    return "Добавлены", 200

def find_jobs_by_parts(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    parts = data["parts"]
    ignore_machine_id = data["ignore_machine_equal"]
    ret = db.work_queue.find_jobs_by_parts(parts, ignore_machine_id)
    return json.dumps({"jobs_equals": ret}), 200

def find_jobs_by_files(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    parts = data["files"]
    ignore_machine_id = data["ignore_machine_equal"]
    ret = db.work_queue.find_jobs_by_files(parts, ignore_machine_id)
    return json.dumps({"jobs_equals": ret}), 200