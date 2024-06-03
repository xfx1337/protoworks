from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox
from PySide6.QtCore import QTimer

import os, shutil

import utils
from defines import *

import UI.stylesheets as stylesheets
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QUserInput import QUserInput
from UI.widgets.QEasyScroll import QEasyScroll
from UI.widgets.QFilesDrop import QFilesDrop

from UI.widgets.QAreUSureDialog import QAreUSureDialog

from UI.tabs.machines_tab.JobListEntry import JobListEntry

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

from PySide6.QtCore import Signal, QObject

class FDMBindingsWindow(QWidget):
    def __init__(self, slave, machine):
        super().__init__()
        self.setStyleSheet(stylesheets.TOOLTIP)

        machine_name = machine["name"]
        self.setWindowTitle(f"Бинды станка {machine_name}")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])

        self.slave = slave
        self.machine = machine

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        idx = self.machine["id"]
        m_id = f"MACHINE{idx}"
        next_job_bind = env.net_manager.bindings.get_event_by_action({"devices": [m_id], "action": "NEXT_JOB"})
        cancel_job_bind = env.net_manager.bindings.get_event_by_action({"devices": [m_id], "action": "CANCEL_JOB"})

        self.next_job_event_input = QUserInput("Запустисть следующий файл из очереди")
        self.next_job_event_input.set_input(next_job_bind)

        self.cancel_job_event_input = QUserInput("Отменить работу")
        self.cancel_job_event_input.set_input(cancel_job_bind)

        self.layout.addWidget(self.next_job_event_input)
        self.layout.addWidget(self.cancel_job_event_input)

        self.apply_btn = QInitButton("Применить", callback=self.apply)
        self.layout.addWidget(self.apply_btn)
    
    def apply(self):
        idx = self.machine["id"]
        m_id = f"MACHINE{idx}"
        next_job_bind = env.net_manager.bindings.get_event_by_action({"devices": [m_id], "action": "NEXT_JOB"})
        cancel_job_bind = env.net_manager.bindings.get_event_by_action({"devices": [m_id], "action": "CANCEL_JOB"})

        next_job_bind_new = self.next_job_event_input.get_input()
        cancel_job_bind_new = self.cancel_job_event_input.get_input()

        env.net_manager.bindings.remove(next_job_bind, {"devices": [m_id], "action": "NEXT_JOB"})
        env.net_manager.bindings.remove(cancel_job_bind, {"devices": [m_id], "action": "CANCEL_JOB"})

        env.net_manager.bindings.add(next_job_bind_new, {"devices": [m_id], "action": "NEXT_JOB"})
        env.net_manager.bindings.add(cancel_job_bind_new, {"devices": [m_id], "action": "CANCEL_JOB"})

        utils.message("Бинды изменены.", tittle="Оповещение")