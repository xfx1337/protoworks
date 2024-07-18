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
from environment.file_manager.ZipDataAdditionalTypes import FilesOverwrite 


class AddProgramWindow(QWidget):
    def __init__(self, change_only=False, program=None):
        super().__init__()

        self.change_only = change_only
        self.program_preset = program

        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        if not self.change_only:
            self.setWindowTitle(f"Добавление программы")
        else:
            self.setWindowTitle("Изменение программы")

        self.setStyleSheet(stylesheets.TOOLTIP)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.h_layout = QHBoxLayout()
        self.layout = QVBoxLayout()
        self.layout2 = QVBoxLayout()

        self.h_layout.addLayout(self.layout, 50)
        self.h_layout.addLayout(self.layout2, 50)
        self.main_layout.addLayout(self.h_layout)
        
        if not self.change_only:
            self.program_name_input = QUserInput("Кодовое название программы на латинице без пробелов:", corner_align=True)
        else:
            program_name = self.program_preset["program_name"]
            self.program_name_input = QLabel(f"Кодовое название программы на латинице без пробелов: {program_name}")

        self.program_name_user_input = QUserInput("Название программы:", corner_align=True)
        if self.change_only:
            # fuck it
            programs_list = env.net_manager.configs.get_sync_data()
            program_user_alias = programs_list[self.program_preset["program_name"]]["program_user_alias"]
            self.program_name_user_input.set_input(program_user_alias)
        self.program_install_path_input = QPathInput("Папка установки программы:")
        self.program_exe_path_btn = QInitButton("Выбрать файл запуска программы(.exe)", callback=self.set_program_exe_path)
        self.program_exe_path_show = QLabel("Путь файла запуска: Нет")
        self.program_name_input.setToolTip("Например 'kompas3d', 'cura', 'fzkviewer'")
        
        self.program_exe_path = None

        self.layout.addWidget(self.program_name_input)
        self.layout.addWidget(self.program_name_user_input)
        self.layout.addWidget(self.program_install_path_input)
        self.layout.addWidget(self.program_exe_path_btn)
        self.layout.addWidget(self.program_exe_path_show)

        self.l_frame = QFrame()
        self.l_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.l_frame.setLineWidth(1)
        self.l_layout = QVBoxLayout()
        self.l_frame.setLayout(self.l_layout)
        self.links_label = QLabel("Ниже можете добавить различные ссылки")
        self.links_label.setToolTip("Например ссылку на скачивание программы")

        self.link_input = QUserInput("Ссылка:", corner_align=True)
        self.link_desc_input = QUserInput("Описание ссылки:", corner_align=True)
        self.add_link_btn = QInitButton("Добавить ссылку", callback=self.add_link)

        self.l_scrollable = QEasyScroll()
        self.l_scrollWidgetLayout = self.l_scrollable.scrollWidgetLayout
        self.l_scrollWidget = self.l_scrollable.scrollWidget

        self.l_layout.addWidget(self.links_label)
        self.l_layout.addWidget(self.link_input)
        self.l_layout.addWidget(self.link_desc_input)
        self.l_layout.addWidget(self.add_link_btn)
        self.l_layout.addWidget(self.l_scrollable)
        self.layout.addWidget(self.l_frame)

        self.d_frame = QFrame()
        self.d_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.d_frame.setLineWidth(1)
        self.d_layout = QVBoxLayout()
        
        self.dirs_label = QLabel("Ниже укажите папки, в которых будет производится поиск конфигураций")
        self.dirs_label.setToolTip("Файлы можно будет указывать лишь из указанных папок(подпапок) и из папки(подпапок) установки")

        self.dir_input = QPathInput("Папка:")
        self.dir_input_name = QUserInput("Кодовое название папки:", corner_align=True)
        self.dir_input_desc = QUserInput("Описание папки: ", corner_align=True)
        self.dir_add_btn = QInitButton("Добавить папку", callback=self.add_dir)

        self.d_scrollable = QEasyScroll()
        self.d_scrollWidgetLayout = self.d_scrollable.scrollWidgetLayout
        self.d_scrollWidget = self.d_scrollable.scrollWidget

        self.d_layout.addWidget(self.dirs_label)
        self.d_layout.addWidget(self.dir_input)
        self.d_layout.addWidget(self.dir_input_name)
        self.d_layout.addWidget(self.dir_input_desc)
        self.d_layout.addWidget(self.dir_add_btn)
        self.d_layout.addWidget(self.d_scrollable)
        self.d_frame.setLayout(self.d_layout)
        self.layout2.addWidget(self.d_frame)


        self.f_frame = QFrame()
        self.f_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.f_frame.setLineWidth(1)
        self.f_layout = QVBoxLayout()
        self.f_frame.setLayout(self.f_layout)
        self.files_label = QLabel("Ниже укажите файлы конфигурации, которые хотите записать на сервер")
        self.add_files_btn = QInitButton("Добавить файлы", callback=self.add_files)

        self.f_scrollable = QEasyScroll()
        self.f_scrollWidgetLayout = self.f_scrollable.scrollWidgetLayout
        self.f_scrollWidget = self.f_scrollable.scrollWidget
    
        self.f_layout.addWidget(self.files_label)
        self.f_layout.addWidget(self.add_files_btn)
        self.f_layout.addWidget(self.f_scrollable)
        self.f_frame.setLayout(self.f_layout)
        self.layout2.addWidget(self.f_frame)

        self.save_btn = QInitButton("Сохранить", callback=self.save)
        self.main_layout.addWidget(self.save_btn)

        self.links = []
        self.files = []
        self.dirs = []

        self.link_entries = []
        self.file_entries = []
        self.dir_entries = []

        if self.change_only:
            data = env.db.configs.get_configs_data(program["program_name"])
            self.links = data["links"]
            self.dirs = data["dirs"]
            self.files = data["files"]
            

            self.update_links()
            self.update_dirs()
            self.update_files()

            self.program_exe_path = data["program_exe_path"]
            self.program_exe_path_show.setText(f"Путь файла запуска: {self.program_exe_path}")
            for d in data["dirs"]:
                if d["path"] == program["program_name"]+"_install":
                    self.program_install_path_input.path = d["real_path"]
                    self.program_install_path_input.set_path(self.program_install_path_input.path)
            for i in range(len(data["dirs"])):
                if data["dirs"][i]["path"] == program["program_name"]+"_install":
                    del data["dirs"][i]
                    break

    def set_program_exe_path(self):
        self.dlg = QAskForFilesDialog("Выберите файлы", callback_yes=self.exe_file_chosen, only_one_file=True)
        self.dlg.exec()
    def exe_file_chosen(self, file):
        self.program_exe_path = file
        self.program_exe_path_show.setText(f"Путь файла запуска: {self.program_exe_path}")

    def save(self):
        if not self.change_only:
            if self.program_name_input.get_input() == "" or self.program_name_user_input.get_input() == "" or self.program_install_path_input.path == None:
                utils.message("Недостаточно данных для создания")
                return
        else:
            if self.program_name_user_input.get_input() == "" or self.program_install_path_input.path == None:
                utils.message("Недостаточно данных для создания")
                return
        
        if self.program_exe_path == None:
            utils.message("Недостаточно данных для создания")
            return
        
        self.dlg = QYesOrNoDialog("Сейчас конфигурации будут перезаписаны. При дальнейшем обновлении у других пользователей будут скачиватся эти конфигурации.")
        self.dlg.exec()
        if not self.dlg.answer:
            event.ignore()
            return

        if not self.change_only:
            self.program = {"name": self.program_name_input.get_input(), "name_user": self.program_name_user_input.get_input()}
        else:
            self.program = {"name": self.program_preset["program_name"], "name_user": self.program_name_user_input.get_input()}

        files = []
        for f in self.files:
            f = File(path=f, f_type=defines.FILE)
            files.append(f)

        data_send = ProgramConfigurations(self.dirs, self.links, self.files, program_install_path=self.program_install_path_input.path, 
        program_exe_path=self.program_exe_path, program_info=self.program)

        entry = FilesOverwrite(self.files, self.dirs)
        dc = {"entry_start": "FILES_LIST:", "entry_end": "LIST_END", "data": entry.get_str()}

        files_overwrite = []
        for f in self.files:
            f = File(path=f, f_type=defines.FILE)
            f._overwrite_archive_filename = entry.get_arch_filename(f.path)
            files_overwrite.append(f)

        zip_path = env.file_manager.make_data_zip(files_overwrite, additional_data_to_send=data_send, overwrite_entries=[dc], _enable_arch_filenames_overwrite=True)
        
        sync_data = env.net_manager.configs.upload_zip(zip_path, self.program["name"], self.program["name_user"])
        env.db.programs_sync.set_program_sync_date(self.program["name"], int(sync_data["time"]), sync_data["update_id"])
        env.db.configs.set_configs(self.program["name"], self.links, self.dirs, self.files, self.program_exe_path)

    def update_links(self):
        for p in self.link_entries:
            if p.parent() != None:
                p.setParent(None)

        self.link_entries = []

        for i in range(len(self.links)):
            p = LinkEntry(self.links[i]["link"], self.links[i]["desc"], del_callback=self.delete_link)
            self.l_scrollWidgetLayout.insertWidget(i, p)
            self.l_scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)

            self.link_entries.append(p)

    def add_link(self):
        if self.link_input.get_input() == "" or self.link_desc_input.get_input() == "":
            utils.message("Заполните соответствующие поля")
            return
        link = {}
        link["link"] = self.link_input.get_input()
        link["desc"] = self.link_desc_input.get_input()
        self.links.append(link)

        self.link_input.set_input("")
        self.link_desc_input.set_input("")

        self.update_links()

    def delete_link(self, link, desc):
        for i in range(len(self.links)):
            if self.links[i]["link"] == link and self.links[i]["desc"] == desc:
                if self.link_entries[i].parent() != None:
                    self.link_entries[i].setParent(None)
                del self.link_entries[i]
                del self.links[i]
                self.update_links()
                break

    def update_dirs(self):
        for p in self.dir_entries:
            if p.parent() != None:
                p.setParent(None)

        self.dir_entries = []

        for i in range(len(self.dirs)):
            if self.change_only:
                if self.dirs[i]["path"] == self.program_preset["program_name"]+"_install":
                    continue
            p = DirEntry(self.dirs[i]["path"], self.dirs[i]["desc"], del_callback=self.delete_dir)
            self.d_scrollWidgetLayout.insertWidget(i, p)
            self.d_scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)

            self.dir_entries.append(p)

        st_m = False
        for i in range(len(self.files)):
            f = self.files[i]
            st = False
            for d in self.dirs:
                if d["real_path"] in f:
                    st = True
                    break
            if not st:
                st_m = True
                del self.files[i]
        
        if st_m:
            utils.message("Некоторые файлы убраны, так как не находятся внутри указанных папок.")
        
        self.update_files()


    def add_dir(self):
        if self.dir_input.path == None or self.dir_input_name.get_input() == "" or self.dir_input_desc.get_input() == "":
            utils.message("Заполните соответствующие поля")
            return
        dirx = {}
        dirx["real_path"] = self.dir_input.path
        dirx["desc"] = self.dir_input_desc.get_input()
        dirx["path"] = self.dir_input_name.get_input()

        if dirx not in self.dirs:
            self.dirs.append(dirx)

            self.dir_input_desc.set_input("")
            self.dir_input_name.set_input("")
            self.dir_input.reset()

            self.update_dirs()
        else:
            utils.message("Такая папка уже добавлена")
            return

    def delete_dir(self, dirx, desc):
        for i in range(len(self.dirs)):
            if self.dirs[i]["path"] == dirx and self.dirs[i]["desc"] == desc:
                if self.dir_entries[i].parent() != None:
                    self.dir_entries[i].setParent(None)
                del self.dir_entries[i]
                del self.dirs[i]
                self.update_dirs()
                break

    def update_files(self):
        for p in self.file_entries:
            if p.parent() != None:
                p.setParent(None)

        self.file_entries = []

        for i in range(len(self.files)):
            p = FileEntry(self.files[i], del_callback=self.delete_dir)
            self.f_scrollWidgetLayout.insertWidget(i, p)
            self.f_scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)

            self.file_entries.append(p)


    def add_files(self):
        self.dlg = QAskForFilesDialog("Выберите файлы", callback_yes=self.files_chosen)
        self.dlg.exec()
    def files_chosen(self, files):
        files_to_add = []
        files_warn = []
        for f in files:
            for p in self.dirs:
                if p["real_path"] in f:
                    files_to_add.append(f)
                    break
            if self.program_install_path_input.path in f and f not in files_to_add:
                files_to_add.append(f)

            if f not in files_to_add:
                files_warn.append(f)

        for f in files_to_add:
            if f not in self.files:
                self.files.append(f)
        
        self.update_files()
        if len(files_warn) > 0:
            utils.message(f"Есть {len(files_warn)} файл(ов), которые не были добавлены, так как не находятся в указанных папках.")

