import os, shutil, sys, subprocess
import locale
import win32api, win32print

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

    command = "{} {}".format('sw_requirements\\PDFtoPrinter.exe', path)
    subprocess.call(command, shell=True) 
    return "Отправлены на печать", 200
