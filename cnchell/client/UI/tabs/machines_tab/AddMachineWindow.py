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
from UI.widgets.QAskForDirectoryDialog import QAskForDirectoryDialog

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

from PySide6.QtCore import Signal, QObject

import gcode_utils

class AddMachineWindow(QWidget):
    def __init__(self, slave_idx):
        super().__init__()
        self.setStyleSheet(stylesheets.TOOLTIP)

        slaves = env.net_manager.slaves.get_slaves_list()["slaves"]
        for s in slaves:
            if s["id"] == int(slave_idx):
                self.slave = s

        self.setWindowTitle(f"Добавление станка")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        self.setFixedSize(QSize(750, 750))

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)


        self.label = QLabel("Здесь вы можете добавить станок в систему CNCHell.")
        self.layout.addWidget(self.label)

        self.label = QLabel("Отключите станок от слейва и нажмите Далее")
        self.label.setWordWrap(True)
        self.btn_next = QInitButton("Далее", callback=self.machine_disconnected)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.btn_next)

    def machine_disconnected(self):
        self.old_connected_devices = env.net_manager.slaves.get_devices(self.slave["id"])['machines']
        self.label.setText("Подключите станок обратно к слейву и нажмите Далее")
        self.btn_next.callback = self.machine_connected
    
    def machine_connected(self):
        self.new_connected_devices = env.net_manager.slaves.get_devices(self.slave["id"])['machines']
        
        self.device = None
        for d in self.new_connected_devices:
            if d not in self.old_connected_devices:
                self.device = d
                break
        
        if self.device == None:
            utils.message("Станок не найден.")
            self.close()
            return
        
        x = -1
        machines = env.net_manager.machines.get_machines_list()["machines"]
        for m in machines:
            if int(m["id"]) > x:
                x = int(m["id"])

        self.unique_info = {"data": str(x+1)}
        self.label.setText(f"Подключён {self.device} с уникальной информацией: \n{str(self.unique_info)}. Нажмитее далее для перехода к настройке станка")
        
        self.btn_next.callback = self.machine_settings

    def machine_settings(self):
        self.label.setText(f"Подключён {self.device} с уникальной информацией: \n{str(self.unique_info)}.")
        self.notes_machine_label = QLabel("Если станок имеет дельта кинематику - устанавливайте лишь параметры дельты. Аналогично и для XYZ кинематики")
        self.notes_baudrate_label = QLabel("Если подключение станка не подразумевает коммуникацию по serial - не указывайте Баудрейт")
        self.notes_gcode_manager_label = QLabel("Если станок не подразумевает работу с GCODE - не указывайте тип GCODE")
        self.notes_machine_label.setWordWrap(True)
        self.notes_baudrate_label.setWordWrap(True)
        
        self.name_input = QUserInput("Название: ", corner_align=True)
        self.x_input = QUserInput("Длина оси X в мм: ", corner_align=True)
        self.y_input = QUserInput("Длина оси Y в мм: ", corner_align=True)
        self.z_input = QUserInput("Длина оси Z в мм: ", corner_align=True)
        self.delta_radius_input = QUserInput("Радиус основания: ", corner_align=True)
        self.delta_height_input = QUserInput("Высота принтера кинематики дельта: ", corner_align=True)
        self.baudrate_input = QUserInput("Баудрейт: ", corner_align=True)
        self.gcode_manager_select = QChooseManyCheckBoxes("Выберите тип GCODE", GCODE_TYPES_STR, allow_only_one=True)
        self.enable_unique_info_on_sd = QCheckBox("Хранить уникальную информацию на SD?")

        self.btn_next.hide()

        self.layout.addWidget(self.notes_machine_label)
        self.layout.addWidget(self.notes_baudrate_label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.x_input)
        self.layout.addWidget(self.y_input)
        self.layout.addWidget(self.z_input)
        self.layout.addWidget(self.delta_radius_input)
        self.layout.addWidget(self.delta_height_input)
        self.layout.addWidget(self.baudrate_input)
        self.layout.addWidget(self.gcode_manager_select)
        self.layout.addWidget(self.enable_unique_info_on_sd)

        self.btn_finish = QInitButton("Добавить станок", callback=self.add_machine_finish)
        self.layout.addWidget(self.btn_finish)
    

    def add_machine_finish(self):
        if self.enable_unique_info_on_sd:
            dlg = QAskForDirectoryDialog("Выберите sd карту")
            dlg.exec()
            folder = dlg.fname
            fname = self.unique_info["data"]
            open(os.path.join(folder, f"PWP{fname}.gcode"), "a").close()

            # fname = self.unique_info["data"]
            # fname = f"PWP{fname}.gco"
            # commands = [f"M28 {fname}", gcode_utils.convert("G28", 1), "M29"]
            # env.net_manager.machines.send_gcode_command(-1, commands, self.slave["id"], self.device)

        else:
            self.unique_info = "-1"
        x = -1
        y = -1
        z = -1
        try:
            x = int(self.x_input.get_input())
            y = int(self.y_input.get_input())
            z = int(self.z_input.get_input())
        except:
            pass

        radius = -1
        height = -1
        try:
            radius = int(self.delta_radius_input.get_input())
            height = int(self.delta_height_input.get_input())
        except:
            pass

        gcode_type = -1
        try:
            gcode_type = GCODE_TYPES_TRANSLATIONS_BACKWARDS[self.gcode_manager.get_selected[0]]
        except:
            pass

        baudrate = 115200
        try:
            baudrate = int(self.baudrate_input.get_input())
        except: pass

        env.net_manager.machines.add_machine(
            self.name_input.get_input(), self.slave["id"], 
            self.unique_info, 
        {"x": x, "y": y, "z": z},
        {"radius": radius, "height": height},
        gcode_type,
        baudrate)
        
        utils.message("Станок добавлен", tittle="Оповещение")
        self.close()