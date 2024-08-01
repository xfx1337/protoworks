import hashlib
import json

import signal
import os
import sys
import zipfile

from database.database import Database
db = Database()

import uuid
import time
import psutil
from datetime import datetime as dt

from config import Config
config = Config("config.ini")

from common import *

import socket
from contextlib import closing

import ping3
from ping3 import ping
ping3.EXCEPTIONS = True

import urllib.request

import subprocess

def get_hostname_ip(hostname, ip):
    try:
        r = requests.get(ip, timeout=3)
        d["info"] = r.text
    except:
        pass

    try:
        hostname = gethostbyaddr(ip)
    except:
        pass
    try:
        ip = gethostbyname(hostname)[0]
    except:
        pass
    
    return hostname, ip

def get_ping(ip):
    p = -1
    host_s = ip.split("//")[-1]
    try:
        if len(ip.split(":")) > 1:
            port = ip.split(":")[-1]
            if "//" not in port:
                try:
                    available = check_socket(host_s.split(":")[0], int(port))
                except:
                    available = False
                if available:
                    p = ping(host_s.split(":")[0], unit="ms", timeout=3)
            else:
                p = ping(host_s.split(":")[0], unit="ms", timeout=3)
        else:
            p = ping(host_s.split(":")[0], unit="ms", timeout=3)
    except:
        pass
    
    if p == None:
        return -1
    return int(p)

def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(3.0)
        if sock.connect_ex((host, port)) == 0:
            return True
        else:
            return False

def get_main_page():
    return "PROTOWORKS SERVER VER0.1"

def check_userlist():
    with open("userlist.txt", "r") as f:
        for line in f.readlines():
            if line == "" or line.startswith("#") or line == "\n":
                continue
            user = line.split()
            ret = db.users.register(user[0], hashlib.md5(user[1].encode()).hexdigest(), user[2])
            if ret == 0:
                print(f"[users] registered new user: {user[0]}")

def time_by_unix(t):
    return dt.fromtimestamp(t).strftime("%d/%m/%Y, %H:%M:%S")

def json_str(s):
    return json.dumps(s, indent=4)

def scan_for_subdirs(dirname):
    subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(scan_for_subdirs(dirname))
    return subfolders

def _read_file_chunks(path):
    CHUNK_SIZE = int(config["networking"]["chunk_size"])
    with open(path, 'rb') as fd:
        while 1:
            buf = fd.read(CHUNK_SIZE)
            if buf:
                yield buf
            else:
                break

def _zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))

def zip(src_path, dest_path):
    if src_path[-1] == "\\":
        src_path = src_path[:-1]
    with zipfile.ZipFile(dest_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        _zipdir(src_path, zipf)

def zip_files(files, src_path, dest_path):
    with zipfile.ZipFile(dest_path, "w") as archive:
        for folder, subfolders, filenames in os.walk(src_path):
            for filename in filenames:
                real_file_path = os.path.join(folder, filename)
                if real_file_path in files:
                    zip_name = real_file_path[len(src_path):]
                    if zip_name[0] == "\\":
                        zip_name = zip_name[1:]
                    archive.write(real_file_path, zip_name)

def delete_file(path):
    os.remove(path)

def get_file_size(path):
    return os.path.getsize(path)

def get_unique_id():
    return str(uuid.uuid1())

def time_now():
    return int(time.time())

def relative(self, path, main):
    filename = path[len(main):]
    if filename[0] == "\\":
        filename = filename[1:]
    return filename

def get_local_ip():
    try:
        if config["custom"]["override_local_ip"] != "":
            return config["custom"]["override_local_ip"]
    except:
        pass
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def backup(origin_path, dest):
    dates = dt.fromtimestamp(time_now()).strftime("%d_%m_%Y_%H_%M_%S")
    fname = f"protoworks_backup_{dates}.zip"
    dest_f = os.path.join(dest, fname)
    zip(origin_path, dest_f)

def get_status():
    data = {}
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    data["local_ip"] = ip
    data["local_ip_override"] = "N/A"
    try:
        if config["custom"]["override_local_ip"] != "":
            data["local_ip_override"] = config["custom"]["override_local_ip"]
    except:
        pass

    public_ip = urllib.request.urlopen('https://v4.ident.me/').read().decode('utf8')
    data["public_ip"] = public_ip
    data["uptime"] = time.time() - psutil.boot_time()
    try:
        data["hub_status"] = db.monitoring.get_device("MAIN_HUB")["status"]
    except:
        data["hub_status"] = "N/A"

    data["cpu_load"] = psutil.cpu_percent()
    data["ram_total"] = psutil.virtual_memory().total
    data["ram_used"] = data["ram_total"] - psutil.virtual_memory().available
    return data

def get_lan_clients():
    ret = subprocess.check_output(['sw_requirements\\map_network.bat']).decode()
    ret = ret.split("clients_list\r\n")[-1]
    ret = ret.replace("'", "")
    ret = ret.replace("[", "")
    ret = ret.replace("]", "")
    ret = ret.replace("\r\n", "")
    lst = ret.split(", ")
    return lst

def restart_self():
    path = config["path"]["restart_routine_bat"]
    os.system(f"start {path}")
    os.kill(os.getpid(),signal.SIGTERM)