from PySide6.QtCore import QSize, Qt
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication

import os, shutil
import subprocess
import utils

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

import UI.stylesheets as stylesheets
from UI.widgets.QClickableLabel import QClickableLabel
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QDoubleLabel import QDoubleLabel
from UI.widgets.QAreUSureDialog import QAreUSureDialog

from UI.tabs.machines_tab.EditSlaveWnd import EditSlaveWnd

from UI.widgets.QYesOrNoDialog import QYesOrNoDialog
from UI.widgets.QFilesListSureDialog import QFilesListSureDialog
from UI.widgets.QAskForNumberDialog import QAskForNumberDialog

import defines

from PySide6.QtCore import Signal, QObject

class PingSignals(QObject):
    ping_finished = Signal(int)
    define_finished = Signal(str)

class SlaveListEntry(QFrame):
    def __init__(self, slave):
        super().__init__()
        self.slave = slave

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.ping_signals = PingSignals()
        self.ping_signals.ping_finished.connect(self.change_ping_state)
        self.ping_signals.define_finished.connect(self.notify_define)

        self.layout = QVBoxLayout()

        idx = slave["id"]
        hostname = slave["hostname"]
        ip = slave["ip"]
        type_s = slave["type"]
        type_ss = defines.SLAVES_TYPES_TRANSLATIONS[type_s]
        ping_s = slave["ping"]

        if int(ping_s) == -1:
            ping_s = "Соединение не удалось"
        if int(ping_s) == -2:
            ping_s = "Ожидание ответа"

        self.id_label = QLabel(f"Слейв {idx}")
        self.hostname_label = QLabel(f"Хостнейм: {hostname}")
        self.ip_label = QLabel(f"IP: {ip}")
        self.ping_label = QLabel(f"Задержка: {ping_s} мс.")
        self.type_label = QLabel(f"Тип: {type_ss}")

        self.layout.addWidget(self.id_label)
        self.layout.addWidget(self.hostname_label)
        self.layout.addWidget(self.ip_label)
        self.layout.addWidget(self.ping_label)
        self.layout.addWidget(self.type_label)


        self.menu = QMenu(self)
        self.menu.setStyleSheet(stylesheets.DEFAULT_BORDER_STYLESHEET)
        action_ping = self.menu.addAction("Проверить")
        action_info = self.menu.addAction("Получить информацию")
        action_restart = self.menu.addAction("Перезапустить")
        action_get_machines = self.menu.addAction("Получить список станков")
        action_edit = self.menu.addAction("Редактировать")
        action_delete = self.menu.addAction("Удалить")

        action_ping.triggered.connect(self.ping_host)
        action_info.triggered.connect(self.define)
        action_restart.triggered.connect(self.restart)
        action_get_machines.triggered.connect(self.get_machines_list)
        action_edit.triggered.connect(self.edit)
        action_delete.triggered.connect(self.delete_slave)

        self.setLayout(self.layout)

    def restart(self):
        self.dlg = QYesOrNoDialog("Вы действительно хотите перезапустить слейв?")
        self.dlg.exec()
        if self.dlg.answer:
            env.net_manager.slaves.restart(self.slave["id"])
            utils.message("Запрос отправлен.", tittle="Оповещение")

    def set_ping(self, ping):
        if int(ping) == -1:
            ping = "Соединение не удалось"
            self.ping_label.setStyleSheet(stylesheets.RED_HIGHTLIGHT)
        elif int(ping) == -2:
            ping = "Ожидание ответа"
        self.slave["ping"] = ping
        self.ping_label.setText(f"Задержка {str(ping)} мс.")
        self.ping_label.setStyleSheet(stylesheets.NO_HIGHLIGHT)

    def edit(self):
        wnd = EditSlaveWnd(self.slave)
        wnd.show()

    def get_machines_list(self):
        pass

    def delete_slave(self):
        pass

    def contextMenuEvent(self, event):
        self.menu.exec(event.globalPos())

    def change_ping_state(self, delay):
        if delay != -1:
            self.ping_label.setText("Задержка: " + str(delay) + "мс.")
        else:
            self.ping_label.setText("Соединение не удалось")

    def ping_host(self):
        env.task_manager.run_silent_task(self.ping_thread)

    def ping_thread(self):
        if self.slave["hostname"] != "":
            host = self.slave["hostname"]
            is_hostname = True
        else:
            host = self.slave["ip"]
            is_hostname = False
        try:
            ret = env.net_manager.hardware.ping(host, is_hostname=is_hostname)
            delay = ret
        except:
            delay = -1
        if delay == -1 and is_hostname:
            try:
                ret = env.net_manager.hardware.ping(self.slave["ip"])
                delay = ret
            except:
                delay = -1
        self.ping_signals.ping_finished.emit(int(delay))

    def define(self):
        host = self.slave["ip"]
        if len(host.split(":")) < 3:
            self.dlg = QAskForNumberDialog("Укажите порт, по которому получить информацию.", "Выбор порта")
            self.dlg.exec()
            port = int(self.dlg.answer)
            host = host + ":" + str(port)
        try:
            ret = env.net_manager.hardware.send_get_request(host)
            delay = ret
        except:
            delay = -1
        self.ping_signals.define_finished.emit(str(delay))
    
    def notify_define(self, text):
        utils.message(text, tittle="Оповещение")