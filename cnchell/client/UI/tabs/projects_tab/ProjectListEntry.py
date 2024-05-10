from PySide6.QtCore import QSize, Qt
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication

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


from UI.tabs.projects_tab.ProjectPropertiesWidget import ProjectPropertiesWidget

from UI.widgets.QYesOrNoDialog import QYesOrNoDialog
from UI.widgets.QFilesListSureDialog import QFilesListSureDialog

from UI.tabs.projects_tab.ProjectView import ProjectView

import environment.task_manager.statuses as statuses

from environment.file_manager.File import File
from environment.file_manager.ZipDataAdditionalTypes import ProjectData

import defines

class ProjectListEntry(QDoubleLabel):
    def __init__(self, project, parent=None):
        self.project = project
        self._parent = parent

        if "last_synced_server" not in project:
            super().__init__(self.project["name"], "")
        else:
            last_synced_server = project["last_synced_server"]
            super().__init__(self.project["name"], f"Последнее обновление на сервере: {utils.time_by_unix(last_synced_server)}")
        
            if "last_synced_client" in project:
                if project["last_synced_client"] < project["last_synced_server"]:
                    self.label2.setStyleSheet(stylesheets.combine([stylesheets.YELLOW_HIGHLIGHT, stylesheets.DISABLE_BORDER]))

        self.menu = QMenu(self)
        self.menu.setStyleSheet(stylesheets.DEFAULT_BORDER_STYLESHEET)
        action_open = self.menu.addAction("Открыть")
        action_open_dir = self.menu.addAction("Открыть директорию")
        action_properties = self.menu.addAction("Свойства")

        action_open.triggered.connect(self.open)
        action_open_dir.triggered.connect(self.open_dir)
        action_properties.triggered.connect(self.open_properties)

        if self.project["status"] == defines.PROJECT_IN_WORK and utils.unix_is_expired(self.project["time_deadline"]):
            self.label1.setStyleSheet(stylesheets.combine([stylesheets.YELLOW_HIGHLIGHT, stylesheets.DISABLE_BORDER]))
            self.label1.setText(f'[Просрочен] {self.project["name"]}')
        
        if self.project["status"] == defines.PROJECT_DONE:
            #self.setStyleSheet(stylesheets.combine([stylesheets.BLACK_HIGHLIGHT, DISABLE_BORDER]))
            self.label1.setText(f'[Сдан] {self.project["name"]}')

    def contextMenuEvent(self, event):
        self.menu.exec(event.globalPos())

    def open(self):
        self.view = ProjectView(self.project)
        self.view.show()
    
    def open_dir(self):
        path = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"])
        subprocess.Popen(f'explorer "{path}"')
    
    
    def open_properties(self):
        self.properties_window = ProjectPropertiesWidget(self.project) # without self. -> garbage collector will destroy window
        self.properties_window.show()