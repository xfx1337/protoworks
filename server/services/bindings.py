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

def add(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    event = data["event"]
    action = data["action"]

    db.bindings.add_bind(event, action)
    
    return "Добавлено", 200

def remove(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    event = data["event"]
    action = data["action"]

    db.bindings.remove_bind(event, action)
    
    return "Удалено", 200

def get_event_by_action(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    action = data["action"]

    ret = db.bindings.get_event_by_action(action)
    return json.dumps({"event": ret}), 200