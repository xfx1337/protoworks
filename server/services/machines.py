import os, shutil, sys, subprocess
import locale
import win32api, win32print
import tempfile
import requests
from requests_toolbelt import MultipartEncoder

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

import services.slaves
import services.monitoring
import services.hardware

def add_machine(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    name = data["name"]
    slave_id = data["slave_id"] 
    unique_info = data["unique_info"]
    plate = data["plate"]
    delta = data["delta"]
    baudrate = data["baudrate"]
    gcode_manager = data["gcode_manager"]

    db.machines.add_machine(name, slave_id, unique_info, plate, delta, gcode_manager, baudrate)

    conf = services.monitoring.get_monitoring_configuration()
    services.hardware.send_hub_command("/api/set_monitoring_configuration", {"conf": conf})

    return "Добавлено", 200

def edit_machine(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    name = data["name"]
    idx = data["idx"]
    unique_info = data["unique_info"]
    plate = data["plate"]
    delta = data["delta"]
    baudrate = data["baudrate"]
    gcode_manager = data["gcode_manager"]

    db.machines.edit_machine(idx, name, unique_info, plate, delta, gcode_manager, baudrate)

    conf = services.monitoring.get_monitoring_configuration()
    services.hardware.send_hub_command("/api/set_monitoring_configuration", {"conf": conf})

    return "Изменено", 200

def list_machines(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    if "slave_id" in data:
        slave_idx = int(data["slave_id"])
    else:
        slave_idx = -1
    
    ret = db.machines.get_machines_list(slave_idx)

    for m in ret:
        m["status"] = "N/A"
        m["work_status"] = "N/A"
        m["last_seen"] = 0
        m["info"] = {}
        try:
            d = db.monitoring.get_device("MACHINE" + str(m["id"]))
            m["status"] = d["status"]
            m["work_status"] = d["info"]["work_status"]
            m["info"] = d["info"]
            m["last_seen"] = d["date"]
        except:
            pass

    return json.dumps({"machines": ret}), 200

def get_machine(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    idx = data["id"]
    machine = db.machines.get_machine(int(idx))
    if machine == None:
        return "Not found", 404
    machine["status"] = "N/A"
    machine["work_status"] = "N/A"
    machine["info"] = {}
    machine["last_seen"] = 0
    try:
        d = db.monitoring.get_device("MACHINE" + str(machine["id"]))
        machine["status"] = d["status"]
        machine["work_status"] = d["info"]["work_status"]
        machine["info"] = d["info"]
        machine["last_seen"] = d["date"]
    except:
        pass
    return json.dumps({"machine": machine}), 200

def get_host(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    idx = data["id"]
    machine = db.machines.get_machine(idx)
    slave = db.slaves.get_slave(machine["slave_id"])
    
    ret = services.slaves._send_request(slave["id"], "/api/machines/get_host", "POST", {"id": idx})
    return ret, 200

def restart_handler(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    idx = data["machine_id"]

    machine = db.machines.get_machine(int(idx))
    slave = db.slaves.get_slave(machine["slave_id"])
    
    r = requests.post(slave["ip"] + "/api/machines/restart_handler", json = {"unique_info":json.loads(machine["unique_info"].replace("'", '"')), "id": machine["id"]})
    return r.text, 200

def reconnect(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    idx = data["machine_id"]

    machine = db.machines.get_machine(int(idx))
    slave = db.slaves.get_slave(machine["slave_id"])
    r = requests.post(slave["ip"] + "/api/machines/reconnect", json = {"unique_info":json.loads(machine["unique_info"].replace("'", '"')), 
    "id": machine["id"], "baudrate": machine["baudrate"]})
    return r.text, 200

def send_request(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    idx = data["machine_id"]
    link = data["link"]
    method = data["method"]

    machine = db.machines.get_machine(int(idx))
    slave = db.slaves.get_slave(machine["slave_id"])
    
    data_sent = {}
    if "data" in data:
        data_sent = data["data"]
    method = data['method']

    if method == 'POST':
        r = requests.post(slave["ip"] + f"{5001+int(idx)}" + link, json=data_sent)
    elif method == 'GET':
        r = requests.get(slave['ip'] + f"{5001+int(idx)}" + link)
    else:
        return "Method not implemented", 405
    
    return r.text, 200

def send_gcode(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    idx = data["machine_id"]
    gcode = data["gcode"]

    
    if idx != -1:
        machine = db.machines.get_machine(int(idx))
        slave = db.slaves.get_slave(machine["slave_id"])
        r = requests.post(slave["ip"] + "/api/machines/send_gcode", json = {"unique_info":json.loads(machine["unique_info"].replace("'", '"')), "id": machine["id"], "command": gcode})
    else:
        slave = db.slaves.get_slave(data["slave_id"])
        device = data["device"]
        r = requests.post(slave["ip"] + "/api/machines/send_gcode", json = {"unique_info":"", "id": -1, "command": gcode, "device": device})

    return "Успешно", 200

def check_online(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    idx = data["id"]
    machine = db.machines.get_machine(int(idx))
    slave = db.slaves.get_slave(machine["slave_id"])
    try:
        r = requests.post(slave["ip"] + "/api/machines/check_online", 
        json={"unique_info":json.loads(machine["unique_info"].replace("'", '"')), "id": machine["id"]})
    except:
        return "Нет соединения", 200

    return r.text, 200

def cancel_job(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    idx = data["machine_id"]
    if "pause" in data:
        pause = data["pause"]
    else:
        pause = False

    jobs = db.work_queue.get_jobs(int(idx))
    if jobs[0]["status"] == "В работе":
        jobs[0]["status"] = "Отменена"
        db.work_queue.overwrite_job(jobs[0]["id"], jobs[0])

    machine = db.machines.get_machine(int(idx))
    slave = db.slaves.get_slave(machine["slave_id"])
    r = requests.post(slave["ip"] + "/api/machines/cancel_job", json = {"unique_info":json.loads(machine["unique_info"].replace("'", '"')), "id": machine["id"], "pause": pause})

    return r.text, 200

def upload_gcode(request):
    data = request.files['json']
    obj = json.loads(data.read())

    ret = db.users.valid_token(obj["token"])
    if not ret:
        return "Токен не валиден", 403

    filename = obj["filename"]

    path = os.path.join(config["path"]["temp_path"], obj["filename"])

    f = request.files['file']
    f.save(path)

    idx = obj["machine_id"]

    machine = db.machines.get_machine(int(idx))
    slave = db.slaves.get_slave(machine["slave_id"])
    

    encoder = MultipartEncoder(fields={'file': (filename, open(path, "rb"), 'application/octet-stream'), 
        "json": ('payload.json', json.dumps({"filename": filename, "unique_info":json.loads(machine["unique_info"].replace("'", '"')), "id": machine["id"]}), "application/json")}
    )
    
    r = requests.post(
        slave["ip"] + "/api/machines/upload_gcode", data=encoder, headers={'Content-Type': encoder.content_type}
    )

    try:
        os.remove(path)
    except: pass

    return r.text, 200

def start_job(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    idx = data["machine_id"]
    file = data["file"]

    machine = db.machines.get_machine(int(idx))
    slave = db.slaves.get_slave(machine["slave_id"])
    
    r = requests.post(slave["ip"] + "/api/machines/start_job", json = {"unique_info":json.loads(machine["unique_info"].replace("'", '"')), "id": machine["id"], "file": file})

    return r.text, 200

def delete(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    idx = data["machine_id"]
    db.machines.delete(idx)
    return "Успешно", 200