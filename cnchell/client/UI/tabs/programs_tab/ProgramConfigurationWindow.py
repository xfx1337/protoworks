from PySide6.QtCore import QSize, Qt
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QTableWidget, QTableWidgetItem, QFileDialog, QApplication

import os, shutil
import subprocess
import utils

from environment.environment import Environment
env = Environment()

from environment.file_manager.File import File

from environment.task_manager.Progress import Progress

import UI.stylesheets as stylesheets
from UI.widgets.QClickableLabel import QClickableLabel
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QPathInput import QPathInput
from UI.widgets.QUserInput import QUserInput
from UI.widgets.QDoubleLabel import QDoubleLabel
from UI.widgets.QAreUSureDialog import QAreUSureDialog

from UI.tabs.machines_tab.EditSlaveWnd import EditSlaveWnd

from UI.widgets.QYesOrNoDialog import QYesOrNoDialog
from UI.widgets.QFilesListSureDialog import QFilesListSureDialog
from UI.widgets.QAskForNumberDialog import QAskForNumberDialog
from UI.widgets.QEasyScroll import QEasyScroll
from UI.widgets.QAskForFilesDialog import QAskForFilesDialog

import defines

from PySide6.QtCore import Signal, QObject

from environment.file_manager.ZipDataAdditionalTypes import ProgramConfigurations 


class ProgramConfigurationWindow(QWidget):
    def __init__(self, program):
        super().__init__()

        self.program = program

        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        self.setWindowTitle(f"Конфигурирование программы")

        self.setStyleSheet(stylesheets.TOOLTIP)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.h_layout = QHBoxLayout()
        self.layout = QVBoxLayout()
        self.layout2 = QVBoxLayout()

        self.h_layout.addLayout(self.layout, 50)
        #self.h_layout.addLayout(self.layout2, 50)
        self.main_layout.addLayout(self.h_layout)
        
        program_name = self.program["program_user_alias"]
        program_code_name = self.program["program_name"]
        self.program_label = QLabel(f"Название программы: {program_name}")
        self.program_code_name = QLabel(f"Кодовое название программы: {program_code_name}")
        self.notes_label = QLabel("Укажите все данные для того, что бы у вас была возможность синхронизовать конфигурации программы с сервером и другими пользователями")
        self.notes_label.setWordWrap(True)

        self.layout.addWidget(self.program_label)
        self.layout.addWidget(self.program_code_name)
        self.layout.addWidget(self.notes_label)

        self.program_exe_path_btn = QInitButton("Выбрать файл запуска программы(.exe)", callback=self.set_program_exe_path)
        self.program_exe_path_show = QLabel("Путь файла запуска: Нет")

        self.program_exe_path = None

        self.layout.addWidget(self.program_exe_path_btn)
        self.layout.addWidget(self.program_exe_path_show)

        self.d_frame = QFrame()
        self.d_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.d_frame.setLineWidth(1)
        self.d_layout = QVBoxLayout()
        
        self.dirs_label = QLabel("Ниже укажите пути папок на вашем компьютере")

        self.d_scrollable = QEasyScroll()
        self.d_scrollWidgetLayout = self.d_scrollable.scrollWidgetLayout
        self.d_scrollWidget = self.d_scrollable.scrollWidget

        self.d_layout.addWidget(self.dirs_label)
        self.d_layout.addWidget(self.d_scrollable)
        self.d_frame.setLayout(self.d_layout)
        self.layout.addWidget(self.d_frame)


        self.save_btn = QInitButton("Сохранить", callback=self.save)
        self.main_layout.addWidget(self.save_btn)

        self.dirs = []
        self.dir_entries = []

        try:
            data = env.db.configs.get_configs_data(self.program["program_name"])
            if "program_exe_path" in data:
                if data["program_exe_path"] == None:
                    self.program_exe_path_show.setText("Путь файла запуска: Нет")
                else:
                    self.program_exe_path_show.setText("Путь файла запуска: " + data["program_exe_path"])
                self.program_exe_path = data["program_exe_path"]
        except:
            utils.message("Не найдены конфигурационные файлы. Пожалуйста, обновите данные во вкладке 'Программы'")
            self.close()
            return

        self.update_dirs()
    
    def save(self):
        data = env.db.configs.get_configs_data(self.program["program_name"])
        data["program_exe_path"] = self.program_exe_path
        for i in range(len(self.dir_entries)):
            p = self.dir_entries[i].get_path()
            if p != None:
                self.dirs[i]["real_path"] = p

        env.db.configs.set_configs(self.program["program_name"], dirs=self.dirs, program_exe_path=self.program_exe_path)
        utils.message("Записано", tittle="Уведомление")
        self.close()
        

    def set_program_exe_path(self):
        self.dlg = QAskForFilesDialog("Выберите файлы", callback_yes=self.exe_file_chosen, only_one_file=True)
        self.dlg.exec()
    def exe_file_chosen(self, file):
        self.program_exe_path = file
        self.program_exe_path_show.setText(f"Путь файла запуска: {self.program_exe_path}")
    
    def update_dirs(self):
        data = env.db.configs.get_configs_data(self.program["program_name"])

        self.dirs = data["dirs"]

        for p in self.dir_entries:
            if p.parent() != None:
                p.setParent(None)

        self.dir_entries = []

        for i in range(len(self.dirs)):
            p = DirEntry(self.dirs[i])
            self.d_scrollWidgetLayout.insertWidget(i, p)
            self.d_scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)

            self.dir_entries.append(p)

class DirEntry(QFrame):
    def __init__(self, dirx, del_callback=None):
        super().__init__()
        self.dir = dirx

        self.path = None
        self.desc = ""
        self.path_name = ""

        if "desc" in self.dir:
            self.desc = self.dir["desc"]
        if "path" in self.dir:
            self.path_name = self.dir["path"]
        if "real_path" in self.dir:
            self.path = self.dir["real_path"]

        self.del_callback = del_callback

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)
        
        self.layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.dir_label = QLabel(self.path_name)
        self.desc_label = QLabel(self.desc)

        self.layout.addWidget(self.dir_label, 99)

        self.path_input = QPathInput("Директория")
        if self.path != None:
            self.path_input.set_path(self.path)

        self.main_layout.addLayout(self.layout)
        self.main_layout.addWidget(self.desc_label)
        self.main_layout.addWidget(self.path_input)
    
    def get_path(self):
        return self.path_input.path

