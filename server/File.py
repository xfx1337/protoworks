import os, time

CUR_CLIENT = 0
SERVER = 1
FILE = 0
FOLDER = 1

class File:
    def __init__(self, path=None, date_modified=None, size=None, host_pc=SERVER, f_type=FILE, JSON=None):
        self.path = path
        self.date_modified = date_modified
        self.size = size
        self.host_pc = host_pc
        self.f_type = f_type
        if self.path != None and self.host_pc == CUR_CLIENT and self.date_modified == None and self.f_type == FILE:
            self.date_modified = time.ctime(os.path.getmtime(self.path))
        if self.path != None and self.host_pc == CUR_CLIENT and self.size == None and self.f_type == FILE:
            self.size = os.path.getsize(self.path)

        if JSON != None:
           self.path = JSON["path"]
           self.date_modified = JSON["date_modified"]
           self.size = JSON["size"]
           self.host_pc = JSON["host_pc"]
           self.f_type = JSON["f_type"]

    def relative(path):
        return os.path.join(path, self.path)
    
    def to_dict(self):
        return {"path": self.path, 
                "date_modified": self.date_modified,
                "size": self.size,
                "host_pc": self.host_pc,
                "f_type": self.f_type}