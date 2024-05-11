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

from UI.widgets.QEasyScroll import QEasyScroll

from UI.widgets.QAreUSureDialog import QAreUSureDialog

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

from UI.tabs.machines_tab.MachineListEntry import MachineListEntry

from PySide6.QtCore import Signal, QObject

class MachinesListWindowSigals(QObject):
    draw_data = Signal(dict)
    got_pings = Signal()

class MachinesListWindow(QWidget):
    def __init__(self):
        super().__init__()


        self.signals = MachinesListWindowSigals()
        self.signals.draw_data.connect(self.draw_data)
        self.signals.got_pings.connect(self.got_pings)
        self.setStyleSheet(stylesheets.TOOLTIP)

        self.setWindowTitle(f"Список станков")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        self.setFixedSize(QSize(700, 600))


        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Здесь отображены все станки")
        self.layout.addWidget(self.label)

        self.scrollable = QEasyScroll()

        self.scrollWidgetLayout = self.scrollable.scrollWidgetLayout
        self.scrollWidget = self.scrollable.scrollWidget
        self.layout.addWidget(self.scrollable)

        self.machine_entries = []
        self.pings = {}

        env.task_manager.run_silent_task(self.update_data)

    def update_data(self):
        try: 
            data = env.net_manager.machines.get_machines_list()
        except Exception as e: 
            utils.message(str(e))
            return

        self.signals.draw_data.emit(data)

    def got_pings(self):
        for s in self.slave_entries:
            if s.slave["id"] in self.pings:
                s.set_ping(self.pings[s.slave["id"]])

    def draw_data(self, data):
        for p in self.machine_entries:
            if p.parent() != None:
                p.setParent(None)

        self.machine_entries = []
        machines = data["machines"]
        machines = sorted(machines, key=lambda key: (key["slave_id"]))

        for i in range(len(machines)):
            machine = machines[i]

            s = MachineListEntry(machine)
            self.scrollWidgetLayout.insertWidget(i, s)
            self.scrollWidgetLayout.setAlignment(s, Qt.AlignmentFlag.AlignTop)

            self.machine_entries.append(s)
        
