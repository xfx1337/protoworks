from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QLineEdit

class QUserInput(QWidget):
    def __init__(self, text, corner_align = False, password=False):
        super().__init__()

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.label = QLabel(text)
        self.input = QLineEdit()

        if password:
            self.input.setEchoMode(QLineEdit.Password)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)

        if corner_align:
            self.layout.setAlignment(self.input, Qt.AlignmentFlag.AlignRight)

    def get_input(self):
        return self.input.text()

    def set_input(self, text):
        self.input.setText(text)