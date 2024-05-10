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
from UI.widgets.QYesOrNoDialog import QYesOrNoDialog
from UI.widgets.QAskForFilesDialog import QAskForFilesDialog

import defines

from PySide6.QtCore import Signal, QObject
import time

class PingSignals(QObject):
    ping_finished = Signal(int)
    define_finished = Signal(str)
    status_changed = Signal(str)

class MachineListEntry(QFrame):
    def __init__(self, machine):
        super().__init__()
        self.machine = machine
        self.slave = env.net_manager.slaves.get_slave(self.machine["slave_id"])["slave"]

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.ping_signals = PingSignals()
        self.ping_signals.ping_finished.connect(self.change_ping_state)
        self.ping_signals.define_finished.connect(self.notify_define)
        self.ping_signals.status_changed.connect(self.status_changed_ui)

        self.layout = QVBoxLayout()

        idx = machine["id"]
        slave_id = machine["slave_id"]
        name = machine["name"]
        plate = machine["plate"]
        delta = machine["delta"]
        unique_info = machine["unique_info"]

        self.machine_name_label = QLabel(name)
        self.machine_idx_label = QLabel(f"ID: {str(idx)}")
        self.machine_slave_idx_label = QLabel(f"ID слейва: {str(slave_id)}")
        #self.machine_plate_label = QLabel(f"Стол: {str(plate)}")

        if plate["x"] == -1:
            self.machine_plate_label = QLabel(f"Стол Дельта: {str(delta)}")
        else:
            self.machine_plate_label = QLabel(f"Стол XYZ: {str(plate)}")

        self.machine_status_label = QLabel(f"Состояние: Ожидание данных")
        #self.machine_unique_info_label = QLabel(f"Информация: {str(unique_info)}")


        self.layout.addWidget(self.machine_name_label)
        self.layout.addWidget(self.machine_idx_label)
        self.layout.addWidget(self.machine_slave_idx_label)
        self.layout.addWidget(self.machine_plate_label)
        self.layout.addWidget(self.machine_status_label)
        #self.layout.addWidget(self.machine_unique_info_label)


        self.menu = QMenu(self)
        self.menu.setStyleSheet(stylesheets.DEFAULT_BORDER_STYLESHEET)
        action_queue = self.menu.addAction("Открыть очередь")
        action_force_start = self.menu.addAction("Запустить файл вне очереди")
        action_restart_handler = self.menu.addAction("Перезапустить обработчик станка на слейве")
        action_restart_connection = self.menu.addAction("Перезапустить соединение станка с обработчиком")
        action_send_command = self.menu.addAction("Отправить команду")
        action_pause = self.menu.addAction("Пауза")
        action_stop = self.menu.addAction("Отменить работу")
        action_restart = self.menu.addAction("Перезапустить")
        action_edit = self.menu.addAction("Редактировать")
        action_delete = self.menu.addAction("Удалить")

        action_force_start.triggered.connect(self.force_start)
        action_restart_handler.triggered.connect(self.restart_handler)
        action_restart_connection.triggered.connect(self.restart_connection)
        action_send_command.triggered.connect(self.send_command)
        action_stop.triggered.connect(self.stop_job)

        # action_ping.triggered.connect(self.ping_host)
        # action_info.triggered.connect(self.define)
        # action_restart.triggered.connect(self.restart)
        # action_get_machines.triggered.connect(self.get_machines_list)
        # action_edit.triggered.connect(self.edit)
        # action_delete.triggered.connect(self.delete_slave)

        self.setLayout(self.layout)

        self.update_data()

    def stop_job(self):
        self.dlg = QYesOrNoDialog("Вы уверены, что хотите отменить текущую работу станка?")
        self.dlg.exec()
        if self.dlg.answer:
            env.net_manager.machines.cancel_job(self.slave["id"], self.machine["id"])
            utils.message("Запрос отправлн", tittle="Оповещение")

    # def auto_update(self):
    #     while self.isVisible():
    #         time.sleep(2)
        
    #     #env.net_manager.get_all_machines_states()

    def status_changed_ui(self, status):
        self.machine_status_label.setText("Состояние: " + status)

    def check_online_thread(self):
        while True:
            try:
                status = env.net_manager.machines.check_online(self.machine["id"])["status"]
                self.ping_signals.status_changed.emit(status)
            except: 
                self.ping_signals.status_changed.emit("Нет соединения")
            time.sleep(3)

    def update_data(self):
        env.task_manager.run_silent_task(self.check_online_thread)

    def force_start(self):
        self.dlg = QYesOrNoDialog("Вы уверены, что хотите отменить текущую работу станка для запуска другого файла?")
        self.dlg.exec()
        if self.dlg.answer:
            env.net_manager.machines.cancel_job(self.slave["id"], self.machine["id"])
        
        self.files_dlg = QAskForFilesDialog("Выберите GCODE файл", only_one_file=True, callback_yes=self.force_start_file)
        self.files_dlg.exec()

    def force_start_file(self, file):
        env.net_manager.machines.upload_gcode_file(self.machine["slave_id"], self.machine["id"], file)
        env.net_manager.machines.start_job(self.machine["slave_id"], self.machine["id"], file.split("\\")[-1])
        utils.message("Запрос отправлен", tittle="Оповещение")

    
    def send_command(self):
        env.net_manager.machines.send_gcode_command(self.machine["slave_id"], self.machine["id"], "G28")
        utils.message("Запрос отправлен", tittle="Оповещение")

    def restart_connection(self):
        env.net_manager.machines.reconnect(self.machine["slave_id"], self.machine["id"])
        utils.message("Запрос отправлен", tittle="Оповещение")

    def restart_handler(self):
        env.net_manager.machines.restart_handler(self.machine["slave_id"], self.machine["id"])
        utils.message("Запрос отправлен", tittle="Оповещение")

    def restart(self):
        self.dlg = QYesOrNoDialog("Вы действительно хотите перезапустить слейв?")
        self.dlg.exec()
        if self.dlg.answer:
            env.net_manager.slaves.restart(self.slave["id"])
            utils.message("Запрос отправлен.", tittle="Оповещение")

    def set_ping(self, ping):
        if int(ping) == -1:
            ping = "Соединение не удалось"
        elif int(ping) == -2:
            ping = "Ожидание ответа"
        self.slave["ping"] = ping
        self.ping_label.setText(f"Задержка {str(ping)} мс.")

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