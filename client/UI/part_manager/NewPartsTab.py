from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox, QProgressBar
from PySide6.QtCore import QTimer
from PySide6.QtGui import QShortcut, QKeySequence

from PySide6.QtCore import Signal, QObject

import os

import utils
from defines import *

import UI.stylesheets as stylesheets
from UI.widgets.QClickableLabel import QClickableLabel
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QListEntry import QListEntry
from UI.widgets.QDictShow import QDictShow
from UI.widgets.QPathInput import QPathInput
from UI.widgets.QChooseManyCheckBoxes import QChooseManyCheckBoxes
from UI.widgets.QFilesListSureDialog import QFilesListSureWidget
from UI.widgets.QEasyScroll import QEasyScroll


from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

from environment.task_manager.statuses import *

import time

from UI.part_manager.NewPartsCreationProcessWindow import NewPartsCreationProcessWindow


class SettingsFrame(QFrame):
    def __init__(self, callback=None, force_convert=False):
        super().__init__()

        self.callback = callback
        self.force_convert = force_convert

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Доп настройки автоматического создания деталей")
        self.label.setFixedSize(self.label.sizeHint())
        self.layout.addWidget(self.label)

        self.auto_convert_btn = QCheckBox("Автоматически конвертировать файл детали во все форматы")
        self.enable_a3d_convert = QCheckBox("Разрешить конвертирование из a3d")
        self.enable_a3d_convert.setToolTip("Часто приводит к ошибкам из-за недостающих зависимостей.")
        self.setStyleSheet(stylesheets.TOOLTIP)
        self.layout.addWidget(self.auto_convert_btn)
        self.layout.addWidget(self.enable_a3d_convert)
    
        if self.callback != None:
            self.setWindowTitle(f"Настройки конвертации")
            self.setWindowIcon(env.templates_manager.icons["proto"])
            self.apply_btn = QInitButton("Применить", callback=self.on_apply)
            if self.force_convert:
                self.auto_convert_btn.hide()
                self.auto_convert_btn.setChecked(True)
            self.layout.addWidget(self.apply_btn)

    def on_apply(self):
        self.close()
        self.callback(self.get_settings())

    def get_settings(self):
        settings = {
            "auto_convert_all_formats": self.auto_convert_btn.isChecked(),
            "enable_a3d_convert": self.enable_a3d_convert.isChecked()
        }
        return settings

class NewPartsTab(QFrame):
    def __init__(self, project):
        super().__init__()
        self.project = project

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()

        self.label = QLabel("Автоматическое создание новых деталей")
        self.label.setFixedSize(self.label.sizeHint())


        self.files = []

        open_path = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"])
        self.folder_select = QPathInput("Директория исходных файлов", selected_callback = self.update_path, open_path=open_path, limit_dir=open_path)
        self.subfolders_enable_cb = QCheckBox("Проверять подпапки на наличие файлов")
        self.subfolders_enable_cb.setChecked(True)
        self.subfolders_enable_cb.toggled.connect(self.update_path)



        self.folder_select.setStyleSheet(stylesheets.DISABLE_BORDER)
        self.folder_choosing_frame = QFrame()
        self.folder_choosing_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.folder_choosing_frame.setLineWidth(1)
        self.folder_choosing_layout = QVBoxLayout()
        self.folder_choosing_frame.setLayout(self.folder_choosing_layout)
        self.folder_choosing_layout.addWidget(self.folder_select)
        self.folder_choosing_layout.addWidget(self.subfolders_enable_cb)


        
        extensions = []
        for ext in FILE_FORMATS.keys():
            extensions.append(FILE_FORMATS[ext])

        self.extensions = QChooseManyCheckBoxes("Форматы исходных файлов", extensions, checking_callback=self.update_data_files)

        self.files_show = QFilesListSureWidget([], [], "Выберите исходные файлы", "Исходные файлы", "Проигнорировать")


        self.settings_frame = SettingsFrame()
        self.run_btn = QInitButton("Выполнить", callback=self.run_creation)

        self.layout.addWidget(self.label, 10)
        self.layout.addWidget(self.folder_choosing_frame, 10)
        self.layout.addWidget(self.extensions, 20)
        self.layout.addWidget(self.files_show, 50)
        self.layout.addWidget(self.settings_frame, 20)
        self.layout.addWidget(self.run_btn)

        server_parts = env.net_manager.parts.get_parts(self.project["id"])
        self.server_parts_relative = []
        self.server_parts_relative_dc = {}
        for f in server_parts:
            self.server_parts_relative.append(utils.remove_path(self.project["server_path"], f["path"]))
            self.server_parts_relative_dc[utils.remove_path(self.project["server_path"], f["path"])] = f

        self.setLayout(self.layout)

    def run_creation(self):
        if len(self.files_show.files_yes) == 0:
            utils.message("Не выбраны файлы.", tittle="Уведомление")
            return
        self.creation_wnd = NewPartsCreationProcessWindow(self.project, self.files_show.files_yes, self.settings_frame.get_settings())
        self.creation_wnd.show()
        self.parent().close()

    def update_path(self):
        if self.folder_select.path == None:
            return
        if self.subfolders_enable_cb.isChecked():
            self.files = env.file_manager.get_files_list(self.folder_select.path, files_only=True, pw_folders_restriction=True)
        else:
            self.files = env.file_manager.get_files_list(self.folder_select.path, files_only=True, subdirs=False, pw_folders_restriction=True)

        self.files = env.file_manager.files_list_to_dict_list(self.files)

        for f in self.files:
            f["visible"] = True

        self.update_data_files()

    def update_data_files(self):
        extensions = self.extensions.get_selected()
        for f in self.files:
            f["visible"] = True
            ext = f["path"].split(".")[-1]
            if len(extensions) != 0: 
                if ext not in extensions:
                    f["visible"] = False

        self.update_data()

    def update_data(self):
        main_path = self.folder_select.path
        self.files_show.path_dont_show = main_path

        visible_files = []
        for f in self.files:
            if f["visible"]:
                visible_files.append(f)

        
        real_files = []
        local_path = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"])
        for f in visible_files:
            ch_path = utils.remove_path(local_path, f["path"])
            if ch_path not in self.server_parts_relative:
                real_files.append(f)
            else:
                if self.server_parts_relative_dc[ch_path]["status"] == PART_IN_COORDINATION:
                    real_files.append(f)


        self.files_show.files_yes = real_files
        self.files_show.files_no = []
        self.files_show.load_data()
        self.files_show.update()