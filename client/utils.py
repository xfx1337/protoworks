from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QSplitter, QLabel, QMessageBox

import shutil
import os

import uuid

from datetime import datetime as dt
import time

import defines
import environment.task_manager.statuses as task_statuses

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()

def get_unique_id():
    return str(uuid.uuid1())

def get_opened_tabs_count(l):
    c = 0
    for key in l.keys():
        if l[key]:
            c += 1
    return c

def unix_is_expired(t):
    if t < time.time():
        return True
    return False

def project_status(st):
    if st == defines.PROJECT_IN_WORK:
        return "В работе"
    elif st == defines.PROJECT_DONE:
        return "Сдан"
    else:
        return f"Неизвестно({str(st)})"

def time_by_unix(t):
    return dt.fromtimestamp(t).strftime("%d/%m/%Y, %H:%M:%S")

def common_elements(list1, list2):
    return [element for element in list1 if element in list2]

def message(text, tittle="Ошибка"):
    msg_box = QMessageBox()
    msg_box.setWindowIcon(templates_manager.icons["proto"])
    msg_box.setWindowTitle(tittle)
    msg_box.setText(text)
    msg_box.setWindowFlags(Qt.WindowStaysOnTopHint)
    msg_box.exec()

def validate_run_requirements(env):
    valid = True
    out = "Не выполнены условия для полноценного запуска программы. Выполните условия по инструкции ниже и перезапустите программу\n"
    if env.config_manager["path"]["projects_path"] == "none":
        valid = False
        out += "\nУкажите путь для проектов в настройках"
    

    if valid == False:
        message(out, tittle="Условия запуска")

def relative(path, parent):
    return os.path.join(parent, path)

def remove_path(main, full):
    if main[-1] == "\\":
        return full[len(main):]
    else:
        return full[len(main)+1:]