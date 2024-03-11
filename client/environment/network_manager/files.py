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

    def send_files(self, src_path, dest_path, progress=None, filter_func=None, additional_data_to_send=None):
        files_list = self.env.file_manager.get_files_list(src_path)

        if filter_func != None:
            files_list = filter_func(files_list)

        progress.full = self.env.file_manager.get_list_size(files_list)

        # dirs_only = [f for f in files_list if f.f_type == defines.FOLDER]
        # dirs_only = self.env.file_manager.files_list_to_dict_list(dirs_only)
        # dirs_relative = [f.relative(src_path) for f in dirs_only]
        # self.create_dirs(dirs_relative, dest_path)

        path = self.env.file_manager.make_data_zip(files_list, relative=src_path, additional_data_to_send=additional_data_to_send)
        data = self.send_data_zip(path, dest_path, progress=progress)
        return data

    def transfer_project_sources(self, src_path, project, progress=None):
        project_data = ProjectData(project)
        data = self.send_files(src_path, project["server_path"], progress=progress, additional_data_to_send=project_data)
        self.env.db.projects_sync.set_project_sync_date(project["id"], int(data["date"]), data["update_id"])
        
        tab_type = type(self.env.main_window.get_tab_by_alias("projects")())
        tabs = self.env.tab_manager.get_opened_tabs_by_type(tab_type)
        for t in tabs:
            tab = self.env.tab_manager.get_tab_by_id(t)
            tab.signals.update_tab.emit()

    def delete_path(self, path):
        r = self.net_manager.request("/api/files/delete_path", {"path": path})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED("Не удалось удалить папку на сервере", no_message=True)
        return 0

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

    def get_zipped_path(self, path, progress=None):
        return self.get_zipped_files(path, progress=progress, by_path=True)
        
    def get_zipped_files(self, path, files=None, progress=None, by_path=False):
        cfg = self.env.config_manager
        local_filename = utils.get_unique_id()
        local_filename = os.path.join(cfg["path"]["temp_path"], local_filename) + ".zip"
        if by_path:
            url = "/api/files/get_zipped_path"
            data = {"path": path, "token": self.net_manager.token}
        else:
            url = "/api/files/get_zipped_files"
            data = {"path": path, "files": files, "token": self.net_manager.token}
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

            return 0

    def _send_only_new_files(self, project, progress, fr="client", ui_handler=None):
        cfg = self.env.config_manager
        path = os.path.join(cfg["path"]["projects_path"], project["name"])

        server_file_list = self.request_files_list(project["server_path"])
        server_file_list_dict = {}

        for i in range(len(server_file_list)):
            server_file_list_dict[server_file_list[i]["filename"]] = server_file_list[i]["modification_time"]
            server_file_list[i] = server_file_list[i]["filename"]

        dirs, _ = utils.get_dirs_files(path+"\\")
        client_file_list = utils.get_files_with_modification_time(path+"\\")
        client_file_list_dict = {}

        for i in range(len(client_file_list)):
            client_file_list_dict[client_file_list[i]["filename"][len(path):]] = client_file_list[i]["modification_time"]
            client_file_list[i] = client_file_list[i]["filename"][len(path):]

        if fr == "client":
            different = np.setdiff1d(client_file_list, server_file_list).tolist()
            for i in range(len(different)):
                orig_name = different[i]
                if different[i][0] == "\\":
                    different[i] = different[i][1:]
                different[i] = {"filename": os.path.join(path, different[i]), 
                "modification_time": client_file_list_dict[orig_name]}
        else:
            different = np.setdiff1d(server_file_list, client_file_list).tolist()
            for i in range(len(different)):
                orig_name = different[i]
                if different[i][0] == "\\":
                    different[i] = different[i][1:]
                different[i] = {"filename": os.path.join(project["server_path"], different[i]), 
                "modification_time": server_file_list_dict[orig_name]}

        files_not_accepted = []

        if progress != None:
            while progress.task == None:
                time.sleep(1)

        progress.task._disable_task_end_on_func_end = False

        if ui_handler != None:
            dc = {"files": different, "files_not_accepted": files_not_accepted, "project": project, "task_id": progress.task.id, "from": fr}
            ui_handler.action_send_files_dlg.emit(dc)
        
        return

    def _send_only_edited_files(self, project, progress, fr="client", ui_handler=None):
        cfg = self.env.config_manager
        path = os.path.join(cfg["path"]["projects_path"], project["name"])

        server_file_list = self.request_files_list(project["server_path"])

        server_file_list_filenames = []
        server_file_list_dict = {}

        for i in range(len(server_file_list)):
            server_file_list_filenames.append(server_file_list[i]["filename"])
            server_file_list_dict[server_file_list[i]["filename"]] = server_file_list[i]["modification_time"]

        client_file_list = utils.get_files_with_modification_time(path+"\\")
        client_files_list_filenames = []
        client_file_list_dict = {}
        for i in range(len(client_file_list)):
            client_file_list[i]["filename"] = client_file_list[i]["filename"][len(path):]
            client_files_list_filenames.append(client_file_list[i]["filename"])
            client_file_list_dict[client_file_list[i]["filename"]] = client_file_list[i]["modification_time"]
        
        common = utils.common_elements(client_files_list_filenames, server_file_list_filenames)

        transfer = []

        if fr == "client":
            for i in range(len(common)):
                if client_file_list_dict[common[i]] > server_file_list_dict[common[i]]:
                    transfer.append(common[i])
                    if transfer[-1][0] == "\\":
                        transfer[-1] = transfer[-1][1:]
                    transfer[-1] = {"filename": os.path.join(path, transfer[-1]), 
                    "modification_time": client_file_list_dict[common[i]]}
        else:
            for i in range(len(common)):
                if server_file_list_dict[common[i]] > client_file_list_dict[common[i]]:
                    transfer.append(common[i])
                    if transfer[-1][0] == "\\":
                        transfer[-1] = transfer[-1][1:]
                    transfer[-1] = {"filename": os.path.join(project["server_path"], transfer[-1]), 
                    "modification_time": server_file_list_dict[common[i]]}

        files_not_accepted = []

        if progress != None:
            while progress.task == None:
                time.sleep(1)

        progress.task._disable_task_end_on_func_end = False

        if ui_handler != None:
            dc = {"files": transfer, "files_not_accepted": files_not_accepted, "project": project, "task_id": progress.task.id, "from": fr}
            ui_handler.action_send_files_dlg.emit(dc)
        
        return

    def get_files_creating_dirs(self, files, src_path, dest_path, progress=None):
        cfg = self.env.config_manager
        filepath = self.get_zipped_files(dest_path, files, progress=progress)
        utils.unzip(zip=filepath, destination=src_path)

        utils.delete_file(filepath)
        
    def send_files_creating_dirs(self, files, src_path, dest_path, progress=None):
        dirs, _ignore = utils.get_dirs_files(src_path + "\\")

        r = self.net_manager.request("/api/files/create_dirs", {"dirs": dirs, "path": dest_path})
        if r.status_code != 200:
            raise exceptions.REQUEST_FAILED(r.text)
        
        self.send_files(files, src_path, dest_path, progress)


    def _override_client_files(self, project, progress=None):
        cfg = self.env.config_manager
        path = os.path.join(cfg["path"]["projects_path"], project["name"])
        print(path)
        if os.path.isdir(path):
            try: shutil.rmtree(path, ignore_errors=False, onerror=None)
            except: 
                raise exceptions.IO_ERROR("Не удалось удалить локальную директорию", no_message=True)
                return
        
        os.mkdir(path)

        filepath = self.get_zipped_path(project["server_path"], progress=progress)
        #utils.unzip(zip=filepath, destination=cfg["path"]["projects_path"])
        #utils.delete_file(filepath)
        
        print(filepath)

        projects = self.net_manager.audit.get_projects_sync_data()
        if str(project["id"]) in projects: # for some fucken reason2
            data = projects[str(project["id"])]
            self.env.db.projects_sync.set_project_sync_date(project["id"], int(data["date"]), data["update_id"])

        return 0

    