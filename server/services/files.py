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

from file_manager.file_manager import FileManager
file_manager = FileManager()

from file_manager.File import File

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

    data_file = file_manager.unzip_data_archive(os.path.join(config["path"]["temp_path"], obj["filename"]))

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

def delete_logs(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    project_id = int(data["project_id"])

    db.files.remove_logs(project_id)

def delete_files(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    project_id = int(data["project_id"])
    project = db.projects.get_project_info(project_id)

    deleted = []

    for f in data["files"]:
        try:
            path = os.path.join(project["server_path"], f)
            os.remove(path)
            db.files.delete_file(path)
            deleted.append(f)
        except:
            pass
    
    data_file = {"files": deleted}

    data_file["update_id"] = str(utils.get_unique_id())
    event = {
        "event": "DELETE",
        "info": str(json.dumps(data_file)),
        "project_id": int(project_id)
    }
    update_info = db.audit.register_event(event)
    update_info["update_id"] = data_file["update_id"]

    file_manager.delete_empty_folders(project["server_path"])
    try:
        os.mkdir(project["server_path"])
    except:
        pass
    return str(json.dumps(update_info)), 200

def mkdir(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    try: os.mkdir(data["path"])
    except: return "Не удалось", 400
    return "Создана", 200

def get_all_files_that_ever_created_in_project(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    return str(json.dumps(db.files_logging.get(int(data["project_id"])))), 200

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

def files_list_for_project(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    project_id = data["project_id"]

    project_info = db.projects.get_project_info(int(project_id))
    files = file_manager.get_files_list(project_info["server_path"])
    rework_date_modified(files)
    files_dict = file_manager.files_list_to_dict_list(files)
    return json.dumps({"files": files_dict}), 200

def rework_date_modified(files_list):
    check_list_for_db = []
    for f in files_list:
        if f.f_type == FILE:
            check_list_for_db.append(f.path)

    ret = db.files.get_modification_time_for_list(check_list_for_db)
    for f in files_list:
        if f.path in ret:
            f.date_modified = ret[f.path]

def get_zipped_path(request):
    data =  parse_qs(unquote(request.data))
    src_path = data["path"][0]
    ret = db.users.valid_token(data["token"][0])
    if not ret:
        return "Токен не валиден", 403

    files_list = file_manager.get_files_list(src_path)

    rework_date_modified(files_list)

    path = file_manager.make_data_zip(files_list, relative=src_path)

    size = utils.get_file_size(path)

    response = Response(
        stream_with_context(utils._read_file_chunks(path)),
        headers={
            'Content-Disposition': f'attachment; filename={path.split("/")[-1] + ".zip"}',
            'Content-Length': size
        }
    )

    @response.call_on_close
    def on_close():
        utils.delete_file(path)

    return response

def get_zipped_files(request):
    data =  parse_qs(unquote(request.data))
    ret = db.users.valid_token(data["token"][0])
    if not ret:
        return "Токен не валиден", 403

    files_list_data = data["files"]
    relative_path = data["path"][0]
    files_list = []
    for f in files_list_data:
        files_list.append(File(f))

    check_list_for_db = []
    for f in files_list:
        check_list_for_db.append(f.path)

    ret = db.files.get_modification_time_for_list(files_list_data)
    for f in files_list:
        if f.path in ret:
            f.date_modified = ret[f.path]

    path = file_manager.make_data_zip(files_list, relative=relative_path)

    size = utils.get_file_size(path)

    response = Response(
        stream_with_context(utils._read_file_chunks(path)),
        headers={
            'Content-Disposition': f'attachment; filename={path.split("/")[-1] + ".zip"}',
            'Content-Length': size
        }
    )

    @response.call_on_close
    def on_close():
        utils.delete_file(path)

    return response