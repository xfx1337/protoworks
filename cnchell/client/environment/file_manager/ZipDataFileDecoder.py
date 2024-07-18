import re
import json

from singleton import singleton

@singleton
class ZipDataFileDecoder:
    def __init__(self):
        pass
    
    def decode(self, data):
        self.entries = {}
        data += "\n"
        if "PROJECT_DATA" in data:
            d = get(data, "PROJECT_DATA: ")
            self.entries['project'] = json.loads(d)
        
        if "PARTS_DATA" in data:
            d = get(data, "PARTS_DATA:", "LIST_END").split("\n")
            self.entries["parts"] = []
            for f in d:
                try: self.entries["files"].append(json.loads(f))
                except: pass

        if "PROTOWORKS_VERSION" in data:
            d = get(data, "PROTOWORKS_VERSION: ").replace("\n", "").replace("\r", "")
            self.entries["pw_ver"] = d
        
        if "PROTOWORKS_FILETYPES_VERSION" in data:
            d = get(data, "PROTOWORKS_FILETYPES_VERSION: ").replace("\n", "").replace("\r", "")
            self.entries["pw_filetypes_version"] = d
        
        if "DATA_CREATED" in data:
            d = get(data, "DATA_CREATED: ")
            self.entries["data_created"] = d.replace("\n", "").replace("\r", "")
        
        if "MACHINE_NAME" in data:
            d = get(data, "MACHINE_NAME: ")
            self.entries["machine_name"] = d.replace("\n", "").replace("\r", "")
        
        if "DIRS_LIST" in data:
            d = get(data, "DIRS_LIST:", "LIST_END").split("\n")
            self.entries["dirs"] = []
            for f in d:
                if len(f) < 1 or f == "\r":
                    pass
                else:
                    self.entries["dirs"].append(f.replace("\r", ""))
        
        if "FILES_LIST" in data:
            d = get(data, "FILES_LIST:", "LIST_END").split("\n")
            self.entries["files"] = []
            for f in d:
                try: self.entries["files"].append(json.loads(f))
                except: pass
        
        if "CONFIGS_PATHES_LIST" in data:
            d = get(data, "CONFIGS_PATHES_LIST:", "LIST_END").split("\n")
            self.entries["pathes"] = []
            for f in d:
                try: self.entries["pathes"].append(json.loads(f))
                except: pass

        if "CONFIGS_FILE_LIST" in data:
            d = get(data, "CONFIGS_FILE_LIST:", "LIST_END").split("\n")
            self.entries["configs_files"] = []
            for f in d:
                x = f.replace("\r", "")
                if x != "":
                    try: self.entries["configs_files"].append(x)
                    except: pass

        if "PROGRAMS_LINKS_LIST" in data:
            d = get(data, "PROGRAMS_LINKS_LIST:", "LIST_END").split("\n")
            self.entries["links"] = []
            for f in d:
                try: self.entries["links"].append(json.loads(f))
                except: pass

        if "PROGRAM_EXE_PATH" in data:
            d = get(data, "PROGRAM_EXE_PATH: ").replace("\n", "").replace("\r", "")
            self.entries["program_exe_path"] = d
        
        if "PROGRAM_NAME" in data:
            d = get(data, "PROGRAM_NAME: ").replace("\n", "").replace("\r", "")
            self.entries["program_name"] = d

        if "PROGRAM_NAME_USER" in data:
            d = get(data, "PROGRAM_NAME_USER: ").replace("\n", "").replace("\r", "")
            self.entries["program_name_user"] = d

        return self.entries

def get(data, header, end="\n"):
    try:
        start = data.index( header ) + len( header )
        end = data.index( end, start )
        return data[start:end]
    except ValueError:
        return ""