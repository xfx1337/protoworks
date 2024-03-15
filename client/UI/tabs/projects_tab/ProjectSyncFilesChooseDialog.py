import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QStyleOption, QStyle
from PySide6 import QtGui

from UI.widgets.QEasyScroll import QEasyScroll
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QListEntry import QListEntry

import UI.stylesheets

import utils

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()

from UI.widgets.QFilesListSureDialog import QFilesListSureWidget

class ProjectSyncFilesChooseDialog(QDialog):
    def __init__(self, files_send, files_get, path_dont_show_server=None, path_dont_show_client=None, sure=None):
        super().__init__()
        self.widget1 = QFilesListSureWidget(files_send, [], "Отправление файлов на сервер", "Отправить", "Проигнорировать", path_dont_show_client)
        self.widget2 = QFilesListSureWidget(files_get, [], "Получение файлов с сервера", "Получить", "Проигнорировать", path_dont_show_server)
        self.sure = sure

        self.layout = QVBoxLayout()

        self.setMinimumSize(QSize(700, 500))
        self.setWindowTitle("Синхронизация")
        self.setWindowIcon(templates_manager.icons["proto"])

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.cancel)

        self.layout.addWidget(self.widget1)
        self.layout.addWidget(self.widget2)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

    def closeEvent(self, event):
        if self.sure != None:
            if self.sure[0] == None:
                self.sure[0] = False
        event.accept()

    def accept(self):
        if self.sure != None:
            self.sure[0] = True # fuck that's pointer system
        self.close()
    
    def cancel(self):
        if self.sure != None:
            self.sure[0] = False
        self.close()
