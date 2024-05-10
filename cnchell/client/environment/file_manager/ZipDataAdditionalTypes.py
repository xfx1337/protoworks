import json

import utils

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