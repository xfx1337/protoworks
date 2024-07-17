from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication
from PySide6.QtGui import QIntValidator


import os
import json
import ctypes

from environment.tab_manager.Tab import Tab

from environment.environment import Environment
env = Environment()

import utils

import UI.stylesheets as stylesheets
from UI.widgets.QClickableLabel import QClickableLabel
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QPathInput import QPathInput
from UI.widgets.QUserInput import QUserInput
from UI.widgets.QAreUSureDialog import QAreUSureDialog

import defines

from UI.widgets.QProgramWidget import QProgramWidget
from UI.tabs.programs_tab.AddProgramWindow import AddProgramWindow
from UI.tabs.programs_tab.ProgramConfigurationWindow import ProgramConfigurationWindow
from UI.tabs.programs_tab.ProgramInfoWindow import ProgramInfoWindow
from UI.widgets.QSelectOneFromList import QSelectOneFromList

import subprocess

from environment.file_manager.ZipDataAdditionalTypes import ProgramConfigurations 
from UI.widgets.QAskForFilesDialog import QAskForFilesDialog
from environment.file_manager.File import File

class ProgramsWidget(QWidget, Tab):
    def __init__(self):
        super().__init__()

        self.programs_entries = []

        self.cwd = env.cwd

        self.setStyleSheet(stylesheets.DEFAULT_BORDER_STYLESHEET)

        self.layout = QVBoxLayout()

        upper_layout = QHBoxLayout()
        
        self.label = QClickableLabel(text=f"Программы")

        self.add_program_btn = QInitButton("Добавить", callback=self.add_program)
        self.exit_btn = QInitButton("X", callback=self.exit)

        upper_layout.addWidget(self.label, 99)
        upper_layout.addWidget(self.add_program_btn, 1)
        upper_layout.addWidget(self.exit_btn, 1)
        upper_layout.setSpacing(0)
        upper_layout.setAlignment(self.exit_btn, Qt.AlignmentFlag.AlignRight)


        self.layout.addLayout(upper_layout)
        self.layout.setAlignment(upper_layout, Qt.AlignmentFlag.AlignTop)

        self.scrollable = QScrollArea()
        self.scrollable.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollable.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollable.setWidgetResizable(True)

        self.scrollWidgetLayout = QVBoxLayout()
        self.scrollWidgetLayout.setSpacing(0)
        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollWidgetLayout)
        self.scrollable.setWidget(self.scrollWidget)
        #self.scrollable.setLayout(self.scroll_layout)

        #self.update_data()
        
        self.scrollWidgetLayout.addStretch()

        self.layout.addWidget(self.scrollable)
        self.setLayout(self.layout)

        self.load_programs()
    
    def load_programs(self):
        self.programs_list = env.net_manager.configs.get_sync_data()
        self.programs_sync = env.db.programs_sync.get_programs_sync_data()

        j = 0
        for key in self.programs_list.keys():
            program = self.programs_list[key]
            t = program["date"]
            t_c = -1
            if program["program_name"] in self.programs_sync:
                t_c = self.programs_sync[program["program_name"]]["date"]

            if t_c == -1:
                t_c = "Отсутствует"
            else:
                t_c = utils.time_by_unix(t)

            p = QProgramWidget(program["program_user_alias"], "app", "Открыть", lambda val=str(program): self.open_prog(program), [64,64], 
            [["Информация", lambda val=str(program): self.show_info(program)],
            ["Конфигурация", lambda val=str(program): self.configure_prog(program)], 
            ["Обновить данные", lambda val=str(program): self.update_prog(program)], 
            ["Удалить из каталога", lambda val=str(program): self.delete(program)]], 
            [f"Последнее обновление данных(сервер): {utils.time_by_unix(t)}", 
            f"Последнее обновление данных(клиент): {t_c}"])
            self.scrollWidgetLayout.insertWidget(j, p)
            self.scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)
            self.programs_entries.append(p)
            j+=1

    def show_info(self, program):
        self.prog_info_wnd = ProgramInfoWindow(program)
        self.prog_info_wnd.show()

    def delete(self, program):
        dlg = QAreUSureDialog("Введите название программы, что бы подтвердить удаление.")
        dlg.exec()
        if dlg.input.text() == program["program_user_alias"]:
            env.net_manager.configs.delete(program["program_name"])
            utils.message("Запрос отправлен", tittle="Уведомление")

    def configure_prog(self, program):
        self.cfg_wnd = ProgramConfigurationWindow(program)
        self.cfg_wnd.show()
    
    def open_prog(self, program):
        try:
            program = env.db.configs.get_configs_data(program["program_name"])
        except:
            utils.message("Не удалось из-за конфигурации")
            return
        

        if "program_exe_path" in program:
            if program["program_exe_path"] != '':
                path = program["program_exe_path"]
                subprocess.Popen(f'"{path}"')
            else:
                utils.message("Не настроена конфигурация")
                return
        else:
            utils.message("Не настроена конфигурация")
            return
    
    def update_prog(self, program):
        self.update_dlg = QSelectOneFromList("Выбор", ["Обновить клиент", "Обновить сервер", "Обновить сервер и поменять конфигурацию"], 
        callback=lambda key: self.update_prog_callback(program, key))
        self.update_dlg.show()

    def update_prog_callback(self, program, option):
        if option == "Обновить сервер" or option == "Обновить сервер и поменять конфигурацию":
            try:
                program = env.db.configs.get_configs_data(program["program_name"])
            except:
                utils.message("Не удалось из-за конфигурации")
                return
            if "program_exe_path" in program:
                if program["program_exe_path"] != '':
                    pass
                else:
                    utils.message("Не настроена конфигурация")
                    return
            else:
                utils.message("Не настроена конфигурация")
                return
        
        if option == "Обновить сервер":
            data = env.db.configs.get_configs_data(program["program_name"])
            files = []
            for f in data["files"]:
                f = File(path=f, f_type=defines.FILE)
                files.append(f)

            program_install_path = ""
            d_name = [program["program_name"] + "_install"]
            for d in data["dirs"]:
                if d["path"] == d_name:
                    program_install_path = d["real_path"]
                    break
            program_exe_path = program["program_exe_path"]

            programs_list = env.net_manager.configs.get_sync_data()
            program_user_alias = programs_list[program["program_name"]]["program_user_alias"]
            program = {"name": program["program_name"], "name_user": program_user_alias}

            data_send = ProgramConfigurations(data["dirs"], data["links"], data["files"], program_install_path=program_install_path, 
            program_exe_path=program_exe_path, program_info=program)
            zip_path = env.file_manager.make_data_zip(files, additional_data_to_send=data_send)
            
            sync_data = env.net_manager.configs.upload_zip(zip_path, program["name"], program_user_alias)
            env.db.programs_sync.set_program_sync_date(program["name"], int(sync_data["time"]), sync_data["update_id"])
            env.db.configs.set_configs(program["name"], data["links"], data["dirs"], data["files"], program_exe_path)
            utils.message("Отправлено")
    
        if option == "Обновить сервер и поменять конфигурацию":
            self.add_program_wnd = AddProgramWindow(change_only=True, program=program)
            self.add_program_wnd.show()

        if option == "Обновить клиент":
            zip_path = env.net_manager.configs.get_zip(program["program_name"])
            data = env.db.configs.get_configs_data(program["program_name"])
            idx = utils.get_unique_id() 
            filename = os.path.join(env.config_manager["path"]["temp_path"], (idx + ".txt"))
            out = {"zip_path": zip_path, "data": data, "program": program}
            with open(filename, "w") as f:
                f.write(json.dumps(out))

            ctypes.windll.shell32.ShellExecuteW(None, "runas", "additional\\unzip_config\\unzip_config.bat", f"{filename}", None, 1)
            data_file = self.env.file_manager.unzip_data_configs_archive(zip_path, data)
            

    def add_program(self):
        self.add_program_wnd = AddProgramWindow()
        self.add_program_wnd.show()