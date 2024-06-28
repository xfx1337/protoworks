from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication
import os

import utils

from environment.environment import Environment
env = Environment()

import UI.stylesheets as stylesheets
from UI.widgets.QClickableLabel import QClickableLabel
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QListEntry import QListEntry

import defines

from UI.widgets.QEasyScroll import QEasyScroll
from UI.widgets.QListEntry import QListEntry

class QSelectOneFromList(QWidget):
    def __init__(self, text, c_list, callback):
        super().__init__()

        self.c_list = c_list
        self.callback = callback
        self.entries = []

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setWindowTitle("Выбор")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        #self.setFixedSize(QSize(400, 600))

        self.label = QLabel(text)

        self.scrollable = QEasyScroll()

        self.scrollWidgetLayout = self.scrollable.scrollWidgetLayout
        self.scrollWidget = self.scrollable.scrollWidget

        self.layout.addWidget(self.scrollable)

        self.update_data()
    
    def update_data(self):
        for p in self.entries:
            if p.parent() != None:
                p.setParent(None)

        self.entries = []

        for i in range(len(self.c_list)):
            p = QListEntry(self.c_list[i], mouse_left_callback=lambda val=i: self.choose(int(val)))
            self.scrollWidgetLayout.insertWidget(i, p)
            self.scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)

            self.entries.append(p)
    
    def choose(self, i):
        self.close()
        self.callback(self.c_list[i])