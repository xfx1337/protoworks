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
        if "PROJECT DATA" in data:
            d = get(data, "PROJECT DATA: ")
            self.entries['project'] = json.loads(d)
        
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
        
        return self.entries

def get(data, header, end="\n"):
    try:
        start = data.index( header ) + len( header )
        end = data.index( end, start )
        return data[start:end]
    except ValueError:
        return ""