from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QWidget, QSplitter, QLabel, QMessageBox, QCalendarWidget, QCheckBox
from PySide6.QtCore import QTimer

from UI.widgets.QUserInput import QUserInput
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QDoubleLabel import QDoubleLabel


class QChooseManyCheckBoxes(QFrame):
    def __init__(self, text, elements):
        super().__init__()
        
        self.elements = elements

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel(text)
        self.label.setFixedSize(self.label.sizeHint())
        self.layout.addWidget(self.label)

        self.entries = []

        for e in self.elements:
            self.entries.append(QCheckBox(e))
            self.layout.addWidget(self.entries[-1])
    
    def get_selected(self):
        selected = []
        for i in range(len(self.entries)):
            if self.entries[i].isChecked():
                selected.append(self.extensions[i])
        
        return selected