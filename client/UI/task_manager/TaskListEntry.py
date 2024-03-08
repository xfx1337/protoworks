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
    
class TaskListEntry(QWidget):
    def __init__(self, task, parent=None):
        super().__init__()
        self.task = task
        self.task.signals.task_status_changed.connect(self.on_status_change)
        self._parent = parent

        self.layout = QHBoxLayout()

        self.label = QLabel(task.name)
        self.layout.addWidget(self.label, 30)

        self.setStyleSheet(stylesheets.DEFAULT_BORDER_STYLESHEET)
        
        self.prog_bar = QProgressBar(self)
        #self.prog_bar.setGeometry(50, 100, 250, 30)
        self.prog_bar.setValue(self.task.progress.get_percentage())
        
        self.task.progress.signals.progress_changed.connect(self.update_progress)

        self.layout.addWidget(self.prog_bar)

        self.setLayout(self.layout)

        if self.task.status == ENDED or self.task.status == CANCELED or self.task.status == FAILED:
            if self.prog_bar.parent != None:
                self.prog_bar.setParent(None)
        
        self.on_status_change()

    def update_progress(self, percentage):
        self.prog_bar.setValue(percentage)
    
    def on_status_change(self):
        if self.task.status == WAITING:
            self.setStyleSheet(stylesheets.CYAN_HIGHLIGHT)

        if self.task.status == ENDED:
            self.label.setStyleSheet(stylesheets.GREEN_HIGHLIGHT)
        elif self.task.status == FAILED:
            self.label.setStyleSheet(stylesheets.RED_HIGHLIGHT)
        elif self.task.status == CANCELED:
            self.label.setStyleSheet(stylesheets.YELLOW_HIGHLIGHT)
        
        if self.task.status != RUNNING and self.task.status != WAITING:
            self.prog_bar.hide()
            self.setStyleSheet(stylesheets.DISABLE_BORDER)

        

        #if self.prog_bar.parent != None:
        #    self.prog_bar.setParent(None)
        
    def mousePressEvent(self, QMouseEvent):
        info = f"""Задача: {self.task.name} 
        Статус: {TASK_STATUS_TRANSLATIONS[self.task.status]}
        id: {self.task.id}
        Ошибка: {"Нет" if self.task._error == None else repr(self.task._error)}
        Время запуска: {utils.time_by_unix(self.task.time_started)}
        Время завершения: {"Неизвестно" if self.task.time_stopped == None else utils.time_by_unix(self.task.time_stopped)}
        """

        utils.message(info, "Информация о задаче")