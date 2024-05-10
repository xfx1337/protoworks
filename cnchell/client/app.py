import ctypes

myappid = 'prototype.cnchell.cnchell.0.1' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

from PySide6.QtCore import QFile, QTextStream, QDir
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

import os, sys
sys.dont_write_bytecode = True # no pycache now

from UI.main_window import MainWindow
from UI.auth_window import AuthWindow

from environment.environment import Environment

from MainSignals import MainSignals

import utils

from UI.stylesheets import OVERALL_STYLESHEET

import locale
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

app = QApplication(sys.argv)

import qdarktheme

app.setStyleSheet(
    qdarktheme.load_stylesheet(
        theme="dark",
        custom_colors={
            "[dark]": {
                "primary": "#FF8102"
            }
        },
    )
)
app.setPalette(
    qdarktheme.load_palette(
        theme="dark",
        custom_colors={
            "[dark]": {
                "primary": "#FF8102"
            }
        },
    )
)


#qdarktheme.setup_theme()

# QDir.addSearchPath('dark', 'UI/breeze/pyqt6/dark')
# file = QFile("dark:stylesheet.qss")
# file.open(QFile.ReadOnly | QFile.Text)
# stream = QTextStream(file)
# app.setStyleSheet(stream.readAll())
# app.setStyle("Fusion")

# app.setStyle("Fusion")
# palette = QPalette()
# palette.setColor(QPalette.Window, QColor(32,33,36))
# palette.setColor(QPalette.WindowText, Qt.white)
# palette.setColor(QPalette.Base, QColor(25, 25, 25))
# palette.setColor(QPalette.AlternateBase, QColor(32,33,36))
# palette.setColor(QPalette.ToolTipBase, Qt.black)
# palette.setColor(QPalette.ToolTipText, Qt.white)
# palette.setColor(QPalette.Text, Qt.white)
# palette.setColor(QPalette.Button, QColor(32,33,36))
# palette.setColor(QPalette.ButtonText, QColor(138, 180, 247))
# palette.setColor(QPalette.BrightText, Qt.red)
# palette.setColor(QPalette.Link, QColor(42, 130, 218))
# palette.setColor(QPalette.Highlight, QColor(32, 33, 36))
# palette.setColor(QPalette.HighlightedText, QColor(138,180,247))
# app.setPalette(palette)
# app.setStyleSheet(OVERALL_STYLESHEET)

env = Environment()

env.main_signals = MainSignals()

window = MainWindow()
window.show()

auth_window = AuthWindow()
auth_window.show()

app.exec()