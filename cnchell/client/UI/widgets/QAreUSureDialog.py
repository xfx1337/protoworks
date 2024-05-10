import sys

from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QLabel, QLineEdit, QVBoxLayout, QDialogButtonBox

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()


class QAreUSureDialog(QDialog):
    def __init__(self, text):
        super().__init__()

        self.setWindowIcon(templates_manager.icons["cnchell"])
        self.setWindowTitle("Вы уверены?")

        self.layout = QVBoxLayout()

        self.message = QLabel(text)
        self.layout.addWidget(self.message)

        self.input = QLineEdit()
        self.layout.addWidget(self.input)

        QBtn = QDialogButtonBox.StandardButton.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout.addWidget(self.buttonBox)


        self.setLayout(self.layout)