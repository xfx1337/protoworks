import sys

from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QDialogButtonBox
from PySide6.QtGui import QIntValidator

from UI.widgets.QInitButton import QInitButton

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()


class QAskForLineDialog(QDialog):
    def __init__(self, text, title):
        super().__init__()

        self.answer = ""

        self.setWindowTitle(title)
        self.setWindowIcon(templates_manager.icons["cnchell"])

        self.layout = QVBoxLayout()

        self.message = QLabel(text)
        self.layout.addWidget(self.message)

        self.input = QLineEdit()
        #self.input.setValidator(QIntValidator(0, 999999, self))

        self.layout.addWidget(self.input)

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.No
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.ok)
        self.buttonBox.rejected.connect(self.cancel)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

    def ok(self):
        self.answer = self.input.text()
        if self.answer == "":
            self.answer = ""
        self.close()
    def cancel(self):
        self.answer = ""
        self.close()

    def closeEvent(self, event):
        event.accept()
