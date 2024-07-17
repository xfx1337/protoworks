import json

import utils

import os

class ProjectData:
    def __init__(self, project):
        self.project = project
        if self.project == None:
            self.data = ""
        self.data = json.dumps(self.project)

    def get_str(self):
        return "PROJECT_DATA: " + self.data

class PartsData:
    def __init__(self, ids_files_linkers, relative=None):
        self.ids_files_linkers = ids_files_linkers
        self.data = json.dumps(self.ids_files_linkers)
        self.relative = relative
    
    def get_str(self):
        out = "PARTS_DATA: \n"
        for i in list(self.ids_files_linkers.keys()):
            e = self.ids_files_linkers[i]
            files_pathes = []
            if self.relative != None:
                for f in e:
                    files_pathes.append(utils.remove_path(self.relative, f))
            else:
                files_pathes = e.copy()

            d = {"id": i, "files": files_pathes}
            out += (json.dumps(d) + "\n")
        out += "LIST_END"
        return out

class ProgramConfigurations:
    def __init__(self, pathes, links, files, program_install_path=None, program_exe_path=None, program_info=None):
        self.pathes = pathes
        self.links = links
        self.files = files
        self.program_install_path = program_install_path
        self.program_exe_path = program_exe_path
        self.program_info = program_info
        if self.program_install_path and self.program_info:
            program_name = self.program_info["name"]
            self.pathes.append({"real_path": self.program_install_path, "path": program_name+"_install", "desc": "Папка установки программы"})
    
    def get_str(self):
        out = "CONFIGS_PATHES_LIST:\n"
        for p in self.pathes:
            path = p["path"]
            desc = p["desc"]
            out += f"{path} | {desc}\n"
        out += "LIST_END\n\n"

        out += "CONFIGS_FILE_LIST:\n"
        for p in self.files:
            st = False
            dirname, filename = os.path.split(p)
            save_path = dirname
            for p_l in self.pathes:
                if os.path.abspath(p_l["real_path"]) in os.path.abspath(dirname):
                    dirname = os.path.abspath(dirname)
                    rel = os.path.relpath(p, start=p_l["real_path"])
                    res = os.path.join(p_l["path"], rel)
                    out += res
                    out += "\n"
                    st = True
                    break
            
        out += "LIST_END\n\n"

        out += "PROGRAMS_LINKS_LIST:\n"
        for l in self.links:
            link = l["link"]
            desc = l["desc"]
            out += f"{link} | {desc}\n"
        out += "LIST_END\n\n"

        #if self.program_install_path:
            #out += f"PROGRAM_INSTALL_PATH: {self.program_install_path}\n"
        
        if self.program_exe_path and self.program_install_path and self.program_info:
            dirname, filename = os.path.split(self.program_exe_path)
            save_path = dirname
            if os.path.abspath(self.program_install_path) in os.path.abspath(self.program_exe_path):
                dirname = os.path.abspath(dirname)
                rel = os.path.relpath(self.program_exe_path, start=self.program_install_path)
                res = os.path.join(self.program_info["name"] + "_install", rel)
                out += f"PROGRAM_EXE_PATH: {res}\n"

        if self.program_info:
            name = self.program_info["name_user"]
            name_user = self.program_info["name"]
            out += f"PROGRAM_NAME: {name}\n"
            out += f"PROGRAM_NAME_USER: {name_user}\n"

        return out