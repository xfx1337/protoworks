from singleton import singleton

import exceptions

import pythoncom
import win32com

import time
import threading

# KOMPAS 3D
@singleton
class Files:
    def __init__(self, kompas3d):
        self.kompas3d = kompas3d
        self.env = self.kompas3d.env

    def init_api(self):
        pass

    def open(self, path):
        doc = self.kompas3d.app.Documents.Open(PathName=path,
                                   Visible=True,
                                   ReadOnly=True)
        return doc

    def convert(self, fr, to, settings=None):
        if fr.split(".")[-1] in ["m3d", "frw"]:
            doc = self.open(fr)
            doc.SaveAs(to)
            doc.Close(self.kompas3d.consts.kdDoNotSaveChanges)

        