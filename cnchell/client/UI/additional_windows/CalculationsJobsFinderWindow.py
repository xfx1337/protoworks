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

from UI.widgets.QEasyScroll import QEasyScroll

class CalculationsJobsFinderWindow(QWidget):
    def __init__(self, dc):
        super().__init__()
        self.dc = dc["jobs_equals"]
        self.setStyleSheet(stylesheets.TOOLTIP)
        self.setWindowTitle(f"Обнаружены рассчётные файлы для станков")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.notes_label = QLabel("Ниже будут по очереди представлены рассчитанные файлы под различные станки. Пожалуйста, выбирайте в правой части окна приложения работу, которой этот файл должен соответствовать.")
        self.notes_label.setWordWrap(True)
        self.layout.addWidget(self.notes_label)

        self.h_layout = QHBoxLayout()
        self.layout.addLayout(self.h_layout)

        self.left_frame = QFrame()
        self.left_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.left_frame.setLineWidth(1)
        self.left_frame_layout = QVBoxLayout()
        self.left_frame.setLayout(self.left_frame_layout)

        self.files_left_label = QLabel(f"Не отобранных файлов осталось: 0")
        self.files_left_machine_label = QLabel(f"Не отобранных под текущий станок файлов осталось: 0")
        self.current_machine_label = QLabel(f"Станок, под который сейчас выбираются файлы: ")
        self.current_machine_id_label = QLabel(f"ID станка, под который сейчас выбираются файлы: ")
    
        self.left_frame_layout.addWidget(self.files_left_label)
        self.left_frame_layout.addWidget(self.files_left_machine_label)
        self.left_frame_layout.addWidget(self.current_machine_label)
        self.left_frame_layout.addWidget(self.current_machine_id_label)


        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.left_frame)

        self.part_overview = PartOverviewWidget(self)
        self.left_layout.addWidget(self.part_overview)
        self.h_layout.addLayout(self.left_layout)

        self.right_layout = QVBoxLayout()
        self.h_layout.addLayout(self.right_layout)
        self.queue_w = JobSelectWidget(self)
        self.right_layout.addWidget(self.queue_w)

        self.apply_btn = QInitButton("Применить и перейти к следующему", self.apply)
        self.ignore_btn = QInitButton("Проигнорировать и перейти к следующему", self.ignore)

        self.low_h_layout = QHBoxLayout()
        self.low_h_layout.addWidget(self.apply_btn)
        self.low_h_layout.addWidget(self.ignore_btn)

        self.layout.addLayout(self.low_h_layout)

        self.cur_machine = env.net_manager.machines.get_machine(list(self.dc.keys())[0])

        self.first = True
        self.show_next()

    def apply(self):
        job_id = -1
        for i in range(len(self.queue_w.job_entries)):
            if self.queue_w.job_entries[i].selected:
                job_id = self.queue_w.job_entries[i].job["id"]

        if job_id == -1:
            utils.message("Не выбрана работа.")
            return
        
        self.job = env.net_manager.work_queue.get_job_by_id(job_id)

        file_path = os.path.join(env.config_manager["path"]["calculation_path"], "Checked", self.part_overview.filename)
        files = []
        self.job["unique_info"]["job_send_pre_calculated_filename"] = utils.get_unique_id()
        self.job["unique_info"]["job_pre_calculated_filename"] = self.part_overview.filename
        self.job["unique_info"]["job_pre_calculated"] = True
        self.job["unique_info"]["job_pre_calculated_machine"] = self.cur_machine["id"]

        self.job["work_time"] = env.machine_utils.calculate_job_time_by_file(file_path)

        files.append({self.job["unique_info"]["job_send_pre_calculated_filename"]: file_path})
        if self.job["status"] == "Ошибка. Отсутствует файл расчёта для станка.":
            self.job["status"] = "В ожидании"
        
        env.net_manager.work_queue.overwrite_job_files(self.job["id"], self.job, files)
        utils.message("Отправлено", tittle="Оповещение")
        os.remove(file_path)
        self.show_next()

    def ignore(self):
        file_path = os.path.join(env.config_manager["path"]["calculation_path"], "Checked", self.part_overview.filename)
        os.remove(file_path)
        self.show_next()

    def calculate_summary(self):
        files_left = 0
        files_left_machine = 0
        machine_name = self.cur_machine["name"]
        machine_id = self.cur_machine["id"]

        for m in self.dc.keys():
            for p in self.dc[m].keys():
                if m == str(self.cur_machine["id"]):
                    files_left_machine += 1
                files_left += 1

        self.files_left_label.setText(f"Не отобранных файлов осталось: {files_left}")
        self.files_left_machine_label.setText(f"Не отобранных под текущий станок файлов осталось: {files_left_machine}")
        self.current_machine_label.setText(f"Станок, под который сейчас выбираются файлы: {machine_name}")
        self.current_machine_id_label.setText(f"ID станка, под который сейчас выбираются файлы: {machine_id}")

    def show_next(self):
        if not self.first:
            parts = self.dc[str(self.cur_machine["id"])]
            del self.dc[str(self.cur_machine["id"])][list(parts.keys())[0]]
        if len(self.dc[str(self.cur_machine["id"])].keys()) == 0:
            del self.dc[str(self.cur_machine["id"])]
            if len(self.dc.keys()) > 0:
                self.cur_machine = env.net_manager.machines.get_machine(list(self.dc.keys())[0])
            else:
                utils.message("Файлы распределены", tittle="Оповещение")
                self.hide()
                del self
                return

        self.first = False

        self.calculate_summary()
        self.part_overview.update_data(self.dc[str(self.cur_machine["id"])][list(self.dc[str(self.cur_machine["id"])].keys())[0]])
        self.queue_w.update_data(self.dc[str(self.cur_machine["id"])][list(self.dc[str(self.cur_machine["id"])].keys())[0]])

