from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QMenu, QFileDialog

import UI.stylesheets

from UI.widgets.QInitButton import QInitButton

from environment.environment import Environment
env = Environment()

import os

class QPathInput(QWidget):
    def __init__(self, text, path=None, parent=None, selected_callback=None, open_path=None, limit_dir=None):
        super().__init__()
        self.path = path
        self._parent = parent
        self.open_path = open_path
        self.limit_dir = limit_dir

        self.selected_callback = selected_callback

        self.layout = QHBoxLayout()
        
        self.label = QLabel(text)
        self.layout.addWidget(self.label, 30)

        if self.path != None:
            self.path_button = QInitButton(self.path, callback=self.select_path)
        else:
            self.path_button = QInitButton("Выбрать", callback=self.select_path)

        self.layout.addWidget(self.path_button)

        self.setStyleSheet(UI.stylesheets.DEFAULT_BORDER_STYLESHEET)
        self.setLayout(self.layout)

    def check_dir_limit(self, dirName):
        dn = os.path.normpath(dirName)
        if not dn.startswith(self.limit_dir):
            self.dialog.setDirectory(self.limit_dir)

    def change_to_limit_dir(self):
        self.dialog.setDirectory(self.open_path)

    def select_path(self):
        if self.open_path == None:
            self.open_path = "C:\\"
        
        self.dialog = QFileDialog(self)
        self.dialog.setFileMode(QFileDialog.FileMode.Directory)
        if self.limit_dir != None:
            self.dialog.directoryEntered.connect(self.check_dir_limit)
            #self.dialog.setOption(QFileDialog.DontUseNativeDialog, True)

        self.dialog.exec()

        self.fname = self.dialog.selectedFiles()[0]

        if self.fname != "": 
            self.path = self.fname.replace("/", "\\") + "\\"
            self.path_button.setText(self.path)
        
            if self.selected_callback != None:
                self.selected_callback()
            
    def reset(self):
        self.path_button.setText("Выбрать")
        self.path = None

    def set_path(self, path):
        self.path = path
        self.path_button.setText(self.path)