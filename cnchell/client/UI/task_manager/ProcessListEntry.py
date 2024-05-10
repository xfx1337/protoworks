from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QProgressBar, QStyleOption, QStyle, QFrame
from PySide6 import QtGui
import utils

from environment.environment import Environment
env = Environment()

import UI.stylesheets as stylesheets
from UI.widgets.QClickableLabel import QClickableLabel
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QListEntry import QListEntry
from UI.widgets.QEasyScroll import QEasyScroll

from UI.task_manager.TaskListEntry import TaskListEntry


from environment.task_manager.statuses import *


import defines
    
class ProcessListEntry(QFrame):
    def __init__(self, process, parent=None):
        super().__init__()
        self.process = process
        self.process.signals.process_status_changed.connect(self.on_status_change)
        self._parent = parent

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.main_layout = QVBoxLayout()
        self.layout = QHBoxLayout()

        self.label = QLabel(process.name)
        self.layout.addWidget(self.label, 30)

        self.setStyleSheet(stylesheets.DEFAULT_BORDER_STYLESHEET)
        
        self.prog_bar = QProgressBar(self)
        #self.prog_bar.setGeometry(50, 100, 250, 30)
        self.prog_bar.setValue(self.process.progress.get_percentage())
        
        self.process.progress.signals.progress_changed.connect(self.update_progress)

        self.layout.addWidget(self.prog_bar)

        self.open_more_btn = QInitButton("", callback=self.open_more)
        self.open_more_btn.setIcon(env.templates_manager.icons["down_arrow"])

        self.layout.addWidget(self.open_more_btn)


        self.main_layout.addLayout(self.layout)

        self.scrollable = QEasyScroll()
        self.scrollWidgetLayout = self.scrollable.scrollWidgetLayout
        self.scrollWidget = self.scrollable.scrollWidget
        self.tasks_entries = []


        self.main_layout.addWidget(self.scrollable)
        self.scrollable.hide()
        self.showing_scrollable = False

        self.setLayout(self.main_layout)

        if self.process.status == ENDED or self.process.status == CANCELED or self.process.status == FAILED:
            if self.prog_bar.parent != None:
                self.prog_bar.setParent(None)
    

        self.on_status_change()

    def open_more(self):
        if self.showing_scrollable:
            self.scrollable.hide()
        else:
            self.scrollable.show()
        
        self.showing_scrollable = not self.showing_scrollable

        for p in self.tasks_entries:
            if p.parent() != None:
                p.setParent(None)

        self.tasks_entries = []

        tasks_sorted = sorted(self.process.tasks, key=lambda key: (self.process.tasks[key].time_started, self.process.tasks[key].name))

        for i in range(len(tasks_sorted)):
            task = self.process.tasks[tasks_sorted[i]]
            p = TaskListEntry(task, parent=self)
            self.scrollWidgetLayout.insertWidget(i, p)
            self.scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)

            self.tasks_entries.append(p)


    def update_progress(self, percentage):
        self.prog_bar.setValue(percentage)
    
    def on_status_change(self):
        if self.process.status == WAITING:
            self.setStyleSheet(stylesheets.CYAN_HIGHLIGHT)

        if self.process.status == ENDED:
            self.label.setStyleSheet(stylesheets.GREEN_HIGHLIGHT)
        elif self.process.status == FAILED:
            self.label.setStyleSheet(stylesheets.RED_HIGHLIGHT)
        elif self.process.status == CANCELED:
            self.label.setStyleSheet(stylesheets.YELLOW_HIGHLIGHT)
        
        if self.process.status != RUNNING and self.process.status != WAITING:
            self.prog_bar.hide()
            self.setStyleSheet(stylesheets.DISABLE_BORDER)

        

        #if self.prog_bar.parent != None:
        #    self.prog_bar.setParent(None)
        
    def mousePressEvent(self, QMouseEvent):
        info = f"""Процесс: {self.process.name} 
        Состояние: {TASK_STATUS_TRANSLATIONS[self.process.status]}
        id: {self.process.id}
        Ошибка: {"Нет" if self.process._error == None else (str(repr(self.process._error)) + " Функция: " + str(self.process._error_data["func_name"]))}
        Время запуска: {utils.time_by_unix(self.process.time_started)}
        Время завершения: {"Неизвестно" if self.process.time_stopped == None else utils.time_by_unix(self.process.time_stopped)}
        """

        utils.message(info, "Информация о задаче")