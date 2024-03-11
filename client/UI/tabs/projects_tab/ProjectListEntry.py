from PySide6.QtCore import QSize, Qt
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication

import os

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
from UI.tabs.projects_tab.ProjectSyncDialog import ProjectSyncDialog

from UI.widgets.QYesOrNoDialog import QYesOrNoDialog
from UI.widgets.QFilesListSureDialog import QFilesListSureDialog

import environment.task_manager.statuses as statuses

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
        action_sync = self.menu.addAction("Синхронизировать")
        action_pass = self.menu.addAction("Сдать")
        action_delete = self.menu.addAction("Удалить")
        action_properties = self.menu.addAction("Свойства")

        action_open.triggered.connect(self.open)
        action_open_dir.triggered.connect(self.open_dir)
        action_sync.triggered.connect(self.sync)
        action_pass.triggered.connect(self.pass_project)
        action_delete.triggered.connect(self.delete)
        action_properties.triggered.connect(self.open_properties)

        if self.project["status"] == defines.PROJECT_IN_WORK and utils.unix_is_expired(self.project["time_deadline"]):
            self.label1.setStyleSheet(stylesheets.combine([stylesheets.YELLOW_HIGHLIGHT, stylesheets.DISABLE_BORDER]))
            self.label1.setText(f'[Просрочен] {self.project["name"]}')
        
        if self.project["status"] == defines.PROJECT_DONE:
            self.setStyleSheet(stylesheets.combine([BLACK_HIGHLIGHT, DISABLE_BORDER]))
            self.label1.setText(f'[Сдан] {self.project["name"]}')

    def contextMenuEvent(self, event):
        self.menu.exec(event.globalPos())

    def open(self):
        pass
    
    def open_dir(self):
        pass
    
    def sync(self):
        dlg = ProjectSyncDialog(callback=self._start_sync_thread)
        dlg.exec()

    def _start_sync_thread(self, action):
        pro = Progress()
        action_translation = defines.ACTION_TRANSLATIONS[action]
        project_name = self.project["name"]

        ui_handler = SyncActionsUIHandlers()
        ui_handler.action_send_files_dlg.connect(lambda dc: self._send_fiels_dlg_func(dc))

        task = env.task_manager.append_task( lambda: (env.net_manager.files.sync_by_action(self.project, action, progress=pro, ui_handler=ui_handler)),
        f"[{project_name}] {action_translation}", progress=pro)
        pro.set_task(task)

    def pass_project(self):
        dlg = QAreUSureDialog("Проект действительно сдан заказчику и принят? Напишите название проекта ниже, если подтверждаете")
        dlg.exec()
        if dlg.input.text() == self.project["name"]:
            ret =  env.net_manager.projects.pass_(self.project["id"])
        
        if self._parent != None:
            self._parent.update_data()
    
    def delete(self):
        dlg = QAreUSureDialog("Вы действительно хотите безвозвратно удалить проект? Напишите название проекта ниже, если подтверждаете")
        dlg.exec()
        if dlg.input.text() == self.project["name"]:
            ret = env.net_manager.projects.delete(self.project["id"])
            if ret != 0:
                utils.message("Не удалось удалить проект")
                return

            dlg = QYesOrNoDialog("Хотите удалить файлы проекта на сервере?")
            dlg.exec()
            if dlg.answer == True:
                ret = env.net_manager.files.delete_path(self.project["server_path"])
                if ret != 0:
                    utils.message("Не удалось удалить файлы проекта")
                    return

        if self._parent != None:
            self._parent.update_data()
    
    def open_properties(self):
        self.properties_window = ProjectPropertiesWidget(self.project) # without self. -> garbage collector will destroy window
        self.properties_window.show()
    
    def _send_fiels_dlg_func(self, dc):
        files = dc["files"]
        fr = dc["from"]
        dc["task"] = env.task_manager.tasks[dc["task_id"]]
        dc["task"].set_status(statuses.WAITING)
        files_not_accepted = dc["files_not_accepted"]
        sure = [None]
        if fr == "client":
            dlg = QFilesListSureDialog(files, files_not_accepted,
                "Выбор файлов", "Выберите файлы, которые будет отправлены на сервер", "Файлы на отправку", "Проигнорировать файлы", 
                path_dont_show=os.path.join(env.config_manager["path"]["projects_path"], self.project["name"]), sure=sure)
        else:
            dlg = QFilesListSureDialog(files, files_not_accepted,
            "Выбор файлов", "Выберите файлы, которые будут получены с сервера", "Файлы на получение", "Проигнорировать файлы",
            path_dont_show=self.project["server_path"], sure=sure)
        dlg.exec()

        real_files = []

        for f in files:
            real_files.append(f["filename"])

        if sure[0] == True:
            if len(files) == 0:
                dc["task"].end_task(statuses.ENDED)
                return
            if fr == "client":
                func = lambda: env.net_manager.files.send_files_creating_dirs(real_files, os.path.join(env.config_manager["path"]["projects_path"], self.project["name"]), 
                    self.project["server_path"], progress=dc["task"].progress)
            else:
                func = lambda: env.net_manager.files.get_files_creating_dirs(real_files, os.path.join(env.config_manager["path"]["projects_path"], self.project["name"]), 
                self.project["server_path"], progress=dc["task"].progress)

            env.task_manager.replace_task(dc["task_id"], func)
        else:
            dc["task"].end_task(statuses.CANCELED)

class SyncActionsUIHandlers(QObject):
    action_send_files_dlg = Signal(dict)