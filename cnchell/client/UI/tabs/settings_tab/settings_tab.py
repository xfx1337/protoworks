from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication
from PySide6.QtGui import QIntValidator


import os

from environment.tab_manager.Tab import Tab

from environment.environment import Environment
env = Environment()

import utils

import UI.stylesheets as stylesheets
from UI.widgets.QClickableLabel import QClickableLabel
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QPathInput import QPathInput
from UI.widgets.QUserInput import QUserInput

from UI.tabs.settings_tab.MachinesConnectionTableWindow import MachinesConnectionTableWindow

import defines


class SettingsWidget(QWidget, Tab):
    def __init__(self):
        super().__init__()

        self.projects_entries = []

        self.cwd = env.cwd

        self.setStyleSheet(stylesheets.DEFAULT_BORDER_STYLESHEET)

        self.layout = QVBoxLayout()

        upper_layout = QHBoxLayout()
        
        self.label = QClickableLabel(text=f"Настройки")

        self.exit_btn = QInitButton("X", callback=self.exit)

        upper_layout.addWidget(self.label, 99)
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

        self.load_settings()
    
    def load_settings(self):
        self.path_list = [
            ["Путь хранения проектов:", "projects_path"],
            ["Путь временных файлов:", "temp_path"],
            ["Путь рассчёта файлов:", "calculation_path"],
            ["Путь установки OrcaSlicer", "orca_path"]
        ]

        self.pathes_label = QLabel("Пути")
        self.scrollWidgetLayout.insertWidget(0, self.pathes_label)
        self.scrollWidgetLayout.setAlignment(self.pathes_label, Qt.AlignmentFlag.AlignTop)

        j = 1

        self.path_inputs = []

        for i in range(len(self.path_list)):
            path = self.path_list[i]
            if env.config_manager["path"][path[1]] != "none":
                p = QPathInput(path[0], path=env.config_manager["path"][path[1]], parent=self)
            else:
                p = QPathInput(path[0], parent=self)
            self.scrollWidgetLayout.insertWidget(j, p)
            self.scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)
            self.path_inputs.append(p)
            j+=1
        
        # self.networking_label = QLabel("Сетевые процессы")
        # self.scrollWidgetLayout.insertWidget(j, self.networking_label)
        # self.scrollWidgetLayout.setAlignment(self.networking_label, Qt.AlignmentFlag.AlignTop)
        # j+=1

        self.machines_label = QLabel("Конфигурация подключений станков на клиенте")
        self.scrollWidgetLayout.insertWidget(j, self.machines_label)
        self.scrollWidgetLayout.setAlignment(self.machines_label, Qt.AlignmentFlag.AlignTop)
        j += 1
        self.machines_notes_label = QLabel("В CNCHell есть возможность автоматизированного слайсинга и добавления в очередь станка. Для этого, в окне расчёта детали в очереди станка Вы можете выбрать одну из программ слайсеров, поддерживающих удалённую печать(например OrcaSlicer). В программе у станка указывается его подключение(хост, порт и тд). В таблице ниже можно получить эти данные. Подобнее читайте в руководстве пользователя.")
        self.machines_notes_label.setWordWrap(True)
        self.scrollWidgetLayout.insertWidget(j, self.machines_notes_label)
        self.scrollWidgetLayout.setAlignment(self.machines_notes_label, Qt.AlignmentFlag.AlignTop)
        j += 1
        
        self.configure_machines_btn = QInitButton("Открыть таблицу подключений станков", callback=self.open_machines_connection_table)
        self.scrollWidgetLayout.insertWidget(j, self.configure_machines_btn)
        self.scrollWidgetLayout.setAlignment(self.configure_machines_btn, Qt.AlignmentFlag.AlignTop)
        j += 1

        self.apply_btn = QInitButton("Применить", callback=self.apply)
        self.layout.addWidget(self.apply_btn)

    def open_machines_connection_table(self):
        self.machines_connection_table = MachinesConnectionTableWindow()
        self.machines_connection_table.show()

    def apply(self):
        for i in range(len(self.path_inputs)):
            env.config_manager["path"][self.path_list[i][1]] = self.path_inputs[i].path
        
        env.config_manager.override()



