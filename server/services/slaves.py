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

import services.monitoring
import services.hardware

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

    conf = services.monitoring.get_monitoring_configuration()
    services.hardware.send_hub_command("/api/set_monitoring_configuration", {"conf": conf})

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
        try: 
            d = db.monitoring.get_device("SLAVE" + str(ret[i]["id"]))
            ret[i]["status"] = d["status"]
            ret[i]["ping"] = d["info"]["ping"]
        except:
            ret[i]["status"] = "N/A"
            ret[i]["ping"] = "N/A"
        

    return json.dumps({"slaves": ret}), 200

def get_slave(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    idx = data["id"]
    slave = db.slaves.get_slave(idx)
    try: 
        d = db.monitoring.get_device("SLAVE" + str(slave["id"]))
        slave["status"] = d["status"]
        slave["ping"] = d["info"]["ping"]
    except:
        slave["status"] = "N/A"
        slave["ping"] = "N/A"
    return json.dumps({"slave": slave}), 200

def edit(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    ip = data["ip"]
    hostname = data["hostname"]
    idx = data["id"]

    db.slaves.edit(idx, ip, hostname)

    conf = services.monitoring.get_monitoring_configuration()
    services.hardware.send_hub_command("/api/set_monitoring_configuration", {"conf": conf})

    return "Успешно", 200

def restart(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    idx = data["id"]
    slave = db.slaves.get_slave(idx)
    r = requests.get(slave['ip'] + "/api/restart")
    return "Запрос отправлен", 200


def send_request(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    idx = data["id"]
    link = data["link"]
    data_sent = {}
    if "data" in data:
        data_sent = data["data"]
    method = data['method']

    slave = db.slaves.get_slave(idx)

    if method == 'POST':
        r = requests.post(slave["ip"] + link, json=data_sent)
    elif method == 'GET':
        r = requests.get(slave['ip'] + link)
    else:
        return "Method not implemented", 405
    
    return r.text, 200

def _send_request(slave_id, link, method, data={}, ret_text=False):
    slave = db.slaves.get_slave(slave_id)

    if method == 'POST':
        r = requests.post(slave["ip"] + link, json=data)
    elif method == 'GET':
        r = requests.get(slave['ip'] + link)
    else:
        return "Method not implemented", 405
    if ret_text:
        return r.text
    return r.json()
