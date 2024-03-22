import sys

from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QLabel, QLineEdit, QVBoxLayout, QDialogButtonBox, QFileDialog
from PySide6 import QtGui

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()


class QAskForDirectoryDialog(QDialog):
    def __init__(self, text, project_id=None, callback_yes=None, callback_no=None):
        super().__init__()

        self.project_id = project_id

        self.callback_yes = callback_yes

        self.callback_no = callback_no

        self.setWindowTitle("Загрузка директории проекта")
        self.setWindowIcon(templates_manager.icons["proto"])

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
        fname = QFileDialog.getExistingDirectory(
            self,
            "Выбрать",
            "ProtoWorks",
        )
        if fname != "":
            fname = fname.replace("/", "\\") + "\\"

        self.close()
        if self.callback_yes != None:
           if self.project_id != None:
               self.callback_yes(fname, self.project_id)
           else:
               self.callback_yes(fname)
        
    def close_and_check_callback(self):
        self.close()
        if self.callback_no != None:
            self.callback_no()