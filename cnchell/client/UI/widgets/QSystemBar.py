from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QStyleOption, QStyle
from PySide6 import QtGui

from UI.widgets.QClickableLabel import QClickableLabel
from UI.task_manager.task_manager_window import TaskManagerWindow

import UI.stylesheets

from environment.task_manager.statuses import *

import types

def paintEvent(self, pe):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        s = self.style()
        s.drawPrimitive(QStyle.PE_Widget, opt, p, self)

class QSystemBar(QWidget):
    def __init__(self):
        super().__init__()

        self.setAttribute(Qt.WA_StyleSheet)
        self.setAttribute(Qt.WA_StyledBackground)  

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)

        self.label = QLabel("CNCHell")
        
        self.operation = QClickableLabel("Нет операции", callback=self.show_task_manager)
        
        self.taskmanager = TaskManagerWindow()

        self.layout.addWidget(self.label)
        self.layout.setAlignment(self.label, Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.operation)
        self.layout.setAlignment(self.operation, Qt.AlignmentFlag.AlignRight)

        self.setLayout(self.layout)

    def set_operation(self, text):
        self.operation.setText(text)
        self.update()

    def set_operation_color_by_task_status(self, status):
        if status == ENDED:
            self.operation.setStyleSheet(UI.stylesheets.NO_HIGHLIGHT)
        if status == FAILED:
            self.operation.setStyleSheet(UI.stylesheets.RED_HIGHLIGHT)
        elif status == CANCELED:
            self.operation.setStyleSheet(UI.stylesheets.YELLOW_HIGHLIGHT)
        elif status == WAITING:
            self.operation.setStyleSheet(UI.stylesheets.CYAN_HIGHLIGHT)
        #elif status == RUNNING:
        #    self.operation.setStyleSheet(UI.stylesheets.PURPLE_HIGHLIGHT)

        self.update()

    def show_task_manager(self):
        self.taskmanager.show()
        self.taskmanager.showNormal()
        self.taskmanager.raise_()
        self.taskmanager.activateWindow()