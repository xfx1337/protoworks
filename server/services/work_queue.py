import os, shutil, sys, subprocess
import requests

from flask import Flask, Response, request
from flask import stream_with_context

import utils

import json

from database.database import Database
db = Database()

from config import Config
config = Config("config.ini")

from common import *

import services.monitoring
import services.hardware

def get_job_order(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    idx = -1
    if "id" in data:
        idx = int(data["id"])
    ret = db.work_queue.get(idx)
    return "", 200

def add_jobs(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    return "", 200

def get_jobs(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    return "", 200

def delete_jobs(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    return "", 200