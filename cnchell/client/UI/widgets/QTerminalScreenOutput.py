from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox, QPlainTextEdit
from PySide6.QtCore import QTimer

from PySide6.QtCore import Signal, QObject

from UI.stylesheets import COLORS_TO_HTML_RGB

class ScreenSignals(QObject):
    append = Signal(dict)
    clear = Signal()

class QTerminalScreenOutput(QWidget):
    def __init__(self):
        super().__init__()
    
        self.layout = QVBoxLayout()

        self.signals = ScreenSignals()
        self.signals.append.connect(self.append)
        self.signals.clear.connect(self.clear)

        self.screen = QPlainTextEdit()
        self.screen.setReadOnly(True)

        self.layout.addWidget(self.screen)
        self.setLayout(self.layout)

    def append(self, string_dc):
        #self.screen.blockSignals(True)
        if "color" in string_dc:
            color = COLORS_TO_HTML_RGB[string_dc["color"]]
        else:
            color = string_dc["rgb_color"]

        string = string_dc["string"]
        self.screen.appendHtml(f"<p style=\"color:{color};white-space:pre\">" + string + "</p>")
        #self.screen.blockSignals(False)
    
    def clear(self):
        #self.screen.blockSignals(True)
        self.screen.clear()
        #self.screen.blockSignals(False)