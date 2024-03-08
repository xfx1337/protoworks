from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QMenu

import UI.stylesheets

class QListEntry(QWidget):
    def __init__(self, text, mouse_left_callback=None, buttons=[]):
        super().__init__()

        self.mouse_left_callback = mouse_left_callback
        self.mouse_right_callback = None

        self.layout = QHBoxLayout()
        
        self.label = QLabel(text)
        self.layout.addWidget(self.label, 99)

        self.buttons = buttons

        for b in self.buttons:
            self.layout.addWidget(b, 1)
            self.layout.setAlignment(b, Qt.AlignmentFlag.AlignRight)
        

        self.setStyleSheet(UI.stylesheets.DEFAULT_BORDER_STYLESHEET)
        self.setLayout(self.layout)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            if self.mouse_left_callback != None:
                self.mouse_left_callback()
        
        elif e.button() == Qt.MouseButton.RightButton:
            if self.mouse_right_callback != None:
                self.mouse_right_callback()
        
        e.accept()