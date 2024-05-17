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
    msg_box.setWindowIcon(templates_manager.icons["cnchell"])
    msg_box.setWindowTitle(tittle)
    msg_box.setText(text)
    msg_box.setWindowFlags(Qt.WindowStaysOnTopHint)
    msg_box.exec()

def relative(self, path, main):
    filename = path[len(main):]
    if filename[0] == "\\":
        filename = filename[1:]
    return filename

def remove_path(main, full):
    if main[-1] == "\\":
        return full[len(main):]
    else:
        return full[len(main)+1:]

def seconds_to_str(seconds: int) -> str:
    mm, ss = divmod(seconds, 60)
    hh, mm = divmod(mm, 60)
    return "%02d час, %02d мин, %02d сек" % (hh, mm, ss)