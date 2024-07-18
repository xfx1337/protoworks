# 0. Информация о проекте
# 1. Менеджер деталей
# 2. Утилиты
# 3. Подготовка деталей к печати/фрезеровке
# 4. Просмотр ТЗ, печать ТЗ на серверном пк
# 5. Задачи
# 6. Открыть аудит действий
# 7. 

import os, sys, shutil

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QWidget, QSplitter, QLabel, QMessageBox, QCalendarWidget
from PySide6.QtCore import QTimer

from UI.widgets.QUserInput import QUserInput
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QDoubleLabel import QDoubleLabel

from UI.widgets.QAskForFilesDialog import QAskForFilesDialog
from UI.widgets.QSelectOneFromList import QSelectOneFromList
from UI.widgets.QEasyScroll import QEasyScroll

from UI.stylesheets import *
from UI.part_manager.PartsListView import PartsListView

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

from environment.file_manager.File import File

from environment.file_manager.ZipDataAdditionalTypes import ProjectData

import utils

from defines import *

import time
from datetime import datetime as dt

class ProjectInfo(QFrame):
    def __init__(self, project):
        super().__init__()

        self.project = project

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()

        self.name = QDoubleLabel("Название:", self.project["name"])
        self.deadline = QDoubleLabel("Срок сдачи:", utils.time_by_unix(self.project["time_deadline"]))

        if utils.unix_is_expired(self.project["time_deadline"]):
            self.deadline.setStyleSheet(YELLOW_HIGHLIGHT)

        self.layout.addWidget(self.name)
        self.layout.addWidget(self.deadline)
        
        self.setLayout(self.layout)

class MachinesWorkMenu(QFrame):
    def __init__(self, project):
        super().__init__()
        self.project = project

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()

        self.label = QLabel("Подготовка к печати/фрезеровке")
        self.label.setFixedSize(self.label.sizeHint())
        self.layout.addWidget(self.label)

        self.view_parts_btn = QInitButton("Менеджер деталей", callback=self.view_parts)
        self.machines_view_btn = QInitButton("Станки", callback=self.open_machines)
        self.terminal_btn = QInitButton("Открыть терминал", callback=self.open_terminal)
        self.distribute_btn = QInitButton("Распределить детали по станкам", callback=self.open_distribute_wnd)
        self.export_current_work_info = QInitButton("Экспортировать информацию о работе станков", callback=self.export_work_info)
        self.print_current_work_info = QInitButton("Печать информации о работе станков", callback=self.print_current_work_info)

        self.layout.addWidget(self.view_parts_btn)
        #self.layout.addWidget(self.machines_view_btn)
        #self.layout.addWidget(self.terminal_btn)
        #self.layout.addWidget(self.distribute_btn)
        #self.layout.addWidget(self.export_current_work_info)
        #self.layout.addWidget(self.print_current_work_info)

        self.setLayout(self.layout)

    def view_parts(self):
        self.wnd_v = PartsListView(self.project)
        self.wnd_v.show()

    def open_terminal(self):
        pass

    def print_current_work_info(self):
        pass

    def export_work_info(self):
        pass

    def open_cnchell(self):
        pass

    def open_machines(self):
        pass

    def open_distribute_wnd(self):
        pass


class AuditView(QFrame):
    def __init__(self, project):
        super().__init__()
        self.project = project

        self.entries = []

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()

        self.label = QLabel("Аудит")
        self.label.setFixedSize(self.label.sizeHint())
        self.layout.addWidget(self.label)

        self.audit_info = QLabel("Последние 10 событий")
        self.scrollable = QEasyScroll()
        self.scrollWidgetLayout = self.scrollable.scrollWidgetLayout
        self.scrollWidget = self.scrollable.scrollWidget

        self.layout.addWidget(self.audit_info)
        self.layout.addWidget(self.scrollable)

        self.setLayout(self.layout)

        self.update_data()

    def update_data(self):
        data = env.net_manager.audit.get_project_audit(self.project["id"], 0, 10)

        for e in self.entries:
            if e.parent() != None:
                e.setParent(None)

        self.entries = []

        events = sorted(data, key=lambda key: (-key["date"]))

        for i in range(len(events)):
            event = events[i]
            e = QDoubleLabel(event["event"], utils.time_by_unix(event["date"]))
            self.scrollWidgetLayout.insertWidget(i, e)
            self.scrollWidgetLayout.setAlignment(e, Qt.AlignmentFlag.AlignTop)

            self.entries.append(e)


class ProjectView(QWidget):
    def __init__(self, project):
        super().__init__()

        self.project = project

        self.setWindowTitle("Просмотр проекта: " + self.project["name"])
        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        #self.setFixedSize(QSize(800, 500))

        #self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.layout = QHBoxLayout()

        self.l_side = QVBoxLayout()

        self.project_info = ProjectInfo(self.project)
        self.l_side.addWidget(self.project_info)

        self.machines_work_menu = MachinesWorkMenu(self.project)
        self.l_side.addWidget(self.machines_work_menu)

        self.r_side = QVBoxLayout()

        self.audit_menu = AuditView(self.project)
        self.r_side.addWidget(self.audit_menu)

        self.layout.addLayout(self.l_side, 50)
        self.layout.addLayout(self.r_side, 50)

        self.setLayout(self.layout)

        QTimer.singleShot(10, self.center_window)


    def center_window(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        event.accept()