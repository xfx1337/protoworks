import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QScrollArea, QVBoxLayout, QMenu, QWidget, QSplitter, QLabel, QFrame, QCheckBox, QMessageBox, QCalendarWidget, QGridLayout, QLineEdit
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag

from UI.widgets.QUserInput import QUserInput
from UI.widgets.QInitButton import QInitButton

from UI.widgets.QUserChooseSearch import QUserChooseSearch
from UI.widgets.QSelectOneFromList import QSelectOneFromList

from UI.widgets.QEasyScroll import QEasyScroll

from UI.widgets.QAskForNumberDialog import QAskForNumberDialog
from UI.widgets.QAreUSureDialog import QAreUSureDialog

import UI.stylesheets

from environment.environment import Environment
env = Environment()

import utils

import os, subprocess

from environment.file_manager.File import File

from defines import *

import time
from datetime import datetime as dt

class PartListEntry(QFrame):
    def __init__(self, project, part, manager, _disable_context_menu=False):
        super().__init__()

        self.project = project
        self.part = part
        self.manager = manager

        self._disable_context_menu = _disable_context_menu

        if not _disable_context_menu:
            self.menu = QMenu(self)
            self.menu.setStyleSheet(UI.stylesheets.DEFAULT_BORDER_STYLESHEET)
            action_open = self.menu.addAction("Открыть")
            action_open_dir = self.menu.addAction("Открыть директорию")
            action_change_need_count = self.menu.addAction("Изменить количество(нужно)")
            action_change_done_count = self.menu.addAction("Изменить количество(есть)")
            action_change_status = self.menu.addAction("Изменить состояние")
            action_properties = self.menu.addAction("Больше информации")
            action_work = self.menu.addAction("Запустить на станках вне очереди")

            action_open.triggered.connect(self.open)
            action_open_dir.triggered.connect(self.open_dir)
            action_change_need_count.triggered.connect(self.change_need_count)
            action_change_done_count.triggered.connect(self.change_done_count)
            action_change_status.triggered.connect(self.change_status)
            action_properties.triggered.connect(self.show_properties)
            action_work.triggered.connect(self.start_work)

        self.modified = False

        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        if self.part["status"] == PART_DONE:
            self.setStyleSheet(UI.stylesheets.GREEN_BACKGROUND_STYLESHEET)

        self.left_layout = QVBoxLayout()
        self.setLayout(self.left_layout)

        self.overview = QHBoxLayout()
        self.name = QLabel("Название: " + self.part["name"])
        self.status = QLabel("Статус: " + PART_STATUS_TRANSLATIONS[self.part["status"]])
        self.overview.addWidget(self.name)
        self.overview.addWidget(self.status)

        self.counts = QHBoxLayout()
        self.need_c = QLabel("Нужно: " + str(self.part["count_need"]) + " шт.")
        self.done_c = QLabel("Готово: " + str(self.part["count_done"])+ " шт.")
        self.counts.addWidget(self.need_c)
        self.counts.addWidget(self.done_c)

        self.path_v = QLabel("Путь: " + utils.remove_path(self.project["server_path"], part["path"]))

        idx = part["id"]
        self.idx_v = QLabel(f"ID: PW{str(idx)}")

        if env.part_manager.check_part_up_to_date_with_origin(self.project, part) == 0:
            self.setStyleSheet(UI.stylesheets.YELLOW_HIGHLIGHT)
            self.setToolTip("Оригинальный файл детали был обновлён")
            self.modified = True

        elif env.part_manager.check_part_up_to_date_with_origin(self.project, part) == -1:
            self.setStyleSheet(UI.stylesheets.RED_HIGHLIGHT)
            self.setToolTip("Оригинальный файл детали был удалён")

        formats = []

        files = env.part_manager.get_available_part_files_by_id(self.project, idx)

        for f in files:
            formats.append(f.path.split(".")[-1])
        self.formats = QLabel("Форматы: " + " ".join(formats))
        self.formats.setWordWrap(True)

        self.left_layout.addLayout(self.overview)
        self.left_layout.addLayout(self.counts)
        self.left_layout.addWidget(self.path_v)
        self.left_layout.addWidget(self.formats)
        self.left_layout.addWidget(self.idx_v)

        self.selected = False

        self.dragStartPosition = self.pos()

    def update_view(self):
        idx = self.part["id"]
        self.path_v.setText("Путь: " + utils.remove_path(self.project["server_path"], self.part["path"]))
        self.need_c.setText("Нужно: " + str(self.part["count_need"]) + " шт.")
        self.done_c.setText("Готово: " + str(self.part["count_done"])+ " шт.")
        self.name.setText("Название: " + self.part["name"])
        self.status.setText("Статус: " + PART_STATUS_TRANSLATIONS[self.part["status"]])

        if self.part["status"] == PART_DONE:
            self.setStyleSheet(UI.stylesheets.GREEN_BACKGROUND_STYLESHEET)

        if self.part["count_need"] == self.part["count_done"] and self.part["count_need"] != 0:
            self.setStyleSheet(UI.stylesheets.GREEN_BACKGROUND_STYLESHEET)

        formats = []
        files = env.part_manager.get_available_part_files_by_id(self.project, idx)
        for f in files:
            formats.append(f.path.split(".")[-1])
        self.formats.setText("Форматы: " + " ".join(formats))

        if not env.part_manager.check_part_up_to_date_with_origin(self.project, self.part):
            self.setStyleSheet(UI.stylesheets.YELLOW_HIGHLIGHT)
            self.setToolTip("Оригинальный файл детали был обновлён")
            self.modified = True

    def open(self):
        client_path = utils.remove_path(self.project["server_path"], self.part["path"])
        project_path = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"])
        if project_path[-1] != "\\":
            project_path += "\\"
        path = str(os.path.join(os.path.abspath(project_path), client_path)) # fucken python optimizer breaking
        os.startfile(path, 'open')

    def open_dir(self):
        client_path = utils.remove_path(self.project["server_path"], self.part["path"])
        project_path = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"])
        if project_path[-1] != "\\":
            project_path += "\\"
        path = str(os.path.join(os.path.abspath(project_path), client_path)) # fucken python optimizer breaking
        path = "\\".join(path.split("\\")[:-1])
        subprocess.Popen(f'explorer "{path}"')
    
    def change_need_count(self):
        dlg = QAskForNumberDialog(text = "Укажите количество деталей, которое будет установлено как 'нужно'", title="Выбор")
        dlg.exec()
        answer = dlg.answer
        if answer != None:
            self.part["count_need"] = int(answer)
            env.part_manager.update_parts(self.project, [self.part])
            self.update_view()

    def change_done_count(self):
        dlg = QAskForNumberDialog(text = "Укажите количество деталей, которое будет установлено как 'есть'", title="Выбор")
        dlg.exec()
        answer = dlg.answer
        if answer != None:
            self.part["count_done"] = int(answer)
            env.part_manager.update_parts(self.project, [self.part])
            self.update_view()

    def change_status(self):
        dlg = QSelectOneFromList("Выберите", list(PART_STATUS_TRANSLATIONS_BACKWARDS.keys()), self.changed_status)
        dlg.show()

    def changed_status(self, answer):
        if answer != None:
            answer = PART_STATUS_TRANSLATIONS_BACKWARDS[answer]
            self.part["status"] = int(answer)
            env.part_manager.update_parts(self.project, [self.part])
            self.update_view()

    def show_properties(self):
        pass
    
    def start_work(self):
        pass

    def contextMenuEvent(self, event):
        if not self._disable_context_menu:
            self.menu.exec(event.globalPos())
        else:
            event.accept()

    def mouseMoveEvent(self, event):
        if not event.buttons() == Qt.LeftButton:
            return
        if ((event.pos() - self.dragStartPosition).manhattanLength()
            < QApplication.startDragDistance()):
            return
        self.selected = True
        self.check_selected()
        drag = QDrag(self)
        drag.setPixmap(env.templates_manager.icons["drag2"].pixmap(256,256))
        mimeData = QMimeData()
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - self.rect().topLeft())

        dropAction = drag.exec_(Qt.CopyAction) 

    def mousePressEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            if self.selected:
                self.dragStartPosition = e.pos()
            self.selected = not self.selected
            self.check_selected()

    def check_selected(self):
        if self.selected:
            self.setStyleSheet(UI.stylesheets.SELECTED_STYLESHEET)
        else:
            if not self.modified:
                if self.part["status"] == PART_DONE or (self.part["count_need"] == self.part["count_done"] and self.part["count_need"] != 0):
                    self.setStyleSheet(UI.stylesheets.GREEN_BACKGROUND_STYLESHEET)
                else:
                    self.setStyleSheet(UI.stylesheets.UNSELECTED_STYLESHEET)
            else:
                self.setStyleSheet(UI.stylesheets.YELLOW_HIGHLIGHT)