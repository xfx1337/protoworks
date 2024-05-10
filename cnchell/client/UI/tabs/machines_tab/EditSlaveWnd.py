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
from UI.widgets.QAskForNumberDialog import QAskForNumberDialog

from UI.widgets.QAreUSureDialog import QAreUSureDialog

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

from PySide6.QtCore import Signal, QObject

class PingSignals(QObject):
    ping_finished = Signal(int)
    define_finished = Signal(str)

class EditSlaveWnd(QWidget):
    def __init__(self, slave):
        self.slave = slave
        super().__init__()
        self.setStyleSheet(stylesheets.TOOLTIP)

        self.ping_signals = PingSignals()
        self.ping_signals.ping_finished.connect(self.change_ping_state)
        self.ping_signals.define_finished.connect(self.notify_define)

        self.setWindowTitle(f"Редактирование слейва")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        idx = slave["id"]
        hostname = slave["hostname"]
        ip = slave["ip"]
        type_s = slave["type"]
        type_ss = SLAVES_TYPES_TRANSLATIONS[type_s]
        ping_s = slave["ping"]

        self.current_frame = QFrame()
        self.current_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.current_frame.setLineWidth(1)
        self.current_frame_layout = QVBoxLayout()
        self.id_label = QLabel(f"ID: {idx}")
        self.hostname_label = QLabel(f"Хостнейм: {hostname}")
        self.ip_label = QLabel(f"IP: {ip}")
        if ping_s == -1:
            ping = "Оффлайн"
        if ping_s == -2:
            ping = "Ожидание ответа"
        else:
            ping = ping_s
        self.ping_label = QLabel(f"Задержка: {ping} мс.")
        self.current_frame_layout.addWidget(self.hostname_label)
        self.current_frame_layout.addWidget(self.ip_label)
        self.current_frame_layout.addWidget(self.ping_label)
        self.current_frame.setLayout(self.current_frame_layout)

        self.layout.addWidget(self.current_frame)



        #self.notes_label = QLabel("Если вы настраиваете слейв на Octoprint'е или Klipper'е - не указывайте порт. Порт нужно будет указать при создании станков")
        #self.layout.addWidget(self.notes_label)

        self.host_layout = QHBoxLayout()
        self.ip_input = QUserInput("Локальный хост(http://ip:port): ", corner_align=True)
        self.hostname_input = QUserInput("Hostname: ", corner_align=True)
        self.ping_btn = QInitButton("Проверить", callback=self.ping_host)
        
        self.define_btn = QInitButton("Запросить информацию по указанному IP", callback=self.define)

        self.host_layout.addWidget(self.ip_input)
        self.host_layout.addWidget(self.hostname_input)
        self.host_layout.addWidget(self.ping_btn)
        self.host_layout.addWidget(self.define_btn)

        self.layout.addLayout(self.host_layout)

        self.notes_host_label = QLabel("Если слейв находится в локальной сети главного хаба, желательно, указывать hostname слейва тк он не меняется в отличии от ip.")
        self.layout.addWidget(self.notes_host_label)

        self.edit_btn = QInitButton("Редактировать", callback=self.edit)
        self.layout.addWidget(self.edit_btn)

    def edit(self):
        ip = self.ip_input.get_input()
        hostname = self.hostname_input.get_input()
        
        env.net_manager.slaves.edit_slave(self.slave["id"], ip, hostname)
        utils.message("Изменено", tittle="Оповещение")
        self.close()

    def change_ping_state(self, delay):
        self.ping_btn.setEnabled(True)
        if delay != -1:
            self.ping_btn.setText("Задержка: " + str(delay) + "мс. Проверить снова")
        else:
            self.ping_btn.setText("Соединение не удалось")

    def ping_host(self):
        self.ping_btn.setEnabled(False)
        self.ping_btn.setText("Ожидание")
        env.task_manager.run_silent_task(self.ping_thread)

    def ping_thread(self):
        host = self.ip_input.get_input()
        try:
            ret = env.net_manager.hardware.ping(host)
            delay = ret
        except:
            delay = -1
        self.ping_signals.ping_finished.emit(int(delay))

    def define(self):
        ip = self.ip_input.get_input()
        try:
            ret = env.net_manager.hardware.send_get_request(ip)
            delay = ret
        except:
            delay = -1
        self.ping_signals.define_finished.emit(str(delay))
    
    def notify_define(self, text):
        utils.message(text, tittle="Оповещение")