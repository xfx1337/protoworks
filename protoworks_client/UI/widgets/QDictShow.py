from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QMenu

import UI.stylesheets

class QDictShow(QWidget):
    def __init__(self, key, value, key_space=0):
        super().__init__()

        self.mouse_left_callback = None
        self.mouse_right_callback = None

        self.layout = QHBoxLayout()
        
        self.key = QLabel(key)
        self.value = QLabel(value)

        self.layout.addWidget(self.key, key_space)
        self.layout.addWidget(self.value, 100-key_space)

        #self.setStyleSheet(UI.stylesheets.DEFAULT_BORDER_STYLESHEET)
        self.setLayout(self.layout)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            if self.mouse_left_callback != None:
                self.mouse_left_callback()
        
        elif e.button() == Qt.MouseButton.RightButton:
            if self.mouse_right_callback != None:
                self.mouse_right_callback()