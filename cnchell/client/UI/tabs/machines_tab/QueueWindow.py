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
from UI.widgets.QYesOrNoDialog import QYesOrNoDialog

from UI.tabs.machines_tab.JobListEntry import JobListEntry

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

from PySide6.QtCore import Signal, QObject

from UI.widgets.QEasyScrollDrop import QEasyScrollDrop

class QueueSignals(QObject):
    update_queue = Signal(list)

class QueueWindow(QWidget):
    def __init__(self, machine=-1, distribution_queue=False, window=True, auto_update=True, enable_job_drop=False, distribution_queue_ref=None):
        super().__init__()
        self.setStyleSheet(stylesheets.TOOLTIP)

        self.distribution_queue_ref = distribution_queue_ref

        self.enable_job_drop = enable_job_drop
        self.window = window

        self.signals = QueueSignals()
        self.signals.update_queue.connect(self.update_data)

        if not distribution_queue and window:
            machine_name = machine["name"]
            self.setWindowTitle(f"Очередь станка {machine_name}")
        elif not distribution_queue:
            machine_name = machine["name"]
        elif window:
            self.setWindowTitle(f"Нераспределенная очередь")

        if window:
            self.setWindowIcon(env.templates_manager.icons["cnchell"])
            self.setMinimumSize(QSize(400, 800))

        self.machine = machine

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        if not distribution_queue:
            self.label = QLabel(f"Очередь станка {machine_name}")
        else:
            self.label = QLabel("Нераспределенная очередь")
        self.layout.addWidget(self.label)

        #self.upper_frame = QFrame()
        #self.upper_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        #self.upper_frame.setLineWidth(1)
        #self.upper_frame_layout = QVBoxLayout()
        #self.upper_frame.setLayout(self.upper_frame_layout)

        
        self.files_drop = QFilesDrop("Добавить в очередь", callback=self.add_to_order_drag)
        #self.upper_frame_layout.addWidget(self.files_drop)

        self.delete_all_btn = QInitButton("Удалить все", callback=self.delete_all)
        #self.upper_frame_layout.addWidget(self.delete_all_btn)

        if not distribution_queue:
            self.redistribute_all_btn = QInitButton("Отправить все на перераспределение(снять с очереди станка)", callback=self.redistribute_all)
            #self.upper_frame_layout.addWidget(self.redistribute_all_btn)

        self.summary_label = QLabel("Всего: 0")
        self.full_time_label = QLabel("Общее время работы: 0с")
        #self.upper_frame_layout.addWidget(self.summary_label)

        #self.layout.addWidget(self.upper_frame)
        if not enable_job_drop:
            self.layout.addWidget(self.files_drop)
        self.layout.addWidget(self.delete_all_btn)
        if not distribution_queue:
            self.layout.addWidget(self.redistribute_all_btn)
        self.layout.addWidget(self.summary_label)
        self.layout.addWidget(self.full_time_label)

        self.scrollable = QEasyScrollDrop(self.job_dropped)
        self.scrollWidgetLayout = self.scrollable.scrollWidgetLayout
        self.scrollWidget = self.scrollable.scrollWidget

        self.layout.addWidget(self.scrollable)

        self.job_entries = []

        self.old_queue = None
        queue = env.net_manager.work_queue.get_queue(self.machine["id"])
        queue = sorted(queue, key = lambda key: key["index"])
        self.queue = queue
        self.signals.update_queue.emit(queue)
        if auto_update:
            env.task_manager.run_silent_task(self.update_thread)

        #self.update_data()

        self.calculate_full_time()

    def calculate_full_time(self):
        full_time = 0
        for job in self.queue:
            full_time += env.machine_utils.calculate_job_time(job)
        
        self.full_time_label.setText(f"Общее время работы: {utils.seconds_to_str(full_time)}")


    def job_dropped(self, idx):
        try:
            idx = int(idx)
        except:
            return
        job = env.net_manager.work_queue.get_job_by_id(idx)
        self.queue.append(job)
        p = JobListEntry(job, queue=self)
        i = len(self.job_entries)
        self.scrollWidgetLayout.insertWidget(i, p)
        self.scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)
        self.job_entries.append(p)
        self.summary_label.setText(f"Всего: {len(self.queue)}")
        self.calculate_full_time()

    def delete_job(self, idx):
        for i in range(len(self.queue)):
            if self.queue[i]["id"] == idx:
                del self.queue[i]
                if self.job_entries[i].parent() != None:
                    self.job_entries[i].setParent(None)
                del self.job_entries[i]
                break
        self.summary_label.setText(f"Всего: {len(self.queue)}")
        self.calculate_full_time()

    def redistribute_all(self):
        if self.window:
            self.dlg = QYesOrNoDialog("Вы действительно хотите отправить задачи на перераспределение (на сервере)?")
            self.dlg.exec()
            if not self.dlg.answer:
                return

            ids_to_del = []
            indexes_to_del = []
            changed_jobs = []
            k = 0
            for i in range(len(self.queue)):
                job = self.queue[i+k]
                if job["status"] != "В работе":
                    ids_to_del.append(job["id"])
                    indexes_to_del.append(job["index"])
                    job["machine_id"] = -1
                    changed_jobs.append(job)
                    del self.queue[i+k]
                    k-=1

            for idx in ids_to_del:
                for i in range(len(self.job_entries)):
                    if self.job_entries[i].job["id"] == idx:
                        if self.job_entries[i].parent() != None:
                            self.job_entries[i].setParent(None)
                        del self.job_entries[i]
                        break

            for job in changed_jobs:
                env.net_manager.work_queue.overwrite_job(job["id"], job)
        elif self.distribution_queue_ref != None:
            for job_e in self.job_entries:
                self.distribution_queue_ref.job_dropped(job_e.job["id"])
                self.delete_job(job_e.job["id"])


        self.summary_label.setText(f"Всего: {len(self.queue)}")

    def delete_all(self):
        self.dlg = QYesOrNoDialog("Вы действительно хотите удалить задачи(на сервере)?")
        self.dlg.exec()
        if not self.dlg.answer:
            return
        ids_to_del = []
        jobs_to_del = {}
        k = 0
        for i in range(len(self.queue)):
            job = self.queue[i+k]
            if job["status"] != "В работе":
                ids_to_del.append(job["id"])
                if job["machine_id"] in jobs_to_del:
                    jobs_to_del[job["machine_id"]].append(job["index"])
                else:
                    jobs_to_del[job["machine_id"]] = [job["index"]]
                
                del self.queue[i+k]
                k-=1


        for idx in ids_to_del:
            for i in range(len(self.job_entries)):
                if self.job_entries[i].job["id"] == idx:
                    if self.job_entries[i].parent() != None:
                        self.job_entries[i].setParent(None)
                    del self.job_entries[i]
                    break
        for m in jobs_to_del.keys():
            env.net_manager.work_queue.delete_jobs(jobs_to_del[m], m)
    
        self.summary_label.setText(f"Всего: {len(self.queue)}")

    def add_to_order_drag(self, files):
        parts, not_parts = env.part_manager.indentify_parts(files)
        
        jobs = []
        files_send = []

        for f in not_parts:
            work_time = 0
            un_filename = utils.get_unique_id()
            files_send.append({un_filename: f})
            job_pre_calculated = False
            unique_info = {"job_name": "Работа по файлу", 
            "job_pre_calculated": job_pre_calculated, "job_pre_calculated_machine": self.machine["id"]}
            if f.split(".")[-1] in MACHINES_FILE_TYPES:
                job_pre_calculated = True
                unique_info["job_pre_calculated"] = True
                unique_info["job_pre_calculated_machine"] = self.machine["id"]
                unique_info["job_pre_calculated_filename"] = f.split('\\')[-1]
                unique_info["job_send_pre_calculated_filename"] = un_filename
            else:
                unique_info["job_pre_calculated"] = False
                unique_info["job_pre_calculated_machine"] = -1
                unique_info["job_filename"] = f.split("\\")[-1]
                unique_info["job_send_filename"] = un_filename
            unique_info["job_count_need"] = 1
            unique_info["job_count_done"] = 0
            
            job = {"machine_id": self.machine["id"], "work_time": env.machine_utils.calculate_job_time_by_file(f), "work_start": -1, "status": "Ожидание", "unique_info": unique_info}

            jobs.append(job)

        for f in parts:
            if f == None:
                continue
            un_filename = utils.get_unique_id()
            #files_send.append({un_filename: f["path"].split("\\")[-1]})
            files_send.append({un_filename: f["path"]})
            job_pre_calculated = False
            m_id = -1
            unique_info = {"job_name": "Производство детали", "job_filename": f["path"].split("\\")[-1], "job_send_filename": un_filename,
            "job_part_id": f["id"],
            "job_part_name": f["name"], 
            "job_project_id": f["project_id"],
            "job_pre_calculated": job_pre_calculated,
            "job_pre_calculated_machine": m_id,
            "job_count_need": 1,
            "job_count_done": 0}
            job = {"machine_id": self.machine["id"], "work_time": env.machine_utils.calculate_job_time_by_file(f["path"]), "work_start": -1, "status": "Ожидание", "unique_info": unique_info}
            jobs.append(job)

        env.net_manager.work_queue.add_jobs(jobs, files_send)

    def update_thread(self):
        while True:
            while self.isVisible():
                queue = env.net_manager.work_queue.get_queue(self.machine["id"])
                queue = sorted(queue, key = lambda key: key["index"])
                self.queue = queue
                self.signals.update_queue.emit(queue)

                time.sleep(2)
            time.sleep(1)

    def update_data(self, queue):
        #queue = env.net_manager.work_queue.get_queue(self.machine["id"])
        #queue = sorted(queue, key = lambda key: key["index"])

        self.summary_label.setText(f"Всего: {len(self.queue)}")

        if self.queue == self.old_queue:
            return

        for p in self.job_entries:
            if p.parent() != None:
                p.setParent(None)

        self.job_entries = []

        for i in range(len(queue)):
            job = queue[i]
            if self.enable_job_drop:
                p = JobListEntry(job, queue=self)
            else:
                p = JobListEntry(job, queue=self)
            self.scrollWidgetLayout.insertWidget(i, p)
            self.scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)

            self.job_entries.append(p)
        
        self.old_queue = queue

        self.calculate_full_time()