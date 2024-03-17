import requests
from requests_toolbelt import MultipartEncoder

import json
import os, shutil
import numpy as np
import time

from singleton import singleton

import exceptions

import utils

from environment.config_manager.config_manager import Config
from environment.file_manager.ChunkReader import ChunkReader

from UI.widgets.QFilesListSureDialog import QFilesListSureDialog

from environment.file_manager.ZipDataAdditionalTypes import ProjectData
from environment.file_manager.File import File

import defines

@singleton
class Files:
    def __init__(self, net_manager):
        self.net_manager = net_manager
        self.env = self.net_manager.env

    def create_dirs(self, dirs, path):
        r = self.net_manager.request("/api/files/create_dirs", {"dirs": dirs, "path": dest_path})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)

    def send_data_zip(self, src_path, dest_path, progress=None):
        size = os.path.getsize(src_path)
        cr = ChunkReader(src_path, int(self.env.config_manager["server"]["chunk_size"]), progress)

        filename = src_path.split("\\")[-1]

        encoder = MultipartEncoder(fields={'file': ("data_zip", cr, 'application/octet-stream'), 
            "json": ('payload.json', json.dumps({"path": dest_path, "token": self.net_manager.token, "size": size, "filename": filename}), "application/json")}
        )
        
        r = requests.post(
            self.net_manager.host + "/api/files/upload_data_zip", data=encoder, headers={'Content-Type': encoder.content_type}
        )

        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text, no_message=True)
        
        cr.close_file_handler()

        data = json.loads(r.text)

        self.env.file_manager.delete_file(src_path)
        return data

    def send_files(self, src_path, dest_path, progress=None, filter_func=None, additional_data_to_send=None, files_only=None):
        files_list = self.env.file_manager.get_files_list(src_path)

        if filter_func != None:
            files_list = filter_func(files_list)
        if files_only:
            files_list = files_only

        progress.full = self.env.file_manager.get_list_size(files_list)

        # dirs_only = [f for f in files_list if f.f_type == defines.FOLDER]
        # dirs_only = self.env.file_manager.files_list_to_dict_list(dirs_only)
        # dirs_relative = [f.relative(src_path) for f in dirs_only]
        # self.create_dirs(dirs_relative, dest_path)

        path = self.env.file_manager.make_data_zip(files_list, relative=src_path, additional_data_to_send=additional_data_to_send)
        data = self.send_data_zip(path, dest_path, progress=progress)
        return data

    def after_project_update(self, project_id, data):
        self.env.db.projects_sync.set_project_sync_date(project_id, int(data["date"]), data["update_id"])
        
        tab_type = type(self.env.main_window.get_tab_by_alias("projects")())
        tabs = self.env.tab_manager.get_opened_tabs_by_type(tab_type)
        for t in tabs:
            tab = self.env.tab_manager.get_tab_by_id(t)
            tab.signals.update_tab.emit()

    def transfer_project_sources(self, src_path, project, progress=None, files_only=None):
        project_data = ProjectData(project)
        data = self.send_files(src_path, project["server_path"], progress=progress, additional_data_to_send=project_data, files_only=files_only)
        self.after_project_update(project["id"], data)

    def delete_path(self, path):
        r = self.net_manager.request("/api/files/delete_path", {"path": path})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED("Не удалось удалить папку на сервере", no_message=True)
        return 0
    
    def delete_files_of_project_from_server(self, project_id, files):
        r = self.net_manager.request("/api/files/delete_files_of_project", {"files": files, "project_id": project_id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED("Не удалось удалить файлы на сервере", no_message=True)
        self.after_project_update(project_id, json.loads(r.text))

    def mkdir(self, path):
        r = self.net_manager.request("/api/files/mkdir", {"path": path})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED("Не удалось создать папку на сервере", no_message=True)
        return 0

    def request_dir_tree(self, path):
        r = self.net_manager.request("/api/files/dir_tree", {"path": path})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED("Не удалось получить дерево директории сервера", no_message=True)

        return r.json()["dirs"]

    def request_files_list(self, path):
        r = self.net_manager.request("/api/files/files_list", {"path": path})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED("Не удалось получить дерево файлов сервера", no_message=True)

        return r.json()["files"]
    
    def request_files_list_for_project(self, project_id):
        r = self.net_manager.request("/api/files/files_list_for_project", {"project_id": project_id})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED("Не удалось получить дерево файлов сервера", no_message=True)

        return r.json()["files"]

    def get_zipped_path(self, path, progress=None):
        return self.get_zipped_files(path=path, progress=progress, by_path=True)
        
    def get_zipped_files(self, path=None, files=None, progress=None, by_path=False):
        cfg = self.env.config_manager
        local_filename = utils.get_unique_id()
        local_filename = os.path.join(cfg["path"]["temp_path"], local_filename) + ".zip"
        if by_path:
            url = "/api/files/get_zipped_path"
            data = {"path": path, "token": self.net_manager.token}
        else:
            url = "/api/files/get_zipped_files"
            if type(files[0]) == type(File()):
                for i in range(len(files)):
                    files[i] = files[i].path
            data = {"files": files, "token": self.net_manager.token, "path": path}
        with requests.post(self.net_manager.host+url, stream=True, 
            data = data, 
            headers = {'Content-type':'application/json'}) as r:
            r.raise_for_status()
            progress.full = int(r.headers["Content-Length"])
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(defines.CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        if progress != None:
                            progress.signals.add.emit(len(chunk))
        return local_filename

    def sync_by_action(self, project, action, progress=None, ui_handler=None):
        cfg = self.env.config_manager
        if action == defines.ACTION_OVERRIDE_SERVER_FILES:
            self.delete_path(project["server_path"])
            self.mkdir(project["server_path"])

            self.transfer_project_sources(os.path.join(cfg["path"]["projects_path"], project["name"]), project, progress)
        
        elif action == defines.ACTION_OVERRIDE_CLIENT_FILES:
            self._override_client_files(project, progress)

        elif action == defines.ACTION_SEND_ONLY_NEW_FILES_FROM_CLIENT:
            self._send_only_new_files(project, progress, "client", ui_handler)

        elif action == defines.ACTION_SEND_ONLY_NEW_FILES_FROM_SERVER:
            self._send_only_new_files(project, progress, "server", ui_handler)

        elif action == defines.ACTION_SEND_ONLY_EDITED_FILES_FROM_CLIENT:
            self._send_only_edited_files(project, progress, "client", ui_handler)
        
        elif action == defines.ACTION_SEND_ONLY_EDITED_FILES_FROM_SERVER:
            self._send_only_edited_files(project, progress, "server", ui_handler)

        elif action == defines.ACTION_SYNC_ALL_NEW_FILES:
            self._sync_all(project, progress, ui_handler)
        
        return 0

    def _sync_all(self, project, progress, ui_handler):
        cfg = self.env.config_manager
        path = os.path.join(cfg["path"]["projects_path"], project["name"])

        server_file_list = self.request_files_list_for_project(project["id"])

        server_file_list_relative = []
        server_file_list_relative_dc = {}
        for f in server_file_list:
            if f["f_type"] == defines.FILE:
                server_file_list_relative.append(utils.remove_path(project["server_path"], f["path"]))
                server_file_list_relative_dc[utils.remove_path(project["server_path"], f["path"])] = File(JSON=f)

        client_file_list = self.env.file_manager.get_files_list(path)
        client_file_list_relative = []
        client_file_list_relative_dc = {}
        for f in client_file_list:
            if f.f_type == defines.FILE:
                client_file_list_relative.append(f.relative(path))
                client_file_list_relative_dc[f.relative(path)] = f


        different_from_client = np.setdiff1d(client_file_list_relative, server_file_list_relative).tolist()
        different_from_server = np.setdiff1d(server_file_list_relative, client_file_list_relative).tolist()

        sync_data_client = self.env.db.projects_sync.get_projects_sync_data()
        client_update_time = sync_data_client[project["id"]]["date"]
        server_update_time = project["last_synced_server"]

        delete_from_server_list_dc = []
        delete_from_client_list_dc = []

        i = 0
        while i < len(different_from_server):
            f = different_from_server[i]
            if server_file_list_relative_dc[f].date_modified < client_update_time:
                delete_from_server_list_dc.append(server_file_list_relative_dc[f].to_dict())
                del different_from_server[i]
            else:
                i+=1

        i = 0
        while i < len(different_from_client):
            f = different_from_client[i]
            if client_file_list_relative_dc[f].date_modified <= server_update_time:
                delete_from_client_list_dc.append(client_file_list_relative_dc[f].to_dict())
                del different_from_client[i]
            else:
                i+=1

        common = utils.common_elements(client_file_list_relative_dc.keys(), server_file_list_relative_dc.keys())
        for i in range(len(common)):
            if client_file_list_relative_dc[common[i]].date_modified > server_file_list_relative_dc[common[i]].date_modified:
                different_from_client.append(common[i])
            if server_file_list_relative_dc[common[i]].date_modified > client_file_list_relative_dc[common[i]].date_modified:
                different_from_server.append(common[i])

        different_from_client_dc = []
        different_from_server_dc = []

        for f in different_from_client:
            abs_path = os.path.join(path, f)
            different_from_client_dc.append(File(abs_path).to_dict())

        for f in different_from_server:
            abs_path = os.path.join(project["server_path"], f)
            different_from_server_dc.append(File(abs_path).to_dict())

        files_not_accepted = []

        if progress != None:
            while progress.task == None:
                time.sleep(1)

        progress.task._disable_task_end_on_func_end = True

        if ui_handler != None:
            dc = {"client_send": different_from_client_dc, "server_send": different_from_server_dc,
            "delete_from_server_request_list": delete_from_server_list_dc, "delete_from_client_request_list": delete_from_client_list_dc, 
            "project": project, "task_id": progress.task.id}
            ui_handler.action_sync_all_dlg.emit(dc)
        
        return

    def _send_only_new_files(self, project, progress, fr="client", ui_handler=None):
        cfg = self.env.config_manager
        path = os.path.join(cfg["path"]["projects_path"], project["name"])

        server_file_list = self.request_files_list_for_project(project["id"])

        server_file_list_relative = []
        for f in server_file_list:
            if f["f_type"] == defines.FILE:
                server_file_list_relative.append(utils.remove_path(project["server_path"], f["path"]))

        client_file_list = self.env.file_manager.get_files_list(path)
        client_file_list_relative = []
        for f in client_file_list:
            if f.f_type == defines.FILE:
                client_file_list_relative.append(f.relative(path))

        different_files_dc = []

        if fr == "client":
            different = np.setdiff1d(client_file_list_relative, server_file_list_relative).tolist()
            for f in different:
                abs_path = os.path.join(path, f)
                different_files_dc.append(File(abs_path).to_dict())
        else:
            different = np.setdiff1d(server_file_list_relative, client_file_list_relative).tolist()
            for f in different:
                abs_path = os.path.join(project["server_path"], f)
                different_files_dc.append(File(abs_path).to_dict())

        files_not_accepted = []

        if progress != None:
            while progress.task == None:
                time.sleep(1)

        progress.task._disable_task_end_on_func_end = True

        if ui_handler != None:
            dc = {"files": different_files_dc, "files_not_accepted": files_not_accepted, "project": project, "task_id": progress.task.id, "from": fr}
            ui_handler.action_send_files_dlg.emit(dc)
        
        return

    def get_files_for_project(self, files, project, progress=None):
        local_filename = self.env.net_manager.files.get_zipped_files(files=files, path=project["server_path"], progress=progress)
        path = os.path.join(self.env.config_manager["path"]["projects_path"], project["name"])
        self.unzip_data_archive_register_update(local_filename, path, project=project)

    def unzip_data_archive_register_update(self, zip_path, path, project):
        data_file = self.env.file_manager.unzip_data_archive(os.path.join(zip_path), path)
        
        for f in data_file["files"]:
            self.env.file_manager.set_modification_time(os.path.join(path, f["path"]), f["date_modified"])

        projects = self.net_manager.audit.get_projects_sync_data()
        if str(project["id"]) in projects: # for some fucken reason2
            data = projects[str(project["id"])]
            self.env.db.projects_sync.set_project_sync_date(project["id"], int(data["date"]), data["update_id"])

    def _send_only_edited_files(self, project, progress, fr="client", ui_handler=None):
        cfg = self.env.config_manager
        path = os.path.join(cfg["path"]["projects_path"], project["name"])

        server_file_list = self.request_files_list_for_project(project["id"])

        server_file_list_relative = {}
        for f in server_file_list:
            if f["f_type"] == defines.FILE:
                p = utils.remove_path(project["server_path"], f["path"])
                if p not in server_file_list_relative:
                    server_file_list_relative[p] = File(JSON=f)

        client_file_list = self.env.file_manager.get_files_list(path)
        client_file_list_relative = {}
        for f in client_file_list:
            if f.f_type == defines.FILE:
                p = f.relative(path)
                if p not in client_file_list_relative:
                    client_file_list_relative[p] = f
        
        common = utils.common_elements(client_file_list_relative.keys(), server_file_list_relative.keys())
        transfer = []

        if fr == "client":
            for i in range(len(common)):
                if client_file_list_relative[common[i]].date_modified > server_file_list_relative[common[i]].date_modified:
                    transfer.append(client_file_list_relative[common[i]].to_dict())
        else:
            for i in range(len(common)):
                if server_file_list_relative[common[i]].date_modified > client_file_list_relative[common[i]].date_modified:
                    transfer.append(server_file_list_relative[common[i]].to_dict())

        files_not_accepted = []

        if progress != None:
            while progress.task == None:
                time.sleep(1)

        progress.task._disable_task_end_on_func_end = False

        if ui_handler != None:
            dc = {"files": transfer, "files_not_accepted": files_not_accepted, "project": project, "task_id": progress.task.id, "from": fr}
            ui_handler.action_send_files_dlg.emit(dc)
        
        return

    def _override_client_files(self, project, progress=None):
        cfg = self.env.config_manager
        path = os.path.join(cfg["path"]["projects_path"], project["name"])
        if os.path.isdir(path):
            try: shutil.rmtree(path, ignore_errors=False, onerror=None)
            except: 
                raise exceptions.IO_ERROR("Не удалось удалить локальную директорию", no_message=True)
                return
        
        os.mkdir(path)

        filepath = self.get_zipped_path(project["server_path"], progress=progress)
        #utils.unzip(zip=filepath, destination=cfg["path"]["projects_path"])
        #utils.delete_file(filepath)
        
        self.unzip_data_archive_register_update(filepath, path, project=project)
        return 0

    