class PartOverviewWidget(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.part_id = -1

        self.filename_label = QLabel("Обнаруженный файл: ")
        self.pre_calculated_machine_label = QLabel("Станок, под который рассчитан файл: ")
        self.pre_calculated_machine_id_label = QLabel("ID станка, под который рассчитан файл: ")
        self.part_id_label = QLabel("ID детали: ")
        self.part_name_label = QLabel("Название детали: ")

        self.layout.addWidget(self.filename_label)
        self.layout.addWidget(self.pre_calculated_machine_label)
        self.layout.addWidget(self.pre_calculated_machine_id_label)
        self.layout.addWidget(self.part_id_label)
        self.layout.addWidget(self.part_name_label)
    
    def update_data(self, dc):
        self.part_id = -1
        self.part_name = "Нет"
        try:
            self.part_id = dc[0]["part"]["part_id"]
            self.part_name = dc[0]["part"]["part_name"]
        except:
            pass
        self.filename = dc[0]["part"]["filename"]
        self.pre_calculated_machine_id = self.parent.cur_machine["id"]
        self.pre_calculated_machine_name = self.parent.cur_machine["name"]

        self.filename_label.setText(f"Обнаруженный файл: {self.filename}")
        self.pre_calculated_machine_label.setText(f"Станок, под который рассчитан файл: {self.pre_calculated_machine_name}")
        self.pre_calculated_machine_id_label.setText(f"ID станка, под который рассчитан файл: {self.pre_calculated_machine_id}")
        self.part_id_label.setText(f"ID детали: {self.part_id}")
        self.part_name_label.setText(f"Название детали: {self.part_name}")

class JobSelectWidget(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.jobs = []

        self.job_entries = []
    
        self.scrollable = QEasyScroll()
        self.scrollWidgetLayout = self.scrollable.scrollWidgetLayout
        self.scrollWidget = self.scrollable.scrollWidget

        self.layout.addWidget(self.scrollable)
    
    def update_data(self, dc):
        for i in range(len(self.job_entries)):
            if self.job_entries[i].parent() != None:
                self.job_entries[i].setParent(None)
            del self.job_entries[i]
        self.jobs = []

        for i in range(len(dc)):
            job = dc[i]
            self.jobs.append(job["job"])
            p = JobListEntry(job["job"], drag_enable=False, enable_select=True, select_callback=self.select_callback)
            self.scrollWidgetLayout.insertWidget(i, p)
            self.scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)

            self.job_entries.append(p)

    def select_callback(self, id):
        for i in range(len(self.job_entries)):
            if self.job_entries[i].selected and self.job_entries[i].job["id"] != id:
                self.job_entries[i].selected = False
                self.job_entries[i].check_selected()
                self.job_entries[i].select_btn.setText("Выбрать")