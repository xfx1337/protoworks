from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QDialog, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox
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

from UI.widgets.QEasyScroll import QEasyScroll

from PySide6.QtCore import Signal, QObject

from UI.tabs.machines_tab.MachineListEntries.MachineFDMListEntry import MachineFDMListEntry

from UI.widgets.QEasyScrollDrop import QEasyScrollDrop

class MachinesSelectDialog(QDialog):
    def __init__(self, machines_selected = []):
        self.machines_selected = machines_selected
        super().__init__()
        self.setStyleSheet(stylesheets.TOOLTIP)

        self.setWindowTitle(f"Выбор станков")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.h_layout = QHBoxLayout()
        self.layout.addLayout(self.h_layout)

        self.left_frame = QFrame()
        self.left_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.left_frame.setLineWidth(1)
        self.left_column_layout = QVBoxLayout()
        self.left_label = QLabel("Невыбранные станки")
        self.left_scrollable = QEasyScrollDrop(callback=self.accept_left)
        self.left_scrollWidgetLayout = self.left_scrollable.scrollWidgetLayout
        self.left_scrollWidget = self.left_scrollable.scrollWidget


        self.left_column_layout.addWidget(self.left_label)
        self.left_column_layout.addWidget(self.left_scrollable)

        self.left_frame.setLayout(self.left_column_layout)
        self.h_layout.addWidget(self.left_frame)


        self.right_frame = QFrame()
        self.right_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.right_frame.setLineWidth(1)
        self.right_column_layout = QVBoxLayout()
        self.right_label = QLabel("Выбранные станки")
        
        self.right_scrollable = QEasyScrollDrop(callback=self.accept_right)
        self.right_scrollWidgetLayout = self.right_scrollable.scrollWidgetLayout
        self.right_scrollWidget = self.right_scrollable.scrollWidget


        self.right_column_layout.addWidget(self.right_label)
        self.right_column_layout.addWidget(self.right_scrollable)

        self.right_frame.setLayout(self.right_column_layout)
        self.h_layout.addWidget(self.right_frame)

        self.left_entries = []
        self.right_entries = []

        self.exit_btn = QInitButton("Готов", callback=self.close)
        self.layout.addWidget(self.exit_btn)

        self.update_data()

    def get_machines(self):
        return self.machines_selected

    def update_data(self):
        for p in self.left_entries:
            if p.parent() != None:
                p.setParent(None)
        for p in self.right_entries:
            if p.parent() != None:
                p.setParent(None)

        self.left_entries = []
        self.right_entries = []

        machines = env.net_manager.machines.get_machines_list()["machines"]
        slaves = env.net_manager.slaves.get_slaves_list()
        slaves_dc = {}
        for s in slaves["slaves"]:
            slaves_dc[s["id"]] = s
        slaves = slaves_dc



        for i in range(len(machines)):
            machine = machines[i]
            slave = slaves[machine["slave_id"]]
                
            if slave["type"] in [FDM_DIRECT, FDM_OCTO, FDM_KLIPPER]:
                s = MachineFDMListEntry(machine, slave, drag_enable=True, enable_controls=False)

            if machine["id"] not in self.machines_selected:
                self.left_scrollWidgetLayout.insertWidget(i, s)
                self.left_scrollWidgetLayout.setAlignment(s, Qt.AlignmentFlag.AlignTop)
                self.left_entries.append(s)
            else:
                self.right_scrollWidgetLayout.insertWidget(i, s)
                self.right_scrollWidgetLayout.setAlignment(s, Qt.AlignmentFlag.AlignTop)
                self.right_entries.append(s)


    def accept_right(self, idx):
        self.machines_selected.append(int(idx))
        self.update_data()

    def accept_left(self, idx):
        for i in range(len(self.machines_selected)):
            if self.machines_selected[i] == int(idx):
                del self.machines_selected[i]
                self.update_data()