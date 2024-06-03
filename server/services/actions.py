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

from action_manager.action_manager import ActionManager
action_manager = ActionManager()

from common import *

def execute(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    action = data["action"]

    action_manager.execute(action)

    return "Отправлено на выполнение", 200
