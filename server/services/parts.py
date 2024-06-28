import os, shutil, sys, subprocess

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

def get_parts(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    project_id = int(data["project_id"])

    return json.dumps({"parts": db.parts.get_parts(project_id)}), 200

def register_parts(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    project_id = int(data["project_id"])
    parts = data["parts"]

    st_idx = db.parts.register_parts(project_id, parts)

    return json.dumps({"start_idx": st_idx}), 200

def update_parts(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    project_id = int(data["project_id"])
    parts = data["parts"]

    db.parts.register_update(project_id, parts)

    data_file = {"parts": parts}

    data_file["update_id"] = str(utils.get_unique_id())
    event = {
        "event": "PARTS_UPDATE",
        "info": str(json.dumps(data_file)),
        "project_id": project_id
    }
    update_info = db.audit.register_event(event)
    update_info["update_id"] = data_file["update_id"]

    return "Успешно", 200

def delete_parts(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    project_id = int(data["project_id"])
    parts = data["parts"]

    db.parts.delete_parts(project_id, parts)

    data_file = {"parts": parts}

    data_file["update_id"] = str(utils.get_unique_id())
    event = {
        "event": "PARTS_DELETE",
        "info": str(json.dumps(data_file)),
        "project_id": project_id
    }
    update_info = db.audit.register_event(event)
    update_info["update_id"] = data_file["update_id"]

    return "Успешно", 200

def indentify_parts(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    pathes = data["pathes"]

    projects = db.projects.get_projects()["projects"]
    projects_dc = {}
    for p in projects:
        projects_dc[p["name"]] = p

    parts = []
    for f in pathes:
        project_name = f.split("\\")[0]
        if project_name in projects_dc:
            project = projects_dc[project_name]
            if "_PW" in f:
                id = int(f.split("_PW")[-1].split(".")[0])
                part = db.parts.get_part(project["id"], id)
                if part != None:
                    parts.append(part)
            else:
                part = db.parts.search_by_origin_path(project["id"], os.path.join(config["path"]["projects_path"], f))
                parts.append(part)
    
    return json.dumps({"parts": parts}), 200

def get_part_info(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    part_id = data["part_id"]
    project_id = data["project_id"]

    part = db.parts.get_part(project_id, part_id)
    return json.dumps({"part": part}), 200