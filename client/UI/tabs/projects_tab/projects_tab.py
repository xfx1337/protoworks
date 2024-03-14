from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication
import os

from environment.tab_manager.Tab import Tab

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

import utils

import UI.stylesheets as stylesheets
from UI.widgets.QClickableLabel import QClickableLabel
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QListEntry import QListEntry

from UI.tabs.projects_tab.create_project import CreateProjectWidget

import defines

from UI.tabs.projects_tab.ProjectListEntry import ProjectListEntry
from UI.tabs.projects_tab.ProjectPropertiesWidget import ProjectPropertiesWidget

from UI.widgets.QAskForFilesDialog import QAskForFilesDialog

from UI.widgets.QEasyScroll import QEasyScroll

from UI.tabs.TabSignals import TabSignals

class ProjectsWidget(QWidget, Tab):
    def __init__(self):
        super().__init__()

        self.signals = TabSignals()
        self.signals.update_tab.connect(self.update_data)

        self.projects_entries = []

        self.menu = QMenu(self)
        action_update = self.menu.addAction("Обновить")
        action_create = self.menu.addAction("Создать")
        action_update.triggered.connect(self.update_data)
        action_create.triggered.connect(self.create_project)


        self.cwd = env.cwd

        self.setStyleSheet(stylesheets.DEFAULT_BORDER_STYLESHEET)

        self.layout = QVBoxLayout()

        upper_layout = QHBoxLayout()
        
        self.label = QClickableLabel(text=f"Проекты")

        self.exit_btn = QInitButton("X", callback=self.exit)

        upper_layout.addWidget(self.label, 99)
        upper_layout.addWidget(self.exit_btn, 1)
        upper_layout.setSpacing(0)
        upper_layout.setAlignment(self.exit_btn, Qt.AlignmentFlag.AlignRight)


        self.layout.addLayout(upper_layout)
        self.layout.setAlignment(upper_layout, Qt.AlignmentFlag.AlignTop)

        self.scrollable = QEasyScroll()

        self.scrollWidgetLayout = self.scrollable.scrollWidgetLayout
        self.scrollWidget = self.scrollable.scrollWidget

        self.layout.addWidget(self.scrollable)
        self.setLayout(self.layout)

        self.update_data()
    
    def update_data(self):
        try: 
            data = env.net_manager.projects.get_projects()
            sync_data = env.net_manager.audit.get_projects_sync_data()
        except Exception as e: 
            utils.message(str(e))
            return

        
        for p in self.projects_entries:
            if p.parent() != None:
                p.setParent(None)

        self.projects_entries = []

        projects = data["projects"]

        projects = sorted(projects, key=lambda key: (key["status"], key["time_deadline"]))

        for i in range(len(projects)):
            project = projects[i]
            last_synced = None
            if str(project["id"]) in sync_data: # for some fucken reason
                last_synced_server = sync_data[str(project["id"])]["date"]
                project["last_synced_server"] = last_synced_server
                project["update_id_server"] = sync_data[str(project["id"])]["update_id"]
            
            data = env.db.projects_sync.get_projects_sync_data()
            if project["id"] in data:
                last_synced_client = data[project["id"]]["date"]
                project["last_synced_client"] = last_synced_client
                project["update_id_client"] = data[project["id"]]["update_id"]

            p = ProjectListEntry(project, parent=self)
            self.scrollWidgetLayout.insertWidget(i, p)
            self.scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)

            self.projects_entries.append(p)


    def create_project(self):
        dlg = CreateProjectWidget(callback=self.ask_for_files)
        dlg.show()

    def ask_for_files(self, project_id):
        project = env.net_manager.projects.get_project_info(project_id)
        try: os.mkdir(os.path.join(env.config_manager["path"]["projects_path"], project["name"])) # it can be already created
        except: pass 
        self.dlg = QAskForFilesDialog("Если у вас есть файлы проекта, загрузите их", project_id=project_id,
        callback_yes=self._transfer_files_processing, callback_no = self.update_data) # only with .self or it will be destroyed
        self.dlg.show()

    def _transfer_files_processing(self, path, project_id):
        project = env.net_manager.projects.get_project_info(project_id)
        name = project["name"]
        pro = Progress()
        env.task_manager.append_task( lambda: (env.net_manager.files.transfer_project_sources(path, project, pro)),
        f"[{name}] Перенос файлов на сервер", progress=pro)

        self.update_data()

    def delete_project(self, id):
        pass

    def open_in_app(self):
        pass
    
    def open(self):
        pass
    
    def sync(self):
        pass
    
    def contextMenuEvent(self, event):
        self.menu.exec(event.globalPos())