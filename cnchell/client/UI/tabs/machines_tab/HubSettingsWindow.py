from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox
from PySide6.QtCore import QTimer

import os, shutil

from ping3 import ping, verbose_ping

import utils
from defines import *

import UI.stylesheets as stylesheets
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QUserInput import QUserInput
from UI.widgets.QChooseManyCheckBoxes import QChooseManyCheckBoxes

from UI.widgets.QAreUSureDialog import QAreUSureDialog

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

from PySide6.QtCore import Signal, QObject

class PingSignals(QObject):
    ping_finished = Signal(int)
    define_finished = Signal(str)
    data_got = Signal(dict)

class HubSettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(stylesheets.TOOLTIP)
        
        hostname = "Ожидание данных"
        ip = "Ожидание данных"
        ping = "Ожидание данных"
        info = "Ожидание данных"

        self.ping_signals = PingSignals()
        self.ping_signals.ping_finished.connect(self.change_ping_state)
        self.ping_signals.define_finished.connect(self.notify_define)
        self.ping_signals.data_got.connect(self.update_data_s)

        self.setWindowTitle(f"Настройки Hub'а")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Hub - главная плата в кластере, который управляет станками. Если она не подключена - все станки в локальной её сети будут недоступны.")
        self.layout.addWidget(self.label)

        self.current_frame = QFrame()
        self.current_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.current_frame.setLineWidth(1)
        self.current_frame_layout = QVBoxLayout()
        self.hostname_label = QLabel(f"Хостнейм: {hostname}")
        self.ip_label = QLabel(f"IP: {ip}")
        if ping == -1:
            ping = "Оффлайн"
        self.ping_label = QLabel(f"Задержка: {ping}")
        self.info_label = QLabel(f"Информация: {info}")
        self.current_frame_layout.addWidget(self.hostname_label)
        self.current_frame_layout.addWidget(self.ip_label)
        self.current_frame_layout.addWidget(self.ping_label)
        self.current_frame_layout.addWidget(self.info_label)
        self.current_frame.setLayout(self.current_frame_layout)

        self.layout.addWidget(self.current_frame)


        self.host_layout = QHBoxLayout()
        self.change_label = QLabel("Изменить")
        self.host_input = QUserInput("Локальный хост(http://ip:port): ", corner_align=True)
        self.ping_btn = QInitButton("Проверить", callback=self.ping_host)
        self.define_btn = QInitButton("Запросить информацию", callback=self.define)
        self.host_layout.addWidget(self.host_input)
        self.host_layout.addWidget(self.ping_btn)
        self.host_layout.addWidget(self.define_btn)

        self.layout.addWidget(self.change_label)
        self.layout.addLayout(self.host_layout)

        self.notes_host_label = QLabel("Желательно указывать hostname, а не IP.")
        self.layout.addWidget(self.notes_host_label)

        self.hostname_or_ip = QCheckBox("Hostname?")
        self.layout.addWidget(self.hostname_or_ip)

        self.set_btn = QInitButton("Установить", callback=self.set_hub)
        self.layout.addWidget(self.set_btn)

        self.update_data()

    def update_data_s(self, hub_info):
        if hub_info["got"] == False:
            hostname = "Нет"
            ip = "Нет"
            ping = "Оффлайн"
            info = "Нет"
        else:
            hostname = hub_info["hostname"]
            ip = hub_info["ip"]
            ping = int(hub_info["ping"])
            info = hub_info["info"]
        
        self.hostname_label.setText(f"Хостнейм: {hostname}")
        self.ip_label.setText(f"IP: {ip}")
        self.ping_label.setText(f"Задержка: {ping}")
        self.info_label.setText(f"Информация: {info}")
    
    def data_thread(self):
        hub_info = env.net_manager.hardware.get_hub_info()
        if hub_info == None:
            hub_info = {}
            hub_info["got"] = False
        else:
            hub_info["got"] = True
        self.ping_signals.data_got.emit(hub_info)

    def update_data(self):
        env.task_manager.run_silent_task(self.data_thread)

    def set_hub(self):
        host = self.host_input.get_input()
        if host == "":
            utils.messsage("Не указан ни IP, ни hostname")
            return
        if self.hostname_or_ip.isChecked():
            hostname = host
            ip = ""
        else:
            ip = host
            hostname = ""
        try:
            env.net_manager.hardware.set_hub(hostname, ip)
            utils.message("Успешно", tittle="Оповещение")
        except:
            pass

    def change_ping_state(self, delay):
        self.ping_btn.setEnabled(True)
        self.ping_btn.setText("Задержка: " + str(delay) + "мс. Проверить снова")

    def ping_host(self):
        self.ping_btn.setEnabled(False)
        self.ping_btn.setText("Ожидание")
        env.task_manager.run_silent_task(self.ping_thread)

    def ping_thread(self):
        host = self.host_input.get_input()
        try:
            ret = env.net_manager.hardware.ping(host, is_hostname=self.hostname_or_ip.isChecked())
            delay = ret
        except:
            delay = -1
        self.ping_signals.ping_finished.emit(int(delay))

    def notify_define(self, text):
        utils.message(text, tittle="Оповещение")

    def define(self):
        host = self.host_input.get_input()
        try:
            ret = env.net_manager.hardware.send_get_request(host, is_hostname=self.hostname_or_ip.isChecked())
            delay = ret
        except:
            delay = -1
        self.ping_signals.define_finished.emit(str(delay))