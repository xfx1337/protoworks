from defines import *

import utils, time, os, json, getpass


ENTRY_STRING = f"""PROTOWORKS ZIP DATA FILE
PROTOWORKS_VERSION: {PROTOWORKS_VERSION}
PROTOWORKS_FILETYPES_VERSION: {PROTOWORKS_FILETYPES_VERSION}
"""

class ZipDataFile:
    def __init__(self, files=[], dirs=[], relative_path=None):
        self.files = files
        self.dirs = dirs
        self.author = getpass.getuser()
        self.relative_path = relative_path
        self.FILE_LINKERS = {}

        self.content = ""

    def create_entry(self):
        self.content += ENTRY_STRING

    def create_metadata(self):
        self.content += f"""\n
DATE_CREATED: {utils.time_by_unix(time.time())}
MACHINE_NAME: {self.author}
        """

    def add_list_end(self):
        self.content += "\nLIST_END"

    def create_dirs_list(self):
        self.content += "\nDIRS_LIST:"
        for d in self.dirs:
            self.content += "\n"
            self.content += self._gen_dir_specs(d)
        self.add_list_end()
    
    
    def create_files_list(self):
        self.content += "\nFILES_LIST:"
        for f in self.files:
            self.content += "\n"
            self.content += self._gen_file_specs(f)
        self.add_list_end()

    def create_additional_data(self, data):
        self.content += "\n"
        if type(data) == type(list()):
            for d in data:
                self.create_additional_data(d)
        else:
            self.content += "\n"
            self.content += data.get_str()

    def _gen_dir_specs(self, d):
        path = d.path
        if self.relative_path != None and self.relative_path != "":
            path = d.relative(self.relative_path)
        elif self.relative_path == "":
            path = path.split("\\")[-1]
        
        return path

    def _gen_file_specs(self, f):
        path = f.path
        if self.relative_path != None and self.relative_path != "":
            real_path = f.relative(self.relative_path)
        elif self.relative_path == "":
            real_path = path.split("\\")[-1]
        
        ret = f.to_dict()
        ret["path"] = real_path
        arch_filename = utils.get_unique_id()
        ret["arch_filename"] = arch_filename
        self.FILE_LINKERS[arch_filename] = f.path
        return json.dumps(ret)
    
    def string(self):
        return self.content + "\n"