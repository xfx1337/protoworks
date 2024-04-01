import requests
import os

from singleton import singleton

import exceptions

from environment.part_manager.Part import Part

from environment.file_manager.ZipDataAdditionalTypes import ProjectData, PartsData

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
                for f in files_only_t:
                    if f not in files_only:
                        files_only.append(f)
                ids_files_linkers[i] = files_only_t
        parts_data = PartsData(ids_files_linkers, relative=src_path)
        data = self.env.net_manager.files.send_files(src_path, project["server_path"], progress=progress, additional_data_to_send=[project_data, parts_data], files_only=files_only)
        self.env.net_manager.files.after_project_update(project["id"], data)