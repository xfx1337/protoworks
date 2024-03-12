import hashlib
import json

import os
import zipfile

from database.database import Database
db = Database()

import uuid
import time
from datetime import datetime as dt

from config import Config
config = Config("config.ini")

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