from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox
from PySide6.QtCore import QTimer

import os, shutil
import time

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

from UI.tabs.machines_tab.QueueWindow import QueueWindow
from UI.tabs.machines_tab.MachinesSelectDialog import MachinesSelectDialog

from UI.widgets.QEasyScrollDrop import QEasyScrollDrop

class QueueManagerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(stylesheets.TOOLTIP)

        self.setWindowTitle(f"Менеджер Очередей")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        self.setMinimumSize(QSize(1280, 720))

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.left_column_layout = QVBoxLayout()

        self.upper_frame = QFrame()
        self.upper_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.upper_frame.setLineWidth(1)
        self.upper_frame_layout = QVBoxLayout()

        self.notes_label = QLabel("Здесь можно распределить детали по станкам путем перетаскивания деталей-работ по станкам. Так же можно воспользоваться автораспределением")
        self.notes_label.setWordWrap(True)
        self.machines_select_btn = QInitButton("Станков выбрано: 0", callback=self.machines_select)
        self.auto_distribution_btn = QInitButton("Автораспределение", callback=self.auto_distribution)
        self.apply_distribution = QInitButton("Применить распределение", callback=self.save_distribution)

        self.upper_frame_layout.addWidget(self.notes_label)
        self.upper_frame_layout.addWidget(self.machines_select_btn)
        self.upper_frame_layout.addWidget(self.auto_distribution_btn)
        self.upper_frame_layout.addWidget(self.apply_distribution)


        self.upper_frame.setLayout(self.upper_frame_layout)

        self.distribution_queue = QueueWindow({"id": -1, "name": "Нераспределенная очередь"}, distribution_queue=True, window=False, auto_update=False, enable_job_drop=True)
        
        self.left_column_layout.addWidget(self.upper_frame)
        self.left_column_layout.addWidget(self.distribution_queue)

        self.h_layout = QHBoxLayout()
        self.layout.addLayout(self.h_layout)

        self.right_scrollable = QEasyScrollDrop(callback=lambda: 1+1, horizontal=True, vertical=False, disable_drop=True)
        self.right_scrollWidgetLayout = self.right_scrollable.scrollWidgetLayout
        self.right_scrollWidget = self.right_scrollable.scrollWidget

        self.h_layout.addLayout(self.left_column_layout, 30)
        self.h_layout.addWidget(self.right_scrollable, 70)

        self.machines_ids = []
        self.queue_entries = []
        
        self.update_data(dont_show_message=True)

    def update_data(self, dont_show_message=False):
        if not dont_show_message:
            utils.message("Текущее распределение сброшено.", tittle="Оповещение")
        queue = env.net_manager.work_queue.get_queue(-1)
        queue = sorted(queue, key = lambda key: key["index"])
        self.distribution_queue.update_data(queue)

        for p in self.queue_entries:
            if p.parent() != None:
                p.setParent(None)
    
        self.queue_entries = []
        machines = env.net_manager.machines.get_machines_list()["machines"]
        machines_dc = {}
        for m in machines:
            machines_dc[m["id"]] = m
        machines = machines_dc

        for i in range(len(self.machines_ids)):
            idx = self.machines_ids[i]
            s = QueueWindow(machines[idx], window=False, auto_update=False, enable_job_drop=True, distribution_queue_ref=self.distribution_queue)
            self.right_scrollWidgetLayout.insertWidget(i, s)
            self.right_scrollWidgetLayout.setAlignment(s, Qt.AlignmentFlag.AlignLeft)
            self.queue_entries.append(s)


    def machines_select(self):
        self.machines_select_dlg = MachinesSelectDialog(self.machines_ids)
        self.machines_select_dlg.exec()
        machines_ids = self.machines_select_dlg.get_machines()
        self.machines_ids = machines_ids
        self.machines_select_btn.setText(f"Станков выбрано: {len(self.machines_ids)}")
        self.update_data()

    def auto_distribution(self):
        pass
    
    def save_distribution(self):
        jobs_indexes_to_del = {}
        jobs_to_add = []
        for job in self.distribution_queue.queue:
            if job["machine_id"] != -1:
                if job["machine_id"] in jobs_indexes_to_del:
                    jobs_indexes_to_del[job["machine_id"]].append(job["index"])
                else:
                    jobs_indexes_to_del[job["machine_id"]] = [job["index"]]

                job["machine_id"] = -1
                del job["index"]
                jobs_to_add.append(job)
        for queue in self.queue_entries:
            for job in queue.queue:
                if job["machine_id"] != queue.machine["id"]:
                    if job["machine_id"] in jobs_indexes_to_del:
                        jobs_indexes_to_del[job["machine_id"]].append(job["index"])
                    else:
                        jobs_indexes_to_del[job["machine_id"]] = [job["index"]]
                    job["machine_id"] = queue.machine["id"]
                    del job["index"]
                    jobs_to_add.append(job)
        
        for m in jobs_indexes_to_del.keys():
            indexes = jobs_indexes_to_del[m]
            env.net_manager.work_queue.delete_jobs(indexes, m)
        env.net_manager.work_queue.add_jobs(jobs_to_add, [])

        utils.message("Распределение применено", tittle="Оповещение")