from PySide6 import QtGui

from singleton import singleton

import exceptions

import os

@singleton
class TemplatesManager:
    def __init__(self, env=None):
        self.env = env
        self.path = "UI\\templates"

        self.icons = {}
        self.backgrounds = {}


    def load_templates(self):
        self.load_icons()
        self.load_backgrounds()

    def load_icons(self):
        icons = {}
        for f in [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.path) for f in filenames]:
            icons[f.split("\\")[-1].split(".")[0]] = QtGui.QIcon(f)
        self.icons = icons
        
    def load_backgrounds(self):
        backgrounds = {}
        for f in [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.path) for f in filenames]:
            backgrounds[f.split("\\")[-1].split(".")[0]] = QtGui.QPixmap(f)

        self.backgrounds = backgrounds