from PySide6.QtCore import QSize, Qt
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication

import os, shutil
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

from UI.tabs.projects_tab.ProjectSyncFilesChooseDialog import ProjectSyncFilesChooseDialog

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
        ui_handler.action_send_files_dlg.connect(lambda dc: self._send_files_dlg_func(dc))
        ui_handler.action_sync_all_dlg.connect(lambda dc: self._sync_all_dlg_func(dc))

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

            dlg = QYesOrNoDialog("Хотите удалить файлы проекта на этом компьютере?")
            dlg.exec()
            if dlg.answer == True:
                try: shutil.rmtree(os.path.join(env.config_manager["path"]["projects_path"], self.project["name"]), ignore_errors=False, onerror=None)
                except: utils.message("Не удалось удалить файлы проекта на этом компьютере")

            dlg = QYesOrNoDialog("Хотите удалить файлы проекта на сервере?")
            dlg.exec()
            if dlg.answer == True:
                ret = env.net_manager.files.delete_path(self.project["server_path"])
                if ret != 0:
                    utils.message("Не удалось удалить файлы проекта на сервере")
                    return
            

        if self._parent != None:
            self._parent.update_data()
    
    def open_properties(self):
        self.properties_window = ProjectPropertiesWidget(self.project) # without self. -> garbage collector will destroy window
        self.properties_window.show()
    
    def _sync_all_dlg_func(self, dc):
        files_send = dc["client_send"]
        files_get = dc["server_send"]
        files_to_delete_from_server = dc["delete_from_server_request_list"]
        files_to_delete_from_client = dc["delete_from_client_request_list"]
        dc["task"] = env.task_manager.tasks[dc["task_id"]]
        dc["task"].set_status(statuses.WAITING)
        sure = [None]

        self.dlg = ProjectSyncFilesChooseDialog(files_send=files_send, files_get=files_get, files_to_delete_from_client=files_to_delete_from_client,
        files_to_delete_from_server=files_to_delete_from_server,
        path_dont_show_client = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"]),
        path_dont_show_server = self.project["server_path"], sure=sure)

        self.dlg.exec()
        real_files_send = []
        real_files_get = []
        real_files_delete_from_server = []
        real_files_delete_from_client = []
        for f in files_send:
            real_files_send.append(File(f["path"]))
        for f in files_get:
            real_files_get.append(File(f["path"]))
        for f in files_to_delete_from_server:
            real_files_delete_from_server.append(f["path"])
        for f in files_to_delete_from_client:
            real_files_delete_from_client.append(f["path"])

        if sure[0] == True:
            if len(files_send) == 0 and len(files_get) and len(files_to_delete_from_server)== 0 and len(files_to_delete_from_client) == 0:
                dc["task"].end_task(statuses.ENDED)
                return

            func_send = lambda: env.net_manager.files.transfer_project_sources(
                os.path.join(env.config_manager["path"]["projects_path"], self.project["name"]), self.project, progress=dc["task"].progress, files_only=real_files_send)
            func_get = lambda: env.net_manager.files.get_files_for_project(files=real_files_get, project=self.project, progress=dc["task"].progress)

            func_del_from_server = lambda: env.net_manager.files.delete_files_of_project_from_server(self.project["id"], real_files_delete_from_server)
            func_del_from_client = lambda: env.file_manager.delete_files(real_files_delete_from_client)
            func_check_update = lambda: env.net_manager.files.after_project_update(self.project["id"])
            if len(real_files_send) == 0:
                func_send = lambda: 1+1
            if len(real_files_get) == 0:
                func_get = lambda: 1+1
            if len(real_files_delete_from_server) == 0:
                func_del_from_server = lambda: 1+1
            if len(real_files_delete_from_client) == 0:
                func_del_from_client = lambda: 1+1

            env.task_manager.replace_task(dc["task_id"], [func_send, func_get, func_del_from_server, func_del_from_client, func_check_update])
        else:
            dc["task"].end_task(statuses.CANCELED)

    def _send_files_dlg_func(self, dc):
        files = dc["files"]
        fr = dc["from"]
        dc["task"] = env.task_manager.tasks[dc["task_id"]]
        dc["task"].set_status(statuses.WAITING)
        files_not_accepted = dc["files_not_accepted"]
        sure = [None]
        if fr == "client":
            self.dlg = QFilesListSureDialog(files, files_not_accepted,
                "Выбор файлов", "Выберите файлы, которые будет отправлены на сервер", "Файлы на отправку", "Проигнорировать файлы", 
                path_dont_show=os.path.join(env.config_manager["path"]["projects_path"], self.project["name"]), sure=sure)
        else:
            self.dlg = QFilesListSureDialog(files, files_not_accepted,
            "Выбор файлов", "Выберите файлы, которые будут получены с сервера", "Файлы на получение", "Проигнорировать файлы",
            path_dont_show=self.project["server_path"], sure=sure)
        self.dlg.exec()

        real_files = []

        for f in files:
            real_files.append(File(f["path"]))

        if sure[0] == True:
            if len(files) == 0:
                dc["task"].end_task(statuses.ENDED)
                return
            if fr == "client":
                func = lambda: env.net_manager.files.transfer_project_sources(
                    os.path.join(env.config_manager["path"]["projects_path"], self.project["name"]), self.project, progress=dc["task"].progress, files_only=real_files)
            else:
                func = lambda: env.net_manager.files.get_files_for_project(files=real_files, project=self.project, progress=dc["task"].progress)

            env.task_manager.replace_task(dc["task_id"], func)
        else:
            dc["task"].end_task(statuses.CANCELED)

class SyncActionsUIHandlers(QObject):
    action_send_files_dlg = Signal(dict)
    action_sync_all_dlg = Signal(dict)