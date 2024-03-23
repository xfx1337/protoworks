import os, shutil, sys, subprocess
import locale
import win32api, win32print
import tempfile

import dateutil.parser

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