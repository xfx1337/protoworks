from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QScrollArea, QHBoxLayout, QVBoxLayout, QHBoxLayout, QWidget, QDialog, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox
from PySide6.QtCore import QTimer

import os, shutil

from ping3 import ping, verbose_ping

import utils
from defines import *

class ScrollWidget(QWidget):
    def __init__(self, callback, disable_drop=False):
        super().__init__()
        self.disable_drop = disable_drop
        if not disable_drop:
            self.setAcceptDrops(True)
        self.callback = callback

    def dragEnterEvent(self, e):
        if not self.disable_drop:
            e.accept()

    def dropEvent(self, e):
        if not self.disable_drop:
            position = e.pos()
            e.setDropAction(Qt.CopyAction)
            e.accept()
            self.callback(e.mimeData().text())

    def mousePressEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            if not self.disable_drop:
                self.callback()


class QEasyScrollDrop(QScrollArea):
    def __init__(self, callback, vertical=True, horizontal=False, disable_drop=False):
        super().__init__()
        if vertical:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        if horizontal:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.callback = callback

        if vertical:
            self.scrollWidgetLayout = QVBoxLayout()
        if horizontal:
            self.scrollWidgetLayout = QHBoxLayout()
        self.scrollWidgetLayout.setSpacing(0)
        self.scrollWidget = ScrollWidget(callback, disable_drop=disable_drop)
        self.scrollWidget.setLayout(self.scrollWidgetLayout)
        self.setWidget(self.scrollWidget)

        self.scrollWidgetLayout.addStretch()
