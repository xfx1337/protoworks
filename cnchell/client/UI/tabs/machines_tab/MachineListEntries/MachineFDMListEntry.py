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
from UI.widgets.QAskForLineDialog import QAskForLineDialog

from UI.tabs.machines_tab.widgets.MachineInteractiveMover import MachineInteractiveMover
from UI.tabs.machines_tab.widgets.MachineInteractiveTemperature import MachineInteractiveTemperature
from UI.widgets.QWebTerminal import QWebTerminal
from UI.tabs.machines_tab.QueueWindow import QueueWindow
from UI.tabs.machines_tab.MachineListEntriesWindows.FDMBindingsWindow import FDMBindingsWindow

import defines
from defines import *

from PySide6.QtCore import Signal, QObject
import time

from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag

class PingSignals(QObject):
    ping_finished = Signal(int)
    define_finished = Signal(str)
    status_changed = Signal(str)

class MachineFDMListEntry(QFrame):
    def __init__(self, machine, slave, drag_enable=False, enable_controls=True):
        super().__init__()
        self.machine = machine
        self.slave = slave

        self.enable_controls = enable_controls

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.ping_signals = PingSignals()
        self.ping_signals.ping_finished.connect(self.change_ping_state)
        self.ping_signals.define_finished.connect(self.notify_define)
        self.ping_signals.status_changed.connect(self.status_changed_ui)

        self.layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()

        self.layout.addLayout(self.left_layout)
        self.layout.addLayout(self.right_layout)

        idx = machine["id"]
        slave_id = machine["slave_id"]
        name = machine["name"]
        plate = machine["plate"]
        delta = machine["delta"]
        unique_info = machine["unique_info"]
        status = machine["status"]
        working_state = machine["work_status"]
        type_s = SLAVES_TYPES_TRANSLATIONS[self.slave["type"]]


        self.machine_name_label = QLabel(name)
        self.machine_idx_label = QLabel(f"ID: {str(idx)}")
        self.machine_slave_idx_label = QLabel(f"ID слейва: {str(slave_id)}")
        self.machine_type_label = QLabel(f"Тип: {type_s}")
        #self.machine_plate_label = QLabel(f"Стол: {str(plate)}")

        if plate["x"] == -1:
            self.machine_plate_label = QLabel(f"Стол Дельта: {str(delta)}")
        else:
            self.machine_plate_label = QLabel(f"Стол XYZ: {str(plate)}")

        self.machine_status_label = QLabel(f"Состояние: {status}")
        if status == "offline":
            self.machine_status_label.setStyleSheet(stylesheets.RED_HIGHLIGHT)
        self.machine_work_status_label = QLabel(f"Состояние работы: {working_state}")
        #self.machine_unique_info_label = QLabel(f"Информация: {str(unique_info)}")

        self.machine_time_left_label = QLabel(f"Осталось: N/A")
        self.machine_process_label = QLabel(f"Прогресс: N/A")
        
        if working_state != "Printing":
            self.machine_time_left_label.hide()
            self.machine_process_label.hide()

        self.left_layout.addWidget(self.machine_name_label)
        self.left_layout.addWidget(self.machine_idx_label)
        self.left_layout.addWidget(self.machine_slave_idx_label)
        self.left_layout.addWidget(self.machine_type_label)
        self.left_layout.addWidget(self.machine_plate_label)
        self.left_layout.addWidget(self.machine_status_label)
        self.left_layout.addWidget(self.machine_work_status_label)
        self.left_layout.addWidget(self.machine_time_left_label)
        self.left_layout.addWidget(self.machine_process_label)

        self.alert_label = QLabel("ok")
        self.left_layout.addWidget(self.alert_label)
        self.alert_label.setStyleSheet(stylesheets.YELLOW_HIGHLIGHT)
        self.alert_label.hide()

        st = False
        if "info" in self.machine:
            if "envinronment" in self.machine["info"] and self.machine["info"]["envinronment"] != "offline":
                try:
                    tempertures = self.machine["info"]["envinronment"]["temperature"]
                    actual = tempertures["bed"]["actual"]
                    target = tempertures["bed"]["target"]
                    actual_t = tempertures["tool0"]["actual"]
                    target_t = tempertures["tool0"]["target"]

                    self.bed_temp_label = QLabel(f"Температура стола {actual}/{target}")
                    self.extruder_temp_label = QLabel(f"Температура сопла {actual_t}/{target_t}")
                    self.left_layout.addWidget(self.bed_temp_label)
                    self.left_layout.addWidget(self.extruder_temp_label)
                    st = True
                except:
                    pass
        if not st:
            self.alert_label.setText("Не удалось получить/отобразить данные")
            self.alert_label.show()
        elif time.time() - self.machine["last_seen"] > 10:
            self.alert_label.setText("Станок не отвечает")
            self.alert_label.show()
        else:
            self.alert_label.hide()

        #self.left_layout.addWidget(self.machine_unique_info_label)

        if self.enable_controls:
            self.mover = MachineInteractiveMover(self.move, self.check_online_api)
            self.right_layout.addWidget(self.mover)

            self.menu = QMenu(self)
            self.menu.setStyleSheet(stylesheets.DEFAULT_BORDER_STYLESHEET)
            action_queue = self.menu.addAction("Открыть очередь")
            action_force_start = self.menu.addAction("Запустить файл вне очереди")
            action_restart_handler = self.menu.addAction("Перезапустить обработчик станка на слейве")
            action_restart_connection = self.menu.addAction("Перезапустить соединение станка с обработчиком")
            action_send_command = self.menu.addAction("Отправить команду")
            action_open_terminal = self.menu.addAction("Открыть терминал(LAN)")
            action_bindings = self.menu.addAction("Бинды")
            action_pause = self.menu.addAction("Пауза")
            action_stop = self.menu.addAction("Отменить работу")
            #action_edit = self.menu.addAction("Редактировать")
            action_delete = self.menu.addAction("Удалить")

            action_force_start.triggered.connect(self.force_start)
            action_restart_handler.triggered.connect(self.restart_handler)
            action_restart_connection.triggered.connect(self.restart_connection)
            action_open_terminal.triggered.connect(self.open_terminal)
            action_send_command.triggered.connect(self.send_command)
            action_bindings.triggered.connect(self.open_bindings_window)
            action_delete.triggered.connect(self.delete_self)
            action_stop.triggered.connect(self.stop_job)
            action_pause.triggered.connect(self.pause_job)

            action_queue.triggered.connect(self.open_queue)

        # action_ping.triggered.connect(self.ping_host)
        # action_info.triggered.connect(self.define)
        # action_restart.triggered.connect(self.restart)
        # action_get_machines.triggered.connect(self.get_machines_list)
        # action_edit.triggered.connect(self.edit)
        # action_delete.triggered.connect(self.delete_slave)

        temps = [
            {"id": "bed", "name": "Задать температуру стола"},
            {"id": "ext0", "name": "Задать температуру сопла"}
        ]

        self.main_layout.addLayout(self.layout)

        if self.enable_controls:
            self.temps = MachineInteractiveTemperature(temps, self.submit_temps, check_online=self.check_online_api)
            self.main_layout.addWidget(self.temps)

        self.setLayout(self.main_layout)

        #drag
        self.selected = False
        self.dragStartPosition = self.pos()
        self.drag_enable = drag_enable

        self.update_data()

    def mouseMoveEvent(self, event):
        if not self.drag_enable:
            event.accept()
            return
        if not event.buttons() == Qt.LeftButton:
            return
        if ((event.pos() - self.dragStartPosition).manhattanLength()
            < QApplication.startDragDistance()):
            return
        self.selected = True
        self.check_selected()
        drag = QDrag(self)
        drag.setPixmap(env.templates_manager.icons["drag2"].pixmap(256,256))
        mimeData = QMimeData()
        mimeData.setText(str(self.machine["id"]))
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - self.rect().topLeft())

        dropAction = drag.exec_(Qt.CopyAction) 

    def mousePressEvent(self, e):
        if not self.drag_enable:
            e.accept()
            return
        if e.buttons() == Qt.LeftButton:
            if self.selected:
                self.dragStartPosition = e.pos()
            self.selected = not self.selected
            self.check_selected()

    def check_selected(self):
        if not self.drag_enable:
            return
        if self.selected:
            self.setStyleSheet(stylesheets.SELECTED_STYLESHEET)
        else:
            self.setStyleSheet(stylesheets.UNSELECTED_STYLESHEET)

    def open_bindings_window(self):
        self.dlg = FDMBindingsWindow(self.slave, self.machine)
        self.dlg.show()

    def open_queue(self):
        self.queue_show = QueueWindow(self.machine)
        self.queue_show.show()

    def pause_job(self):
        env.net_manager.machines.pause_job(self.machine["id"])
        utils.message("Запрос отправлен", tittle="Оповещение")


    def delete_self(self):
        self.dlg = QYesOrNoDialog("Вы уверены, что хотите удалить станок?")
        self.dlg.exec()
        if self.dlg.answer:
            # TODO: request parts reorder
            try:
                env.net_manager.machines.delete(self.machine["id"])
                self.hide()
                if self.parent() != None:
                    self.setParent(None)
            except:
                pass

    def submit_temps(self):
        temps = self.temps.get_temps()
        commands = env.machine_utils.get_temp_commands(temps, self.machine["gcode_manager"])
        if len(commands) > 0:
            env.net_manager.machines.send_gcode_command(self.machine["id"], commands)

    def move(self, dirx, dist):
        command = env.machine_utils.get_move_commands(dirx, dist, self.machine["gcode_manager"])
        env.net_manager.machines.send_gcode_command(self.machine["id"], command)

    def check_online_api(self):
        if self.machine["status"] == "offline":
            return False
        return True

    def stop_job(self):
        self.dlg = QYesOrNoDialog("Вы уверены, что хотите отменить текущую работу станка?")
        self.dlg.exec()
        if self.dlg.answer:
            env.net_manager.machines.cancel_job(self.machine["id"])
            utils.message("Запрос отправлен", tittle="Оповещение")

    # def auto_update(self):
    #     while self.isVisible():
    #         time.sleep(2)
        
    #     #env.net_manager.get_all_machines_states()

    def status_changed_ui(self):
        self.machine_status_label.setText("Состояние: " + self.machine["status"])
        if self.machine["status"] == "offline":
            self.machine_status_label.setStyleSheet(stylesheets.RED_HIGHLIGHT)
        else:
            self.machine_status_label.setStyleSheet(stylesheets.NO_HIGHLIGHT)
        working_state = self.machine["work_status"]
        self.machine_work_status_label.setText(f"Состояние работы: {working_state}")

        if working_state != "Printing":
            self.machine_time_left_label.hide()
            self.machine_process_label.hide()
        else:
            self.machine_time_left_label.show()
            self.machine_process_label.show()

        st = False
        if "info" in self.machine:
            if "envinronment" in self.machine["info"] and self.machine["info"]["envinronment"] != "offline":
                try:
                    tempertures = self.machine["info"]["envinronment"]["temperature"]
                    actual = tempertures["bed"]["actual"]
                    target = tempertures["bed"]["target"]
                    actual_t = tempertures["tool0"]["actual"]
                    target_t = tempertures["tool0"]["target"]

                    try:
                        self.bed_temp_label.setText(f"Температура стола {actual}/{target}")
                        self.extruder_temp_label.setText(f"Температура сопла {actual_t}/{target_t}")
                    except:
                        self.bed_temp_label = QLabel(f"Температура стола {actual}/{target}")
                        self.extruder_temp_label = QLabel(f"Температура сопла {actual_t}/{target_t}")
                        self.left_layout.addWidget(self.bed_temp_label)
                        self.left_layout.addWidget(self.extruder_temp_label)
                    st = True
                except:
                    pass
            if "job" in self.machine["info"] and self.machine["info"]["job"] != "N/A":
                try:
                    estimated_time = self.machine["info"]["job"]["progress"]["printTimeLeft"]
                    progress = self.machine["info"]["job"]["progress"]["completion"]
                    if estimated_time != None:
                        estimated_time = int(estimated_time)
                        self.machine_time_left_label.setText(f"Осталось: {utils.seconds_to_str(estimated_time)}")
                    if progress != None:
                        #progress = round(progress, 2)
                        #progress = str(progress).split(".")[-1]
                        #progress = progress.lstrip('0')
                        self.machine_process_label.setText(f"Прогресс: {int(progress)}%")
                except:
                    pass
        
        if not st:
            self.alert_label.setText("Не удалось получить/отобразить данные")
            self.alert_label.show()
        elif time.time() - self.machine["last_seen"] > 10:
            self.alert_label.setText("Станок не отвечает")
            self.alert_label.show()
        else:
            self.alert_label.hide()

    def check_online_thread(self):
        while True:
            try:
                self.machine = env.net_manager.machines.get_machine(self.machine["id"])
                self.ping_signals.status_changed.emit(self.machine["status"])
            except: 
                self.ping_signals.status_changed.emit("Нет соединения")
            time.sleep(3)

    def update_data(self):
        env.task_manager.run_silent_task(self.check_online_thread)

    def force_start(self):
        self.dlg = QYesOrNoDialog("Вы уверены, что хотите отменить текущую работу станка для запуска другого файла?")
        self.dlg.exec()
        if self.dlg.answer:
            env.net_manager.machines.cancel_job(self.machine["id"])
        
        self.files_dlg = QAskForFilesDialog("Выберите GCODE файл", only_one_file=True, callback_yes=self.force_start_file)
        self.files_dlg.exec()

    def force_start_file(self, file):
        env.net_manager.machines.upload_gcode_file(self.machine["id"], file)
        env.net_manager.machines.start_job(self.machine["id"], file.split("\\")[-1])
        utils.message("Запрос отправлен", tittle="Оповещение")

    def send_command(self):
        self.dlg = QAskForLineDialog("Введите строку", "Вопрос")
        self.dlg.exec()
        if self.dlg.answer != "":
            env.net_manager.machines.send_gcode_command(self.machine["id"], self.dlg.answer)
            utils.message("Команда отправлена", tittle="Оповещение")

    def open_terminal(self):
        self.dlg = QYesOrNoDialog("Если вы не находитесь в локальной сети слейва откажитесь нажав 'Нет'")
        self.dlg.exec()
        if self.dlg.answer:
            host = env.net_manager.machines.get_host(self.machine["id"])
            utils.message(f"Хост: {host}")
            #self.term = QWebTerminal(host, FDM_API_KEY_DEFAULT)
            #self.term.show()

    def restart_connection(self):
        env.net_manager.machines.reconnect(self.machine["id"])
        utils.message("Запрос отправлен", tittle="Оповещение")

    def restart_handler(self):
        env.net_manager.machines.restart_handler(self.machine["id"])
        utils.message("Запрос отправлен", tittle="Оповещение")

    def restart(self):
        self.dlg = QYesOrNoDialog("Вы действительно хотите перезапустить слейв?")
        self.dlg.exec()
        if self.dlg.answer:
            env.net_manager.slaves.restart(self.slave["id"])
            utils.message("Запрос отправлен.", tittle="Оповещение")

    def set_ping(self, ping):
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
        if self.enable_controls:
            self.menu.exec(event.globalPos())

    def change_ping_state(self, delay):
        self.ping_label.setText("Задержка: " + str(delay) + "мс.")

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