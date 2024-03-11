import os, shutil

from flask import Flask, Response, request
from flask import stream_with_context

import utils

import json

from urllib.parse import unquote
from urllib.parse import urlparse
from urllib.parse import parse_qs

from database.database import Database
db = Database()

from config import Config
config = Config("config.ini")

from common import *

from zipfile import ZipFile 

def create_dirs(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    path = data["path"]

    for d in data["dirs"]:
        if d[0] == "\\":
            d = d[1:]
        try: os.mkdir(os.path.join(path, d))
        except: pass

    return "Папки подготовлены", 200

def upload_data_zip(request):
    data = request.files['json']
    obj = json.loads(data.read())

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

    data_file = utils.unzip_data_archive(os.path.join(config["path"]["temp_path"], obj["filename"]))

    utils.delete_file(os.path.join(config["path"]["temp_path"], obj["filename"]))

    for i in range(len(data_file["files"])):
        data_file["files"][i]["path"] = os.path.join(data_file["project"]["server_path"], data_file["files"][i]["path"])
        data_file["files"][i]["project_id"] = data_file["project"]["id"]

    db.files.register_update(data_file["files"])
    data_file["update_id"] = str(utils.get_unique_id())
    event = {
        "event": "UPLOAD",
        "info": str(json.dumps(data_file)),
        "project_id": int(data_file["project"]["id"])
    }
    update_info = db.audit.register_event(event)
    update_info["update_id"] = data_file["update_id"]
    return str(json.dumps(update_info)), 200

def delete_path(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    if os.path.isdir(data["path"]):
        try: shutil.rmtree(data["path"], ignore_errors=False, onerror=None)
        except: return "Не удалось", 400
    else:
        return "Папки не существует", 200

    return "Удален", 200

def mkdir(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    try: os.mkdir(data["path"])
    except: return "Не удалось", 400
    return "Создана", 200

def dir_tree(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    dirs = utils.scan_for_subdirs(data["path"])

    for i in range(len(dirs)):
        dirs[i] = dirs[i][(len(data["path"])):]
    
    return {"dirs": dirs}, 200
        
def files_list(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    src_path = data["path"]

    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(src_path) for f in filenames]

    size_sum = 0

    files_to_send = []

    for i in range(len(files)):
        size =  os.path.getsize(files[i])
        size_sum += size
        files_to_send.append({"filename": files[i][len(src_path):], "size": size, "modification_time": os.path.getmtime(files[i])})

    return {"files": files_to_send, "size": size_sum}, 200

def get_zipped_path(request):
    data =  parse_qs(unquote(request.data))
    src_path = data["path"][0]
    ret = db.users.valid_token(data["token"][0])
    if not ret:
        return "Токен не валиден", 403

    name = utils.get_unique_id()

    file_path = os.path.join(config["path"]["temp_path"], name) + ".zip"

    utils.zip(src_path, dest_path=file_path)

    size = utils.get_file_size(file_path)

    response = Response(
        stream_with_context(utils._read_file_chunks(file_path)),
        headers={
            'Content-Disposition': f'attachment; filename={name + ".zip"}',
            'Content-Length': size
        }
    )

    @response.call_on_close
    def on_close():
        utils.delete_file(file_path)

    return response

def get_zipped_files(request):
    data =  parse_qs(unquote(request.data))
    files = data["files"]
    path = data["path"][0]
    ret = db.users.valid_token(data["token"][0])
    if not ret:
        return "Токен не валиден", 403
    
    name = utils.get_unique_id()

    file_path = os.path.join(config["path"]["temp_path"], name) + ".zip"

    utils.zip_files(files, src_path=path, dest_path=file_path)

    size = utils.get_file_size(file_path)

    response = Response(
        stream_with_context(utils._read_file_chunks(file_path)),
        headers={
            'Content-Disposition': f'attachment; filename={name + ".zip"}',
            'Content-Length': size
        }
    )

    @response.call_on_close
    def on_close():
        utils.delete_file(file_path)

    return response