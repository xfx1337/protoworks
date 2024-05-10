import sys

from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QDialogButtonBox

from UI.widgets.QInitButton import QInitButton

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()


class QYesOrNoDialog(QDialog):
    def __init__(self, text):
        super().__init__()

        self.answer = None

        self.setWindowTitle("Выбор")
        self.setWindowIcon(templates_manager.icons["cnchell"])

        self.layout = QVBoxLayout()

        self.message = QLabel(text)
        self.layout.addWidget(self.message)


        self.btn_yes = QInitButton("Да", callback=self.yes)
        self.btn_no = QInitButton("Нет", callback=self.no)

        self.btn_box_layout = QHBoxLayout()
        self.btn_box_layout.addWidget(self.btn_yes)
        self.btn_box_layout.addWidget(self.btn_no)

        self.layout.addLayout(self.btn_box_layout)

        self.setLayout(self.layout)
    
    def yes(self):
        self.answer = True
        self.close()
    
    def no(self):
        self.answer = False
        self.close()

    def closeEvent(self, event):
        if self.answer == None:
            self.answer = False
        event.accept()
