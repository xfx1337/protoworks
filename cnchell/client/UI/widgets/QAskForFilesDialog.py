import sys

from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QLabel, QLineEdit, QVBoxLayout, QDialogButtonBox, QFileDialog
from PySide6 import QtGui

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()


class QAskForFilesDialog(QDialog):
    def __init__(self, text, project_id=None, callback_yes=None, callback_no=None, only_one_file=False):
        super().__init__()

        self.project_id = project_id

        self.callback_yes = callback_yes

        self.callback_no = callback_no

        self.only_one_file = only_one_file

        self.setWindowTitle("Загрузка файлов")
        self.setWindowIcon(templates_manager.icons["cnchell"])

        self.layout = QVBoxLayout()

        self.message = QLabel(text)
        self.layout.addWidget(self.message)

        QBtn = QDialogButtonBox.StandardButton.Open | QDialogButtonBox.StandardButton.No
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.open_files)
        self.buttonBox.rejected.connect(self.close_and_check_callback)
        self.layout.addWidget(self.buttonBox)


        self.setLayout(self.layout)
    
    def open_files(self):
        if not self.only_one_file:
            fnames = QFileDialog.getOpenFileNames(
                self,
                "Выбрать",
                "CNCHell",
            )
        else:
            fnames = QFileDialog.getOpenFileName(
                self,
                "Выбрать",
                "CNCHell",
            )
            
            
        fnames = fnames[0]
        if not self.only_one_file:
            for i in range(len(fnames)):
                if fnames[i] != "":
                    fnames[i] = fnames[i].replace("/", "\\")
        else:
            fnames = fnames.replace("/", "\\")

        self.close()
        if self.callback_yes != None:
           if self.project_id != None:
               self.callback_yes(fnames, self.project_id)
           else:
               self.callback_yes(fnames)
        
    def close_and_check_callback(self):
        self.close()
        if self.callback_no != None:
            self.callback_no()