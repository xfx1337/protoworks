import sys

from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QDialogButtonBox
from PySide6.QtGui import QIntValidator

from UI.widgets.QInitButton import QInitButton

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()


class QGetFromTo(QDialog):
    def __init__(self, title, text):
        super().__init__()

        self.fr = None
        self.to = None

        self.setWindowTitle(title)
        self.setWindowIcon(templates_manager.icons["cnchell"])

        self.layout = QVBoxLayout()

        self.hLayout = QHBoxLayout()

        self.message = QLabel(text)
        self.layout.addWidget(self.message)

        self.input_fr = QLineEdit()
        self.input_fr.setValidator(QIntValidator(0, 999999, self))

        self.input_to = QLineEdit()
        self.input_to.setValidator(QIntValidator(0, 999999, self))

        self.hLayout.addWidget(self.input_fr)
        self.hLayout.addWidget(self.input_to)

        self.layout.addLayout(self.hLayout)

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.No
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.ok)
        self.buttonBox.rejected.connect(self.cancel)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

    def ok(self):
        self.fr = self.input_fr.text()
        self.to = self.input_to.text()
        if self.fr == "" or self.to == "":
            self.fr = None
            self.to = None
        self.close()
    def cancel(self):
        self.fr = None
        self.to = None
        self.close()

    def closeEvent(self, event):
        event.accept()
