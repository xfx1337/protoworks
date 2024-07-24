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

from UI.tabs.machines_tab.JobCalculationWindow import JobCalculationWindow

import defines

from PySide6.QtCore import Signal, QObject

from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag

from UI.widgets.QAskForNumberDialog import QAskForNumberDialog

class JobListEntry(QFrame):
    def __init__(self, job, drag_enable=True, queue=None, enable_select=False, select_callback=None):
        super().__init__()
        self.job = job
        self.queue = queue

        self.enable_select = enable_select
        self.select_callback = select_callback

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
            job_project_name = env.net_manager.projects.get_project_info(job_project_id)["name"]

        job_pre_calculated = "Нет"
        if "job_pre_calculated" in unique_info and unique_info["job_pre_calculated"]:
            job_pre_calculated = "Да"
        
        job_pre_calculated_machine_name = "Нет"
        if "job_pre_calculated_machine" in unique_info:
            job_pre_calculated_machine = unique_info["job_pre_calculated_machine"]
            if job_pre_calculated_machine != -1:
                try:
                    job_pre_calculated_machine_name = env.net_manager.machines.get_machine(job_pre_calculated_machine)["name"]
                except:
                    job_pre_calculated_machine_name = "Недоступно."

        #if "job_project_name" in unique_info:
        #    job_project_name = unique_info["job_project_name"]

        job_count_done = unique_info["job_count_done"]
        job_count_need = unique_info["job_count_need"]

        need = job_count_need-job_count_done

        self.id_label = QLabel(f"ID: {job_id}")
        self.name_label = QLabel(f"Название: {job_name}")
        self.filename_label = QLabel(f"Название файла: {job_filename}")
        self.part_id_label = QLabel(f"ID детали: {job_part_id}")
        self.part_name_label = QLabel(f"Название детали: {job_part_name}")
        self.count_need_label = QLabel(f"Требуемое количество: {job_count_need}")
        self.count_done_label = QLabel(f"Количество выполненных: {job_count_done}")
        self.project_name_label = QLabel(f"Название проекта: {job_project_name}")
        self.job_pre_calculated_label = QLabel(f"Рассчитана под станок: {job_pre_calculated}")
        self.job_pre_calculated_machine_label = QLabel(f"Рассчитана под станок(название): {job_pre_calculated_machine_name}")
        self.work_time_label = QLabel(f"Время работы, рассчитанное под станок: {utils.seconds_to_str(work_time*need)}")
        
        if work_start >= 0:
            self.work_start_label = QLabel(f"Время начала работы: {utils.time_by_unix(work_start)}")
        else:
            self.work_start_label = QLabel(f"Время начала работы: Не начата.")

        self.status_label = QLabel(f"Состояние: {status}")

        self.layout.addWidget(self.id_label)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.filename_label)
        self.layout.addWidget(self.part_id_label)
        self.layout.addWidget(self.part_name_label)
        self.layout.addWidget(self.count_need_label)
        self.layout.addWidget(self.count_done_label)
        self.layout.addWidget(self.project_name_label)
        self.layout.addWidget(self.job_pre_calculated_label)
        self.layout.addWidget(self.job_pre_calculated_machine_label)
        self.layout.addWidget(self.work_time_label)
        self.layout.addWidget(self.work_start_label)
        self.layout.addWidget(self.status_label)

        self.menu = QMenu(self)
        self.menu.setStyleSheet(stylesheets.DEFAULT_BORDER_STYLESHEET)
        action_redistribution = self.menu.addAction("Отправить на перераспределение(снять с очереди станка)")
        action_delete_job = self.menu.addAction("Удалить задачу")
        action_make_first = self.menu.addAction("Установить как следующую на выполнение")
        action_right_now = self.menu.addAction("Отменить текущую и запустить данную прямо сейчас")
        action_calculate = self.menu.addAction("Пересчитать")
        action_count_need = self.menu.addAction("Указать требуемое количество")
        action_count_done = self.menu.addAction("Указать количество выполненных")

        action_redistribution.triggered.connect(self.redistribution)
        action_delete_job.triggered.connect(self.delete_job)
        action_make_first.triggered.connect(self.make_first)
        action_right_now.triggered.connect(self.make_right_now)
        action_calculate.triggered.connect(self.calculate)
        action_count_need.triggered.connect(self.set_count_need)
        action_count_done.triggered.connect(self.set_count_done)

        self.setLayout(self.layout)

        if self.enable_select:
            self.select_btn = QInitButton("Выбрать", callback=self.__select)
            self.layout.addWidget(self.select_btn)

        #drag
        self.selected = False
        self.dragStartPosition = self.pos()
        self.drag_enable = drag_enable

    def __select(self):
        self.select_btn.setText("Отменить выбор")
        self.selected = not self.selected
        self.check_selected()
        if self.selected == True:
            self.select_callback(self.job["id"])
        else:
            self.select_btn.setText("Выбрать")

    def set_count_need(self):
        dlg = QAskForNumberDialog(text = "Требуемое количество:", title="Выбор")
        dlg.exec()
        answer = dlg.answer
        if answer != None:
            self.job["unique_info"]["job_count_need"] = int(answer)
            env.net_manager.work_queue.overwrite_job(self.job["id"], self.job)
            self._update(self.job)

    def set_count_done(self):
        dlg = QAskForNumberDialog(text = "Имеющееся количество:", title="Выбор")
        dlg.exec()
        answer = dlg.answer
        if answer != None:
            self.job["unique_info"]["job_count_done"] = int(answer)
            env.net_manager.work_queue.overwrite_job(self.job["id"], self.job)
            self._update(self.job)
        
        if self.job["unique_info"]["job_count_done"] == self.job["unique_info"]["job_count_need"] and self.job["unique_info"]["job_count_need"] != 0:
            self.delete_job()

    def calculate(self):
        if self.job["status"] == "В работе":
            utils.message("Невозможно.")
            return
        self.calculate_job_wnd = JobCalculationWindow(self.job, change_callback=self._update, queue=self.queue)
        self.calculate_job_wnd.show()

    def _update(self, job):
        self.job = job
        
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
            job_project_name = env.net_manager.projects.get_project_info(job_project_id)["name"]

        job_pre_calculated = "Нет"
        if "job_pre_calculated" in unique_info and unique_info["job_pre_calculated"]:
            job_pre_calculated = "Да"
        
        job_pre_calculated_machine_name = "Нет"
        if "job_pre_calculated_machine" in unique_info:
            job_pre_calculated_machine = unique_info["job_pre_calculated_machine"]
            if job_pre_calculated_machine != -1:
                try:
                    job_pre_calculated_machine_name = env.net_manager.machines.get_machine(job_pre_calculated_machine)["name"]
                except:
                    job_pre_calculated_machine_name = "Недоступно."

        job_count_done = unique_info["job_count_done"]
        job_count_need = unique_info["job_count_need"]

        #if "job_project_name" in unique_info:
        #    job_project_name = unique_info["job_project_name"]

        need = job_count_need-job_count_done

        self.id_label.setText(f"ID: {job_id}")
        self.name_label.setText(f"Название: {job_name}")
        self.filename_label.setText(f"Название файла: {job_filename}")
        self.part_id_label.setText(f"ID детали: {job_part_id}")
        self.part_name_label.setText(f"Название детали: {job_part_name}")
        self.project_name_label.setText(f"Название проекта: {job_project_name}")
        self.job_pre_calculated_label.setText(f"Рассчитана под станок: {job_pre_calculated}")
        self.job_pre_calculated_machine_label.setText(f"Рассчитана под станок(название): {job_pre_calculated_machine_name}")
        self.work_time_label.setText(f"Время работы, рассчитанное под станок: {utils.seconds_to_str(work_time*need)}")
        
        self.count_need_label.setText(f"Требуемое количество: {job_count_need}")
        self.count_done_label.setText(f"Количество выполненных: {job_count_done}")

        if work_start >= 0:
            self.work_start_label.setText(f"Время начала работы: {utils.time_by_unix(work_start)}")
        else:
            self.work_start_label.setText(f"Время начала работы: Не начата.")

        self.status_label.setText(f"Состояние: {status}")


    def mouseMoveEvent(self, event):
        if not self.drag_enable:
            event.accept()
            return
        if not event.buttons() == Qt.LeftButton:
            return
        if ((event.pos() - self.dragStartPosition).manhattanLength()
            < QApplication.startDragDistance()):
            return
        self.selected = True
        self.check_selected()
        drag = QDrag(self)
        drag.setPixmap(env.templates_manager.icons["drag2"].pixmap(256,256))
        mimeData = QMimeData()
        mimeData.setText(str(self.job["id"]))
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - self.rect().topLeft())

        dropAction = drag.exec_(Qt.CopyAction)
        if self.queue != None:
            self.queue.delete_job(self.job["id"])

    def mousePressEvent(self, e):
        if not self.drag_enable:
            e.accept()
            return
        if e.buttons() == Qt.LeftButton:
            if self.selected:
                self.dragStartPosition = e.pos()
            self.selected = not self.selected
            self.check_selected()

    def check_selected(self):
        if self.enable_select or self.drag_enable:
            if self.selected:
                self.setStyleSheet(stylesheets.SELECTED_STYLESHEET)
            else:
                self.setStyleSheet(stylesheets.UNSELECTED_STYLESHEET)


    def make_right_now(self):
        self.dlg = QYesOrNoDialog("Вы действительно хотите отменить текущую работу?")
        self.dlg.exec()
        if not self.dlg.answer:
            return

        jobs = env.net_manager.work_queue.get_queue(self.job["machine_id"])
        self.running_job = None
        for j in jobs:
            if j["status"] == "В работе":
                self.running_job = j

        if self.running_job != None:
            self.running_job["status"] = "Ожидание"
            env.net_manager.machines.cancel_job(self.running_job["machine_id"])
            env.net_manager.work_queue.overwrite_job(self.running_job["id"], self.running_job)
        env.net_manager.work_queue.move_job(self.job["index"], 0, self.job["machine_id"])


    def make_first(self):
        jobs = env.net_manager.work_queue.get_queue(self.job["machine_id"])
        self.running_job = None
        for j in jobs:
            if j["status"] == "В работе":
                self.running_job = j

        if self.running_job == None:
            env.net_manager.work_queue.move_job(self.job["index"], 0, self.job["machine_id"])
        else:
            env.net_manager.work_queue.move_job(self.job["index"], 1, self.job["machine_id"])

    def redistribution(self):
        self.dlg = QYesOrNoDialog("Вы действительно хотите снять задачу со станка?")
        self.dlg.exec()
        if not self.dlg.answer:
            return
        env.net_manager.work_queue.move_job(self.job["index"], -1, self.job["machine_id"])
        self.job = env.net_manager.work_queue.get_job_by_id(self.job["id"])
        self.job["machine_id"] = -1
        env.net_manager.work_queue.overwrite_job(self.job["id"], self.job)

    def delete_job(self):
        if self.job["status"] == "В работе":
            utils.message("Нельзя удалить работу во время её выполнения")
            return

        self.dlg = QYesOrNoDialog("Вы действительно хотите удалить задачу?")
        self.dlg.exec()
        if not self.dlg.answer:
            return
        job_now = env.net_manager.work_queue.get_job_by_id(self.job["id"])
        env.net_manager.work_queue.delete_jobs([self.job["index"]], self.job["machine_id"])
        self.hide()
        del self
    

    def contextMenuEvent(self, event):
        self.menu.exec(event.globalPos())
