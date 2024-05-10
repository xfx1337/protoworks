from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QWidget, QSplitter, QLabel, QMessageBox, QCalendarWidget
from PySide6.QtCore import QTimer

from UI.stylesheets import *


from environment.environment import Environment
env = Environment()

from defines import *



class QFilesDrop(QFrame):
    def __init__(self, text, callback):
        super().__init__()

        self.callback = callback

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QHBoxLayout()

        self.label = QLabel(text)
        
        self.drop = QLabel()
        pixmap = env.templates_manager.backgrounds["drag-and-drop"]
        self.drop.setPixmap(pixmap)
        #self.drop.setScaledContents(True)
        self.layout.addWidget(self.drop)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        position = e.pos()
        e.setDropAction(Qt.CopyAction)
        e.accept()
        mimeData = e.mimeData()
        if mimeData.hasUrls():
            data = []
            for p in mimeData.urls():
                data.append(p.toString())
            self.callback(data)

    def mousePressEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            self.callback()