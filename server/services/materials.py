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


def add_by_files(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    db.materials.add(int(data["project_id"]), data["files"], int(data["type"]))

    return "Добавлены", 200

def get(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    ret = db.materials.get(int(data["project_id"]), data["type"])

    return str(json.dumps(ret)), 200