import os, time

import json

from defines import *

from environment.file_manager.File import File

import environment.part_manager.part_utils as part_utils

class Part:
    def __init__(self, file=None, p_type=None, version=None, JSON=None):
        self.file = file
        self.p_type = p_type
        self.version = version

        if self.p_type == None:
            if self.file != None and self.file.host_pc == CUR_CLIENT:
                self.p_type = format_by_file(self.file)
        if self.version == None:
            if self.file != None and self.file.host_pc == CUR_CLIENT:
                self.version = part_utils.get_version(self)


        if JSON != None:
            self.from_JSON(JSON)
    
    def from_JSON_part(self, json):
        self.p_type = json["p_type"]
        self.file = File(JSON=json["file"])

    def to_dict(self):
        return {"file": self.file.to_dict(),
        "p_type": self.p_type}