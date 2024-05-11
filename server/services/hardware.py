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


def paper_print(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    path = data["path"]
    enc = locale.getpreferredencoding()
    path_e = path.encode('utf-8')

    currentprinter = win32print.GetDefaultPrinter()
    #win32api.ShellExecute(0, 'open', GSPRINT_PATH, '-ghostscript "'+GHOSTSCRIPT_PATH+'" -printer "'+currentprinter+f'" "{path}"', '.', 0)
    #win32api.ShellExecute(0, 'open', GSPRINT_PATH, '-ghostscript "'+GHOSTSCRIPT_PATH+'" -printer "'+currentprinter+f'" "{path_e}"', '.', 0)
    #win32api.ShellExecute(0, "print", path, None,  ".",  0)

    command = 'sw_requirements\\PDFtoPrinter.exe "' + path + '"' 
    subprocess.call(command, shell=True) 
    return "Отправлены на печать", 200

def paper_print_from_upload(request):
    data = request.files['json']
    obj = json.loads(data.read())

    ret = db.users.valid_token(obj["token"])
    if not ret:
        return "Токен не валиден", 403

    path = os.path.join(config["path"]["temp_path"], obj["filename"])

    f = request.files['file']
    f.save(path)

    command = 'sw_requirements\\PDFtoPrinter.exe "' + path + '"' 
    subprocess.run(command)
    file_manager.delete_file(path)

    return "Отправлены на печать", 200 

def paper_print_text(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    text = data["text"]
    filename = tempfile.mktemp (".txt")
    open (filename, "w", encoding="utf-8").write(text)
    ret = win32api.ShellExecute (
    0,
    "printto",
    filename,
    '"%s"' % win32print.GetDefaultPrinter (),
    ".",
    0
    )

    return "Отправлено на печать", 200

def paper_print_get_jobs(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    jobs = []

    phandle = win32print.OpenPrinter(win32print.GetDefaultPrinter())

    print_jobs = win32print.EnumJobs(phandle, 0, -1, 1)
    if print_jobs:
        jobs.extend(list(print_jobs))

    for i in range(len(jobs)):
        jobs[i]["Submitted"] = jobs[i]["Submitted"].now().timestamp()

    return json.dumps({"jobs": jobs}), 200

def cancel_paper_printing(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    job_id = data["JobId"]
    phandle = win32print.OpenPrinter(win32print.GetDefaultPrinter())

    try:
        win32print.SetJob(phandle, job_id, 0, None, win32print.JOB_CONTROL_DELETE)
    except:
        pass

    return "Отменено", 200

def restart_hub(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    d = db.hub.get_hub_info()
    ip = d["ip"]
    r = requests.get(ip + "/api/restart")
    return "Отправлено", 200

def get_hub_info(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    d = db.hub.get_hub_info()
    d["info"] = "NO DATA"
    ip = d["ip"]
    hostname = d["hostname"]
    
    hostname, ip = utils.get_hostname_ip(hostname, ip)
    db.hub.set_hub_info(hostname, ip)

    d["ping"] = utils.get_ping(ip)
    try:
        d["status"] = db.monitoring.get_device("MAIN_HUB")["status"]
    except:
        d["status"] = "N/A"

    try:
        r = requests.get(ip, timeout=3)
        d["info"] = r.text
    except:
        pass

    return json.dumps(d), 200

def set_hub_info(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    hostname = ""
    ip = ""

    hostname = data["hostname"]
    ip = data["ip"]
    
    if hostname == "":
        try:
            hostname = socket.gethostbyaddr(ip)
        except:
            pass
    if ip == "":
        try:
            ip = socket.gethostbyname(hostname)[0]
        except:
            pass

    db.hub.set_hub_info(hostname, ip)
    return "Успешно", 200

def check_ping(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    host = data["host"]
    is_hostname = data["is_hostname"]

    try:
        if is_hostname:
            host = socket.gethostbyname(host)
        delay = utils.get_ping(host)
    except:
        delay = -1

    return json.dumps({"ping": delay}), 200

def send_get_request(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    host = data["host"]
    is_hostname = data["is_hostname"]

    try:
        if is_hostname:
            host = socket.gethostbyname(host)
        r = requests.get(host, timeout=5)
        text = r.text
    except:
        text = "NO DATA"

    return text, 200

def send_hub_command(link, data={}, method='POST'):
    hub = db.hub.get_hub_info()
    if hub == None:
        pass
    else:
        try:
            if method == "POST":
                requests.post(hub["ip"] + link, json = data)
            else:
                requests.get(hub["ip"] + link)
        except: pass

def hub_setup_all_machines():
    machines = db.machines.get_machines_list(-1)
    slaves = {}
    for m in machines:
        if m["slave_id"] not in slaves:
            slaves[m["slave_id"]] = []
        m["unique_info"] = json.loads(m["unique_info"].replace("'", '"'))
        slaves[m["slave_id"]].append(m)
    
    send = []
    for s in slaves.keys():
        send.append({"ip": db.slaves.get_slave(s)["ip"], "machines": slaves[s]})
    
    send_hub_command("/api/machines/setup_all", {"data": send})
