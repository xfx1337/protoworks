from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt

class QInitButton(QPushButton):
    def __init__(self, label, callback=None, checkable=True, _right_click_callback=None):
        super().__init__()
        self.callback = callback
        self.right_click_callback = _right_click_callback
        self.setText(label)
        self.setCheckable(checkable)
        
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.MouseButton.LeftButton:
            self.callback()
        elif QMouseEvent.button() == Qt.MouseButton.RightButton:
            self.right_click_callback()