from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QMenu, QFrame

import UI.stylesheets

class QDoubleLabel(QFrame):
    def __init__(self, text1, text2, mouse_left_callback=None, buttons=[]):
        super().__init__()

        self.mouse_left_callback = mouse_left_callback
        self.mouse_right_callback = None

        self.layout = QHBoxLayout()
        
        self.label1 = QLabel(text1)
        self.label1.setStyleSheet(UI.stylesheets.DISABLE_BORDER)
        self.layout.addWidget(self.label1, 30)

        self.buttons = buttons

        for b in self.buttons:
            self.layout.addWidget(b, 1)
            self.layout.setAlignment(b, Qt.AlignmentFlag.AlignRight)
        
        self.label2 = QLabel(text2)
        self.label2.setStyleSheet(UI.stylesheets.DISABLE_BORDER)
        self.layout.addWidget(self.label2)
        #self.layout.setAlignment(self.label2, Qt.AlignmentFlag.AlignRight)

        self.setStyleSheet(UI.stylesheets.DEFAULT_BORDER_STYLESHEET)

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.setLayout(self.layout)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            if self.mouse_left_callback != None:
                self.mouse_left_callback()
        
        elif e.button() == Qt.MouseButton.RightButton:
            if self.mouse_right_callback != None:
                self.mouse_right_callback()
        
        e.accept()