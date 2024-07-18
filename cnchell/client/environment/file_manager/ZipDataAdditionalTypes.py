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

            st = False
            for d in self.pathes:
                if d["path"] == (program_name+"_install"):
                    st = True
                    break
            if not st:
                self.pathes.append({"real_path": self.program_install_path, "path": program_name+"_install", "desc": "Папка установки программы"})

        self._configs_file_done = []

    def get_str(self):
        out = "CONFIGS_PATHES_LIST:\n"
        for p in self.pathes:
            path = p["path"]
            desc = p["desc"]
            d = {"path": path, "desc": desc}
            out += (json.dumps(d) + "\n")
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
                    if res not in self._configs_file_done:
                        out += res
                        out += "\n"
                        self._configs_file_done.append(res)
                    st = True
            
        out += "LIST_END\n\n"

        out += "PROGRAMS_LINKS_LIST:\n"
        for l in self.links:
            link = l["link"]
            desc = l["desc"]
            d = {"link": link, "desc": desc}
            out += (json.dumps(d) + "\n")
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

class FilesOverwrite:
    def __init__(self, files, dirs):
        self.files = files
        self.dirs = dirs
        self.content = ""
        self._arch_files = {}
        self._files_done = []
    
    def get_str(self):
        self.content += "\nFILES_LIST:"
        for f in self.files:
            try:
                o = self._gen_file_specs(f)
                self.content += "\n"
                self.content += o
            except:
                pass
        self.content += "\nLIST_END"
        return self.content

    def _gen_file_specs(self, f):
        res = ""
        for d in self.dirs:
            if os.path.abspath(d["real_path"]) in os.path.abspath(f):
                rel = os.path.relpath(f, start=d["real_path"])
                res = os.path.join(d["path"], rel)
        if res != "":
            ret = {}
            ret["path"] = res
            arch_filename = utils.get_unique_id()
            ret["arch_filename"] = arch_filename
            if res in self._files_done:
                raise ValueError
            self._files_done.append(res)
            self._arch_files[os.path.abspath(f)] = ret["arch_filename"]
            return json.dumps(ret)
        raise ValueError

    def get_arch_filename(self, path):
        return self._arch_files[path]