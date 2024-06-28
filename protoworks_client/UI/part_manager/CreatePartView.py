import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QSplitter, QLabel, QMessageBox, QCalendarWidget
from PySide6.QtCore import QTimer

from UI.widgets.QUserInput import QUserInput
from UI.widgets.QInitButton import QInitButton

from UI.widgets.QUserChooseSearch import QUserChooseSearch

from environment.environment import Environment
env = Environment()

import utils

import time
from datetime import datetime as dt

class CreatePartView(QWidget):
    def __init__(self, project):
        super().__init__()

        self.project = project

        self.setWindowTitle(f"Создание детали")
        self.setWindowIcon(env.templates_manager.icons["proto"])
        #self.setFixedSize(QSize(800, 500))

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.name_input = QUserInput("Название: ")
        parents = env.net_manager.get_parts(self.project["id"])
        parents.append("Нет")
        self.parent_input = QUserChooseSearch("Деталь принадлежит: ", parents)

        self.deadline_label = QLabel("Срок сдачи")
        self.deadline_input = QCalendarWidget()
        self.deadline_input.setGridVisible(True)
        #self.deadline_input.selectionChanged.connect(self.calendar_date)
        
        self.create_btn = QInitButton("Создать", callback=self.submit)
        

        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.customer_input)
        self.layout.addWidget(self.description_input)
        self.layout.addWidget(self.deadline_label)
        self.layout.addWidget(self.deadline_input)
        self.layout.addWidget(self.create_btn)

        QTimer.singleShot(10, self.center_window)
    
    def center_window(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        event.accept()
    
    def submit(self):
        deadline = time.mktime(self.deadline_input.selectedDate().toPython().timetuple())
        ret = env.net_manager.projects.create(name=self.name_input.get_input(), 
            customer=self.customer_input.get_input(), 
            deadline=deadline, description=self.description_input.get_input())
        self.close()
        if self.callback != None:
            self.callback(ret) # project id