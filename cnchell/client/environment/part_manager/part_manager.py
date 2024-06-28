import requests
import os

from singleton import singleton

import exceptions

from environment.part_manager.Part import Part
from environment.file_manager.File import File

from environment.file_manager.ZipDataAdditionalTypes import ProjectData, PartsData

import utils
from defines import *

@singleton
class PartManager:
    def __init__(self, env):
        self.env = env
    
    def send_parts(self, project, ids, files_only=None, progress=None):
        project_data = ProjectData(project)
        src_path = os.path.join(self.env.config_manager["path"]["projects_path"], project["name"])
        search_path = os.path.join(src_path, "ДЕТАЛИ-PW")

        ids_files_linkers = {}
        if files_only == None:
            files_only = []
            for i in ids:
                name = f"_PW{str(i)}"
                files_only_t = self.env.file_manager.search(search_path, name)
                files_only_t_pathes = []
                for f in files_only_t:
                    files_only_t_pathes.append(f.path)
                for f in files_only_t_pathes:
                    if f not in files_only:
                        files_only.append(f)
                ids_files_linkers[i] = files_only_t_pathes
        parts_data = PartsData(ids_files_linkers, relative=src_path)
        data = self.env.net_manager.files.send_files(src_path, project["server_path"], progress=progress, additional_data_to_send=[project_data, parts_data], files_only=files_only)
        self.env.net_manager.files.after_project_update(project["id"], data)
    
    def get_available_part_files_by_id(self, project, id):
        path = os.path.join(self.env.config_manager["path"]["projects_path"], project["name"])
        path = os.path.join(path, "ДЕТАЛИ-PW")
        name = "_PW" + str(id)
        files = self.env.file_manager.search(path, name)
        found = []
        for f in files:
            i = f.path.split("_PW")[-1].split(".")[0]
            if str(i) == str(id):
                found.append(f)
        return found
    
    def check_part_up_to_date_with_origin(self, project, part):
        try:
            client_path = utils.remove_path(project["server_path"], part["path"])
            project_path = os.path.join(self.env.config_manager["path"]["projects_path"], project["name"])
            client_path = os.path.join(project_path, client_path)
            origin_file = File(path=client_path, f_type=FILE)
        except:
            return -1

        files = self.get_available_part_files_by_id(project, part["id"])
        st = False
        for f in files:
            if f.date_modified < origin_file.date_modified:
                st = True
                break
        
        return not st
    
    def update_parts(self, project, parts):
        self.env.net_manager.parts.update_parts(project["id"], parts)

    def delete_parts(self, project, parts):
        ids = []
        for p in parts:
            ids.append(p["id"])
        self.env.net_manager.parts.delete_parts(project["id"], ids)

    def indentify_parts(self, files):
        for i in range(len(files)):
            if "file:///" in files[i]:
                files[i] = files[i][8:]
            files[i] = files[i].replace("/", "\\")
        relative_files = []
        not_parts = []
        for f in files:
            if self.env.config_manager["path"]["projects_path"] in f:
                path_p = utils.remove_path(self.env.config_manager["path"]["projects_path"], f)
                relative_files.append(path_p)
            else:
                not_parts.append(f)
        if len(relative_files) > 0: 
            parts = self.env.net_manager.parts.indentify_parts(relative_files)
            return parts, not_parts
        return [], not_parts