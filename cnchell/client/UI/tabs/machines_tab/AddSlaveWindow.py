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

class AddSlaveWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(stylesheets.TOOLTIP)

        self.ping_signals = PingSignals()
        self.ping_signals.ping_finished.connect(self.change_ping_state)
        self.ping_signals.define_finished.connect(self.notify_define)

        self.setWindowTitle(f"Добавление слейва")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)


        self.label = QLabel("Здесь вы можете добавить слейв в систему CNCHell. Слейв - устройство, позволяющее подключить больше станков к CNCHell-Hub")
        self.layout.addWidget(self.label)

        #self.notes_label = QLabel("Если вы настраиваете слейв на Octoprint'е или Klipper'е - не указывайте порт. Порт нужно будет указать при создании станков")
        #self.layout.addWidget(self.notes_label)

        self.host_layout = QHBoxLayout()
        self.host_input = QUserInput("Локальный хост(http://ip:port): ", corner_align=True)
        self.ping_btn = QInitButton("Проверить", callback=self.ping_host)
        self.define_btn = QInitButton("Запросить информацию", callback=self.define)
        self.host_layout.addWidget(self.host_input)
        self.host_layout.addWidget(self.ping_btn)
        self.host_layout.addWidget(self.define_btn)

        self.layout.addLayout(self.host_layout)

        #self.network_btn = QCheckBox("Находится в локальной сети")
        #self.layout.addWidget(self.network_btn)

        self.notes_host_label = QLabel("Если слейв находится в локальной сети главного хаба, желательно, указывать hostname слейва тк он не меняется в отличии от ip.")
        self.layout.addWidget(self.notes_host_label)

        self.hostname_or_ip = QCheckBox("Hostname?")
        self.layout.addWidget(self.hostname_or_ip)

        self.type_choose = QChooseManyCheckBoxes("Выберите тип станков, подключенных к слейву", SLAVE_TYPES_STR, allow_only_one=True)
        self.layout.addWidget(self.type_choose)

        self.add_btn = QInitButton("Добавить", callback=self.add)
        self.layout.addWidget(self.add_btn)

    def add(self):
        host = self.host_input.get_input()
        is_hostname = self.hostname_or_ip.isChecked()
        if is_hostname:
            hostname = host
            ip = ""
        else:
            ip = host
            hostname = ""
        
        s_type = SLAVES_TYPES_TRANSLATIONS_BACKWARDS[self.type_choose.get_selected()[0]]
        env.net_manager.slaves.add_slave(ip, hostname, s_type)
        utils.message("Добавлен", tittle="Оповещение")
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
        host = self.host_input.get_input()
        try:
            ret = env.net_manager.hardware.ping(host, is_hostname=self.hostname_or_ip.isChecked())
            delay = ret
        except:
            delay = -1
        self.ping_signals.ping_finished.emit(int(delay))

    def define(self):
        host = self.host_input.get_input()
        if len(host.split(":")) < 3:
            self.dlg = QAskForNumberDialog("Укажите порт, по которому получить информацию.", "Выбор порта")
            self.dlg.exec()
            port = int(self.dlg.answer)
            host = host + ":" + str(port)
        try:
            ret = env.net_manager.hardware.send_get_request(host, is_hostname=self.hostname_or_ip.isChecked())
            delay = ret
        except:
            delay = -1
        self.ping_signals.define_finished.emit(str(delay))
    
    def notify_define(self, text):
        utils.message(text, tittle="Оповещение")