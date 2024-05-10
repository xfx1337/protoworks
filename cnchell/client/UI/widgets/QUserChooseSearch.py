from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QLineEdit, QComboBox, QCompleter

class QUserChooseSearch(QWidget):
    def __init__(self, text, items, corner_align = False):
        super().__init__()

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.label = QLabel(text)
        
        self.combo = QComboBox()
        self.combo.addItems(items)
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.combo.completer().setCompletionMode(QCompleter.PopupCompletion)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo)

        if corner_align:
            self.layout.setAlignment(self.input, Qt.AlignmentFlag.AlignRight)

    def get_input(self):
        return self.input.text()

    def set_input(self, text):
        self.input.setText(text)