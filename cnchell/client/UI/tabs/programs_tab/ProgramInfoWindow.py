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


class ProgramInfoWindow(QWidget):
    def __init__(self, program):
        super().__init__()

        self.program = program

        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        self.setWindowTitle(f"Информация о программе")

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

        self.layout.addWidget(self.program_label)
        self.layout.addWidget(self.program_code_name)

        self.d_frame = QFrame()
        self.d_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.d_frame.setLineWidth(1)
        self.d_layout = QVBoxLayout()

        self.d_scrollable = QEasyScroll()
        self.d_scrollWidgetLayout = self.d_scrollable.scrollWidgetLayout
        self.d_scrollWidget = self.d_scrollable.scrollWidget

        self.d_layout.addWidget(self.d_scrollable)
        self.d_frame.setLayout(self.d_layout)
        self.layout.addWidget(self.d_frame)

        self.links = []
        self.link_entries = []

        try:
            data = env.db.configs.get_configs_data(self.program["program_name"])
        except:
            utils.message("Не найдены конфигурационные файлы. Пожалуйста, обновите данные во вкладке 'Программы'")
            self.close()
            return

        self.update_links()
    
    def update_links(self):
        data = env.db.configs.get_configs_data(self.program["program_name"])

        self.links = data["links"]

        for p in self.link_entries:
            if p.parent() != None:
                p.setParent(None)

        self.link_entries = []

        for i in range(len(self.links)):
            p = LinkEntry(self.links[i]["link"], self.links[i]["desc"])
            self.d_scrollWidgetLayout.insertWidget(i, p)
            self.d_scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)

            self.link_entries.append(p)


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
        self.link_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.desc_label = QLabel(desc)

        self.layout.addWidget(self.link_label, 99)

        self.main_layout.addLayout(self.layout)
        self.main_layout.addWidget(self.desc_label)