from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QLineEdit, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox, QPlainTextEdit
from PySide6.QtCore import QTimer

from PySide6.QtCore import Signal, QObject

from UI.stylesheets import COLORS_TO_HTML_RGB

import json
import time

import requests
import websocket

from UI.widgets.QInitButton import QInitButton

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()


class ScreenSignals(QObject):
    append = Signal(dict)
    clear = Signal()

class QWebTerminal(QWidget):
    def __init__(self, host, apikey):
        super().__init__()
    
        self.setWindowTitle(f"Терминал. Не работает.")
        self.setWindowIcon(templates_manager.icons["cnchell"])

        self.layout = QVBoxLayout()

        self.signals = ScreenSignals()
        self.signals.append.connect(self.append)
        self.signals.clear.connect(self.clear)

        self.screen = QPlainTextEdit()
        self.screen.setReadOnly(True)

        self.h_layout = QHBoxLayout()

        self.input = QLineEdit()
        self.submit = QInitButton("Отправить", self.submit)
        self.h_layout.addWidget(self.input)
        self.h_layout.addWidget(self.submit)

        self.layout.addWidget(self.screen)
        self.layout.addLayout(self.h_layout)

        self.setLayout(self.layout)

    def append_signal_handler(self, string):
        print(string)
        self.signals.append.emit(string)

    def append(self, string):
        self.screen.appendString(string)
    
    def clear(self):
        self.screen.clear()

    def submit(self):
        self.client.send(self.input.text())
        self.input.setText("")