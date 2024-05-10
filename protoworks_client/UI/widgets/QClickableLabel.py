from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel

class QClickableLabel(QLabel):
    def __init__(self, text, callback=None, right_button_callback=None):
        super().__init__(text)
        self.mouse_left_callback = callback
        self.mouse_right_callback = right_button_callback
    
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            if self.mouse_left_callback != None:
                self.mouse_left_callback()
        
        elif e.button() == Qt.MouseButton.RightButton:
            if self.mouse_right_callback != None:
                self.mouse_right_callback()