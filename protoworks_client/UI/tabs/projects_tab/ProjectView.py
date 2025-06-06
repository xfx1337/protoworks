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

from UI.part_manager.CreatePartView import CreatePartView
from UI.part_manager.AutoPartsCreationWindow import AutoPartsCreationWindow
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
        self.auto_create_parts_btn = QInitButton("Автоматическое создание деталей", callback=self.auto_create_parts)
        self.view_parts = QInitButton("Менеджер деталей", callback=self.view_parts)
        self.cnchell_btn = QInitButton("Открыть CNCHell", callback=self.open_cnchell)

        #self.layout.addWidget(self.create_part)
        #self.layout.addWidget(self.create_part_array)
        self.layout.addWidget(self.auto_create_parts_btn)
        self.layout.addWidget(self.view_parts)
        #self.layout.addWidget(self.cnchell_btn)

        self.setLayout(self.layout)
    
    def open_cnchell(self):
        pass

    def auto_create_parts(self):
        self.wnd_a = AutoPartsCreationWindow(self.project)
        self.wnd_a.show()

    def create_part(self):
        self.wnd_c = CreatePartView(self.project)
        self.wnd_c.show()

    def create_part_array(self):
        pass
    
    def view_parts(self):
        self.wnd_v = PartsListView(self.project)
        self.wnd_v.show()

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

        self.add_tt_btn = QInitButton("Добавить ТЗ", callback=self.add_tt_btn)
        self.open_tt_btn = QInitButton("Открыть ТЗ", callback=lambda: self.use_tt(callback_on_choose=self.open_tt_file))
        self.print_tt_btn = QInitButton("Печать ТЗ на сервере", callback=lambda: self.use_tt(callback_on_choose=self.print_tt_file))

        self.layout.addWidget(self.add_tt_btn)
        self.layout.addWidget(self.open_tt_btn)
        self.layout.addWidget(self.print_tt_btn)

        self.setLayout(self.layout)

    def add_tt_btn(self):
        self.ask_for_tt = QAskForFilesDialog("Выберите файлы, которые будут загружены как ТЗ", callback_yes=self.upload_tt_handler)
        self.ask_for_tt.show()

    def use_tt(self, callback_on_choose):
        local_path = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"])
        local_doc_path = os.path.join(local_path, "МАТЕРИАЛЫ-PW")
        materials_on_pc = env.file_manager.get_files_list(local_doc_path)
        materials_server = env.net_manager.materials.get_materials(self.project["id"], MATERIAL_TECH_TASK)

        server_doc_path = os.path.join(self.project["server_path"], "МАТЕРИАЛЫ-PW")

        files_pc_relative = []
        files_server_relative = []
        for f in materials_on_pc:
            files_pc_relative.append(f.relative(local_doc_path))
        for f in materials_server:
            files_server_relative.append(utils.remove_path(server_doc_path, f["path"]))
        
        files = utils.common_elements(files_pc_relative, files_server_relative)

        show_tt = QSelectOneFromList("Выберите из списка", files, callback=callback_on_choose)
        show_tt.show()

    def open_tt_file(self, rel_path):
        path = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"])
        path = os.path.join(path, "МАТЕРИАЛЫ-PW")
        path = os.path.join(path, rel_path)
        os.startfile(path)

    def print_tt_file(self, rel_path):
        path = os.path.join(self.project["server_path"], "МАТЕРИАЛЫ-PW")
        path = os.path.join(path, rel_path)
        env.net_manager.hardware.paper_print(path)
    
    def upload_tt_handler(self, files):
        name = self.project["name"]
        pro = Progress()
        server_path = os.path.join(self.project["server_path"], "МАТЕРИАЛЫ-PW")
        local_project_path = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"])
        local_path = os.path.join(local_project_path, "МАТЕРИАЛЫ-PW")


        files_pathes_server = []
        files_copy = {}
        files_send = []
        for f in files:
            path_docs = os.path.join(local_path, f.split("\\")[-1])
            files_send.append(path_docs)
            files_copy[f] =  path_docs
            files_pathes_server.append(os.path.join(server_path, f.split("\\")[-1]))

        project_data = ProjectData(self.project)
        fn_copy = lambda: (env.file_manager.copy_files(files_copy))
        fn_send = lambda: (env.net_manager.files.send_files(local_project_path, server_path, pro, additional_data_to_send=project_data, files_only=files_send))
        func_check_update = lambda: env.net_manager.files.after_project_update(self.project["id"])
        func_add_materials = lambda: (env.net_manager.materials.add_materials_by_files(self.project["id"], files_pathes_server, MATERIAL_TECH_TASK))
        env.task_manager.append_task([fn_copy, fn_send, func_add_materials, func_check_update],
        f"[{name}] Отправка ТЗ на сервер", progress=pro)

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
        self.setWindowIcon(env.templates_manager.icons["proto"])
        #self.setFixedSize(QSize(800, 800))

        #self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.layout = QHBoxLayout()

        self.l_side = QVBoxLayout()

        self.project_info = ProjectInfo(self.project)
        self.l_side.addWidget(self.project_info)

        self.parts_manager = PartsManagerView(self.project)
        self.l_side.addWidget(self.parts_manager)

        #self.utilities = Utilities(self.project)
        #self.l_side.addWidget(self.utilities)


        self.r_side = QVBoxLayout()
        self.tt_menu = TechTaskMenu(self.project)
        self.r_side.addWidget(self.tt_menu)

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