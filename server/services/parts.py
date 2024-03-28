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