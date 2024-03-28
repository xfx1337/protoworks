from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QProgressBar, QStyleOption, QStyle
from PySide6 import QtGui
import utils

from environment.environment import Environment
env = Environment()

import UI.stylesheets as stylesheets
from UI.widgets.QClickableLabel import QClickableLabel
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QListEntry import QListEntry

from environment.task_manager.statuses import *


import defines
    
class WorkerEntry(QWidget):
    def __init__(self, task, parent=None):
        super().__init__()
        self.task = task

        