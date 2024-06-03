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

import defines

from PySide6.QtCore import Signal, QObject

class JobListEntry(QFrame):
    def __init__(self, job):
        super().__init__()
        self.job = job

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()

        unique_info = job["unique_info"]
        status = job["status"]
        work_time = job["work_time"]
        work_start = job["work_start"]

        job_id = job["id"] 


        job_name = "Нет"
        if "job_name" in unique_info:
            job_name = unique_info["job_name"]
        
        job_filename = "Нет"
        if "job_filename" in unique_info:
            job_filename = unique_info["job_filename"]
        
        job_part_id = "Нет"
        if "job_part_id" in unique_info:
            job_part_id = unique_info["job_part_id"]
        
        job_part_name = "Нет"
        if "job_part_name" in unique_info:
            job_part_name = unique_info["job_part_name"]

        job_project_name = "Нет"
        job_project_id = "Нет"
        if "job_project_id" in unique_info:
            job_project_id = unique_info["job_project_id"]
            job_project_name = env.net_manager.projects.get_project_info(job_project_id)

        #if "job_project_name" in unique_info:
        #    job_project_name = unique_info["job_project_name"]

        self.id_label = QLabel(f"ID: {job_id}")
        self.name_label = QLabel(f"Название: {job_name}")
        self.filename_label = QLabel(f"Название файла: {job_filename}")
        self.part_name_label = QLabel(f"Название детали: {job_part_name}")
        self.project_name_label = QLabel(f"Название проекта: {job_project_name}")
        self.work_time_label = QLabel(f"Время работы: {utils.seconds_to_str(work_time)}")
        
        if work_start >= 0:
            self.work_start_label = QLabel(f"Время начала работы: {utils.time_by_unix(work_start)}")
        else:
            self.work_start_label = QLabel(f"Время начала работы: Не начата.")

        self.status_label = QLabel(f"Состояние: {status}")

        self.layout.addWidget(self.id_label)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.filename_label)
        self.layout.addWidget(self.part_name_label)
        self.layout.addWidget(self.project_name_label)
        self.layout.addWidget(self.work_time_label)
        self.layout.addWidget(self.work_start_label)
        self.layout.addWidget(self.status_label)



        self.menu = QMenu(self)
        self.menu.setStyleSheet(stylesheets.DEFAULT_BORDER_STYLESHEET)
        action_redistribution = self.menu.addAction("Отправить на перераспределение(снять с очереди станка)")
        action_delete_job = self.menu.addAction("Удалить задачу")
        action_make_first = self.menu.addAction("Установить как следующую на выполнение")
        action_right_now = self.menu.addAction("Отменить текущую и запустить данную прямо сейчас")

        action_redistribution.triggered.connect(self.redistribution)
        action_delete_job.triggered.connect(self.delete_job)
        

        self.setLayout(self.layout)

    def redistribution(self):
        pass

    def delete_job(self):
        pass

    

    def contextMenuEvent(self, event):
        self.menu.exec(event.globalPos())
