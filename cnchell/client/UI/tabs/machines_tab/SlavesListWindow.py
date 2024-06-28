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

from UI.tabs.machines_tab.SlaveListEntry import SlaveListEntry

from PySide6.QtCore import Signal, QObject

class SlavesListWindowSigals(QObject):
    draw_data = Signal(dict)
    got_pings = Signal()

class SlavesListWindow(QWidget):
    def __init__(self):
        super().__init__()


        self.signals = SlavesListWindowSigals()
        self.signals.draw_data.connect(self.draw_data)
        self.signals.got_pings.connect(self.got_pings)
        self.setStyleSheet(stylesheets.TOOLTIP)

        self.setWindowTitle(f"Список слейвов")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        #self.setFixedSize(QSize(700, 600))


        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Здесь отображены все слейвы")
        self.layout.addWidget(self.label)

        self.scrollable = QEasyScroll()

        self.scrollWidgetLayout = self.scrollable.scrollWidgetLayout
        self.scrollWidget = self.scrollable.scrollWidget
        self.layout.addWidget(self.scrollable)

        self.slave_entries = []
        self.pings = {}

        env.task_manager.run_silent_task(self.update_data)

    def update_data(self):
        try: 
            data = env.net_manager.slaves.get_slaves_list()
        except Exception as e: 
            utils.message(str(e))
            return

        self.signals.draw_data.emit(data)

        self.pings = {}
        for s in data["slaves"]:
            self.pings[s["id"]] = env.net_manager.hardware.ping(s["ip"])
        self.signals.got_pings.emit()

    def got_pings(self):
        for s in self.slave_entries:
            if s.slave["id"] in self.pings:
                s.set_ping(self.pings[s.slave["id"]])

    def draw_data(self, data):
        for p in self.slave_entries:
            if p.parent() != None:
                p.setParent(None)

        self.slave_entries = []

        slaves = data["slaves"]
        slaves = sorted(slaves, key=lambda key: (key["type"], key["ping"]))

        for i in range(len(slaves)):
            slave = slaves[i]

            s = SlaveListEntry(slave)
            self.scrollWidgetLayout.insertWidget(i, s)
            self.scrollWidgetLayout.setAlignment(s, Qt.AlignmentFlag.AlignTop)

            self.slave_entries.append(s)
        