class LinkEntry(QFrame):
    def __init__(self, link, desc, del_callback=None):
        super().__init__()
        self.link = link
        self.desc = desc
        self.del_callback = del_callback

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)
        
        self.layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.link_label = QLabel(link)
        self.desc_label = QLabel(desc)
        self.del_btn = QInitButton("X", callback=lambda: del_callback(link, desc))

        self.layout.addWidget(self.link_label, 99)
        self.layout.addWidget(self.del_btn, 1)

        self.main_layout.addLayout(self.layout)
        self.main_layout.addWidget(self.desc_label)

class DirEntry(QFrame):
    def __init__(self, path, desc, del_callback=None):
        super().__init__()
        self.path = path
        self.desc = desc
        self.del_callback = del_callback

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)
        
        self.layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.dir_label = QLabel(path)
        self.desc_label = QLabel(desc)
        self.del_btn = QInitButton("X", callback=lambda: del_callback(path, desc))

        self.layout.addWidget(self.dir_label, 99)
        self.layout.addWidget(self.del_btn, 1)

        self.main_layout.addLayout(self.layout)
        self.main_layout.addWidget(self.desc_label)

class FileEntry(QFrame):
    def __init__(self, path, del_callback=None):
        super().__init__()
        self.path = path
        self.del_callback = del_callback

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)
        
        self.layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.path_label = QLabel(path)
        self.del_btn = QInitButton("X", callback=lambda: del_callback(path))

        self.layout.addWidget(self.path_label, 99)
        self.layout.addWidget(self.del_btn, 1)

        self.main_layout.addLayout(self.layout)