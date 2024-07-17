from PySide6.QtCore import QSize, Qt
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QTableWidget, QTableWidgetItem, QFileDialog, QApplication

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

# id станка
# название станка
# полный хост
# статус


class MachinesConnectionTableWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        self.setWindowTitle(f"Таблица подключений станков")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.table = QTableWidget(self)  # Create a table
        self.layout.addWidget(self.table)
        machines = env.net_manager.machines.get_machines_list()["machines"]
        self.table.setColumnCount(5)
        self.table.setRowCount(len(machines))
 
        self.table.setHorizontalHeaderLabels(["ID станка", "Название станка", "Полный хост", "Тип хоста", "Состояние"])

        for i in range(len(machines)):
            machine = machines[i]
            host_type_i = env.net_manager.slaves.get_slave(machine["slave_id"])["slave"]["type"]
            id = machine["id"]
            
            if host_type_i in [defines.FDM_DIRECT, defines.FDM_OCTO, defines.FDM_KLIPPER]:
                host_type = "Octo/Klipper"
                host = f"http://127.0.0.1:{defines.FAKE_OCTO_FIRST_PORT+id}"
            else:
                host_type = "Не поддерживается"
                host = "Не поддерживается"
            
            try:
                server = env.server_executor.get_server_by_port(defines.FAKE_OCTO_FIRST_PORT+id)
                status = server.status()
            except:
                status = "Не запущен"
            self.table.setItem(i, 0, QTableWidgetItem(str(machine["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(machine["name"]))
            self.table.setItem(i, 2, QTableWidgetItem(host))
            self.table.setItem(i, 3, QTableWidgetItem(host_type))
            self.table.setItem(i, 4, QTableWidgetItem(status))
        
        self.table.resizeColumnsToContents()