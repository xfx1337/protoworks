import os, shutil, sys, subprocess
import locale
import win32api, win32print
import tempfile
import requests

import dateutil.parser

from flask import Flask, Response, request
from flask import stream_with_context

import utils

import json

from ping3 import ping, verbose_ping
import socket

from database.database import Database
db = Database()

from config import Config
config = Config("config.ini")

from common import *

def add_slave(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    ip = data["ip"]
    hostname = data["hostname"]
    s_type = data["type"]
    hostname, ip = utils.get_hostname_ip(hostname, ip)
    #d["ping"] = utils.get_ping(ip)

    db.slaves.add(hostname, ip, s_type)
    return "Успешно", 200

def get_slaves_list(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    if "type" in data:
        type_s = int(data["type"])
    else:
        type_s = -1
    
    ret = db.slaves.get_slaves_list(type_s)

    for i in range(len(ret)):
        ret[i]["ping"] = -2
        #ret[i]["ping"] = utils.get_ping(ret[i]["ip"])

    return json.dumps({"slaves": ret}), 200

def edit(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    ip = data["ip"]
    hostname = data["hostname"]
    idx = data["id"]

    db.slaves.edit(idx, ip, hostname)
    return "Успешно", 200