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

import time

from file_manager.file_manager import FileManager
file_manager = FileManager()

from file_manager.File import File

def get_sync(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    ret = db.programs_configs.get_configs_sync_data()

    return json.dumps({"sync_data": ret}), 200


def upload_zip(request):
    data = request.files['json']
    obj = json.loads(data.read())

    ret = db.users.valid_token(obj["token"])
    if not ret:
        return "Токен не валиден", 403
    
    program_name = obj["program_name"]
    program_user_alias = obj["program_user_alias"]

    filename = request.files['file'].filename
    path = os.path.join(config["path"]["configs_path"], program_name + ".zip")

    f = request.files['file']
    try:
        os.remove(path)
    except:
        pass
    f.save(path)


    t = int(time.time())
    update_id = utils.get_unique_id()
    db.programs_configs.set_program_data(program_name, program_user_alias, t, update_id)

    return json.dumps({"sync_data": {"update_id": update_id, "time": t}}), 200

def get_zip(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    breakpoint()
    program_name = data["program_name"]

    path = os.path.join(config_manager["path"]["configs_path"], program_name + ".zip")

    response = Response(
        stream_with_context(utils._read_file_chunks(path)),
        headers={
            'Content-Disposition': f'attachment; filename={program_name + ".zip"}',
            'Content-Length': size
        }
    )

    @response.call_on_close
    def on_close():
        utils.delete_file(path)

    return response

def delete(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    program_name = data["program_name"]
    db.programs_configs.delete(program_name)

    return "Успешно", 200