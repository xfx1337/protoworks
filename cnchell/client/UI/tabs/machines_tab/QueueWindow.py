from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox
from PySide6.QtCore import QTimer

import os, shutil

import utils
from defines import *

import UI.stylesheets as stylesheets
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QEasyScroll import QEasyScroll
from UI.widgets.QFilesDrop import QFilesDrop

from UI.widgets.QAreUSureDialog import QAreUSureDialog

from UI.tabs.machines_tab.JobListEntry import JobListEntry

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

from PySide6.QtCore import Signal, QObject

class QueueWindow(QWidget):
    def __init__(self, slave, machine):
        super().__init__()
        self.setStyleSheet(stylesheets.TOOLTIP)

        machine_name = machine["name"]
        self.setWindowTitle(f"Очередь станка {machine_name}")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        self.setMinimumSize(QSize(400, 800))

        self.slave = slave
        self.machine = machine

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.upper_frame = QFrame()
        self.upper_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.upper_frame.setLineWidth(1)
        self.upper_frame_layout = QVBoxLayout()
        self.upper_frame.setLayout(self.upper_frame_layout)

        self.files_drop = QFilesDrop("Добавить в очередь", callback=self.add_to_order_drag)
        self.upper_frame_layout.addWidget(self.files_drop)

        self.layout.addWidget(self.upper_frame)

        self.scrollable = QEasyScroll()
        self.scrollWidgetLayout = self.scrollable.scrollWidgetLayout
        self.scrollWidget = self.scrollable.scrollWidget

        self.layout.addWidget(self.scrollable)

        self.job_entries = []

        self.update_data()

    def add_to_order_drag(self, files):
        parts, not_parts = env.part_manager.indentify_parts(files)
        
        jobs = []
        files_send = []

        for f in not_parts:
            un_filename = utils.get_unique_id()
            files_send.append({un_filename: f})
            unique_info = {"job_name": "Работа по файлу", "job_filename": f.split("\\")[-1], "job_send_filename": un_filename}
            job = {"machine_id": self.machine["id"], "work_time": env.machine_utils.calculate_job_time_by_file(f), "work_start": -1, "status": "Ожидание", "unique_info": unique_info}

            jobs.append(job)

        for f in parts:
            un_filename = utils.get_unique_id()
            files_send.append({un_filename: f["path"].split("\\")[-1]})
            unique_info = {"job_name": "Производство детали", "job_filename": f["path"].split("\\")[-1], "job_send_filename": un_filename,
            "job_part_id": f["id"],
            "job_part_name": f["name"], 
            "job_project_id": f["project_id"]}
            job = {"machine_id": self.machine["id"], "work_time": env.machine_utils.calculate_job_time_by_file(f), "work_start": -1, "status": "Ожидание", "unique_info": unique_info}
            jobs.append(job)

        env.net_manager.work_queue.add_jobs(jobs, files_send)

    def update_data(self):
        queue = env.net_manager.work_queue.get_queue(self.machine["id"])
        queue = sorted(queue, key = lambda key: key["index"])

        for p in self.job_entries:
            if p.parent() != None:
                p.setParent(None)

        self.job_entries = []

        for i in range(len(queue)):
            job = queue[i]
            
            p = JobListEntry(job)
            self.scrollWidgetLayout.insertWidget(i, p)
            self.scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)

            self.job_entries.append(p)