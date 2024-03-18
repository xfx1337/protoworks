# 0. Информация о проекте
# 1. Менеджер деталей
# 2. Утилиты
# 3. Подготовка деталей к печати/фрезеровке
# 4. Просмотр ТЗ, печать ТЗ на серверном пк
# 5. Задачи
# 6. Открыть аудит действий
# 7. 

import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QWidget, QSplitter, QLabel, QMessageBox, QCalendarWidget
from PySide6.QtCore import QTimer

from UI.widgets.QUserInput import QUserInput
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QDoubleLabel import QDoubleLabel

from UI.stylesheets import *

from environment.environment import Environment
env = Environment()

import utils

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

class PartsManagerView(QFrame):
    def __init__(self, project):
        super().__init__()
        self.project = project

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()

        self.label = QLabel("Менеджер деталей")
        self.label.setFixedSize(self.label.sizeHint())
        self.layout.addWidget(self.label)

        self.create_part = QInitButton("Создать деталь", callback=self.create_part)
        self.create_part_array = QInitButton("Создать множество деталей", callback=self.create_part_array)
        self.view_parts = QInitButton("Список деталей", callback=self.view_parts)

        self.layout.addWidget(self.create_part)
        self.layout.addWidget(self.create_part_array)
        self.layout.addWidget(self.view_parts)

        self.setLayout(self.layout)
    
    def create_part(self):
        pass

    def create_part_array(self):
        pass
    
    def view_parts(self):
        pass

class Utilities(QFrame):
    def __init__(self, project):
        super().__init__()
        self.project = project

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()

        self.label = QLabel("Утилиты")
        self.label.setFixedSize(self.label.sizeHint())
        self.layout.addWidget(self.label)

        self.open_export_project = QInitButton("Экспорт проекта", callback=self.export_project)
        self.open_export_media = QInitButton("Экспорт медиа проекта", callback=self.export_media)
        self.open_printer = QInitButton("Чертежи и печать", callback=self.open_blueprints)

        self.layout.addWidget(self.open_export_project)
        self.layout.addWidget(self.open_export_media)
        self.layout.addWidget(self.open_printer)

        self.setLayout(self.layout)

    def export_project(self):
        pass
    
    def export_media(self):
        pass
    
    def open_blueprints(self):
        pass

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

        self.cnchell_btn = QInitButton("Открыть CNCHell", callback=self.open_cnchell)
        self.machines_view_btn = QInitButton("Станки", callback=self.open_machines)
        self.terminal_btn = QInitButton("Открыть терминал", callback=self.open_terminal)
        self.distribute_btn = QInitButton("Распределить детали по станкам", callback=self.open_distribute_wnd)
        self.export_current_work_info = QInitButton("Экспортировать информацию о работе станков", callback=self.export_work_info)
        self.print_current_work_info = QInitButton("Печать информации о работе станков", callback=self.print_current_work_info)

        self.layout.addWidget(self.cnchell_btn)
        self.layout.addWidget(self.machines_view_btn)
        self.layout.addWidget(self.terminal_btn)
        self.layout.addWidget(self.distribute_btn)
        self.layout.addWidget(self.export_current_work_info)
        self.layout.addWidget(self.print_current_work_info)

        self.setLayout(self.layout)

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

class TechTaskMenu(QFrame):
    def __init__(self, project):
        super().__init__()
        self.project = project

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()

        self.label = QLabel("Техническое задание")
        self.label.setFixedSize(self.label.sizeHint())
        self.layout.addWidget(self.label)

        self.open_tt_btn = QInitButton("Открыть ТЗ", callback=self.open_tt)
        self.print_tt_btn = QInitButton("Печать ТЗ", callback=self.print_tt)

        self.layout.addWidget(self.open_tt_btn)
        self.layout.addWidget(self.print_tt_btn)

        self.setLayout(self.layout)

    def open_tt(self):
        pass

    def print_tt(self):
        pass

class TasksMenu(QFrame):
    def __init__(self, project):
        super().__init__()
        self.project = project

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()

        self.label = QLabel("Задачи")
        self.label.setFixedSize(self.label.sizeHint())
        self.layout.addWidget(self.label)

        self.create_task_btn = QInitButton("Создать задачу", callback=self.create_task)
        self.tasks_list = QLabel("Здесь будет список задач")

        self.layout.addWidget(self.create_task_btn)
        self.layout.addWidget(self.tasks_list)

        self.setLayout(self.layout)

    def create_task(self):
        pass

class AuditView(QFrame):
    def __init__(self, project):
        super().__init__()
        self.project = project

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()

        self.label = QLabel("Аудит")
        self.label.setFixedSize(self.label.sizeHint())
        self.layout.addWidget(self.label)

        self.open_audit = QInitButton("Открыть аудит действий", callback=self.open_audit)
        self.audit_list = QLabel("Здесь будет укороченный список аудита")

        self.layout.addWidget(self.open_audit)
        self.layout.addWidget(self.audit_list)

        self.setLayout(self.layout)

    def open_audit(self):
        pass

class ProjectView(QWidget):
    def __init__(self, project):
        super().__init__()

        self.project = project

        self.setWindowTitle("Просмотр проекта: " + self.project["name"])
        self.setWindowIcon(env.templates_manager.icons["proto"])
        self.setFixedSize(QSize(800, 800))

        #self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.layout = QHBoxLayout()

        self.l_side = QVBoxLayout()

        self.project_info = ProjectInfo(self.project)
        self.l_side.addWidget(self.project_info)

        self.parts_manager = PartsManagerView(self.project)
        self.l_side.addWidget(self.parts_manager)

        self.utilities = Utilities(self.project)
        self.l_side.addWidget(self.utilities)


        self.r_side = QVBoxLayout()

        self.machines_work_menu = MachinesWorkMenu(self.project)
        self.r_side.addWidget(self.machines_work_menu)

        self.tt_menu = TechTaskMenu(self.project)
        self.r_side.addWidget(self.tt_menu)

        self.tasks_menu = TasksMenu(self.project)
        self.r_side.addWidget(self.tasks_menu)

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