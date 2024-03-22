import os
import ezdxf

from defines import *

def get_version(file):
    path = get_path(file)
    frt = format_by_file(path)

    if frt == "dxf":
        doc = ezdxf.readfile(path)
        return doc.dxfversion

    else:
        return "N/A"

def get_path(file):
    if type(file) == type(str()):
        return file
    elif type(file) == type(dict()):
        if "path" in file:
            return file["path"]
        elif "file" in file:
            return file["file"]["path"]