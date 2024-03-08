from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QMenu, QFileDialog

import UI.stylesheets

from UI.widgets.QInitButton import QInitButton

from environment.environment import Environment
env = Environment()


class QPathInput(QWidget):
    def __init__(self, text, path=None, parent=None):
        super().__init__()
        self.path = path
        self._parent = parent

        self.layout = QHBoxLayout()
        
        self.label = QLabel(text)
        self.layout.addWidget(self.label, 30)

        if self.path != None:
            self.path_button = QInitButton(self.path, callback=self.select_path)
        else:
            self.path_button = QInitButton("Выбрать", callback=self.select_path)

        self.layout.addWidget(self.path_button)

        self.setStyleSheet(UI.stylesheets.DEFAULT_BORDER_STYLESHEET)
        self.setLayout(self.layout)

    def select_path(self):
        fname = QFileDialog.getExistingDirectory(
            self,
            "Выбрать",
            "ProtoWorks",
        )
        if fname != "": 
            self.path = fname.replace("/", "\\") + "\\"
            self.path_button.setText(self.path)
            
        