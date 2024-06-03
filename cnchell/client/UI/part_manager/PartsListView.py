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

from UI.part_manager.PartListEntry import PartListEntry

from UI.widgets.QGetFromTo import QGetFromTo
from UI.widgets.QFilesDrop import QFilesDrop

import UI.stylesheets

from environment.environment import Environment
env = Environment()

import utils

import os, subprocess

from environment.file_manager.File import File

from defines import *

import time
from datetime import datetime as dt

from UI.part_manager.PartListViewChangeStatusSignal import PartListViewChangeStatusSignal

class ScrollWidget(QWidget):
    def __init__(self, callback, manager):
        super().__init__()
        self.setAcceptDrops(True)
        self.callback = callback
        self.manager = manager

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        position = e.pos()
        e.setDropAction(Qt.CopyAction)
        e.accept()
        self.manager.accept_details_right()

    def mousePressEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            self.callback()


class QEasyScrollDetails(QScrollArea):
    def __init__(self, callback, manager):
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.callback = callback
        self.manager = manager
    
        self.scrollWidgetLayout = QVBoxLayout()
        self.scrollWidgetLayout.setSpacing(0)
        self.scrollWidget = ScrollWidget(callback, manager)
        self.scrollWidget.setLayout(self.scrollWidgetLayout)
        self.setWidget(self.scrollWidget)

        self.scrollWidgetLayout.addStretch()

class PartsSearch(QFrame):
    def __init__(self, update_search_callback):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.update_search_callback = update_search_callback

        self.layout = QVBoxLayout()
        self.label = QLabel("Поиск")
        self.input = QLineEdit()

        self.apply_btn = QInitButton("Найти", self.search)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.apply_btn)

        self.setLayout(self.layout)

    def search(self):
        self.search_text = self.input.text()
        self.update_search_callback(self.search_text)

class PartsFilters(QFrame):
    def __init__(self, update_filters_callback):
        super().__init__()

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.update_filters_callback = update_filters_callback

        self.layout = QVBoxLayout()
        self.label = QLabel("Фильтры")


        self.format_frame = QFrame()
        self.format_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.format_frame.setLineWidth(1)
        self.format_frame_layout = QVBoxLayout()
        self.ext_label = QLabel("Форматы")
        self.format_buttons = []
        self.formats_layout = QGridLayout()

        self.format_frame_layout.addWidget(self.ext_label)
        self.format_frame_layout.addLayout(self.formats_layout)
        self.format_frame.setLayout(self.format_frame_layout)

        extensions = []
        for ext in FILE_FORMATS.keys():
            extensions.append(FILE_FORMATS[ext])
        
        rows_count = len(extensions) // 4
        for i in range(rows_count-1):
            for j in range(4):
                btn = QCheckBox(extensions[i*4+j])
                self.formats_layout.addWidget(btn, i, j)
                self.format_buttons.append(btn)
        

        self.status_frame = QFrame()
        self.status_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.status_frame.setLineWidth(1)
        self.status_frame_layout = QVBoxLayout()
        self.status_label = QLabel("Статус")
        self.status_buttons = []
        self.status_layout = QHBoxLayout()
        self.status_frame_layout.addWidget(self.status_label)
        for st in PART_STATUS_TRANSLATIONS.keys():
            btn = QCheckBox(PART_STATUS_TRANSLATIONS[st])
            self.status_buttons.append(btn)
            self.status_layout.addWidget(btn)
    
        self.status_frame_layout.addLayout(self.status_layout)
        self.status_frame.setLayout(self.status_frame_layout)

        self.apply_btn = QInitButton("Применить", self.apply)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.format_frame)
        self.layout.addWidget(self.status_frame)
        self.layout.addWidget(self.apply_btn)

        self.setLayout(self.layout)

    def apply(self):
        self.filters = {"formats": [], "statuses": [], "search": ""}
        for b in self.format_buttons:
            if b.isChecked():
                self.filters["formats"].append(b.text())
        for b in self.status_buttons:
            if b.isChecked():
                self.filters["statuses"].append(PART_STATUS_TRANSLATIONS_BACKWARDS[b.text()])

        self.update_filters_callback(self.filters)

class PartsListView(QWidget):
    def __init__(self, project):
        super().__init__()

        self.change_status_signals = PartListViewChangeStatusSignal()
        self.change_status_signals.update.connect(self.set_process_running)

        self.filters_opened = False
        self.search_opened = False

        self.parts_entries = []
        self.selected_part_entries = []

        self.project = project

        self.view_type = "list"

        self.setWindowTitle(f"Список деталей")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        self.setFixedSize(QSize(1280, 720))

        self.main_layout = QHBoxLayout()

        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.main_layout.addLayout(self.left_layout, 50)
        self.main_layout.addLayout(self.right_layout, 50)


        self.hLayout = QHBoxLayout()


        project_name = self.project["name"]
        details_path = os.path.join(env.config_manager["path"]["projects_path"], project_name)
        details_path = os.path.join(details_path, "ДЕТАЛИ-PW")
        self.parts_list_label = QLabel(f"Список деталей проекта: {project_name}")
        self.path_view = QLabel(f"Путь деталей: {details_path}")
        self.details_view_all = QLabel(f"Общее количество деталей: Ожидает загрузки")
        self.details_view_current = QLabel("Количество загруженных деталей: 0")
        self.process_running_label = QLabel("Состояние: ")

        self.view_type_layout = QHBoxLayout()
        self.btn_tree_view = QInitButton("", callback=lambda: self.set_view_type("tree"))
        self.btn_tree_view.setIcon(env.templates_manager.icons["tree_view"])
        self.btn_tree_view.setToolTip("Не сделано(")
        self.btn_list_view = QInitButton("", callback=lambda: self.set_view_type("list"))
        self.btn_list_view.setIcon(env.templates_manager.icons["list_view"])
        self.btn_filters_view = QInitButton("Фильтры", callback=self.open_filters)
        self.btn_search_view = QInitButton("Поиск", callback=self.open_search)
        self.btn_select_from_to = QInitButton("Выбрать детали от и до", callback=self.choose_from_to)
        self.btn_select_from_to.setToolTip("Выберите две детали в левом столбце, затем нажмите кнопку. Будут выбраны все детали между ними")
        self.btn_update_convertation = QInitButton("Требуется обновление деталей", callback=self.update_all_convertation)
        self.btn_update_convertation.setToolTip("Если исходный файл детали был обновлен, то и сконвертированные из него файлы должны быть обновлены. Решите в ProtoWorks.")
        self.btn_resolve_deletion = QInitButton("Внимание: Файл детали утерян.", callback=self.open_resolve_deletion_dialog)
        self.btn_resolve_deletion.setToolTip("Был удалён исходный файл деталь. Перейдите в ProtoWorks для решения проблемы")
        self.btn_resolve_deletion.hide() 

        self.setStyleSheet(UI.stylesheets.TOOLTIP)

        self.view_type_layout.addWidget(self.btn_tree_view)
        self.view_type_layout.addWidget(self.btn_list_view)
        self.view_type_layout.addWidget(self.btn_filters_view)
        self.view_type_layout.addWidget(self.btn_search_view)
        self.view_type_layout.addWidget(self.btn_select_from_to)
        self.view_type_layout.addWidget(self.btn_update_convertation)
        self.view_type_layout.addWidget(self.btn_resolve_deletion)
        self.view_type_layout.addStretch()

        self.scrollable = QEasyScroll()
        self.scrollWidgetLayout = self.scrollable.scrollWidgetLayout
        self.scrollWidget = self.scrollable.scrollWidget

        self.filters_view = PartsFilters(self.update_filters)
        self.search_view = PartsSearch(self.update_search)
        self.filters = {"formats": [], "statuses": []}
        self.search = ""

        self.left_layout.addWidget(self.parts_list_label)
        self.left_layout.addWidget(self.path_view)
        self.left_layout.addWidget(self.details_view_all)
        self.left_layout.addWidget(self.details_view_current)
        self.left_layout.addWidget(self.process_running_label)
        self.left_layout.addLayout(self.view_type_layout)
        self.left_layout.addWidget(self.filters_view)
        self.left_layout.addWidget(self.search_view)
        self.left_layout.addWidget(self.scrollable)

        self.filters_view.hide()
        self.search_view.hide()

        self.downLayout = QHBoxLayout()
        self.view_more_btn = QInitButton("Загрузить больше", callback=lambda: self.update_data())
        self.view_all_btn = QInitButton("Загрузить все", callback=lambda: self.update_data(all=True))
        self.update_btn = QInitButton("Обновить", callback=lambda: self.update_data(update_network=True))
        self.downLayout.addWidget(self.view_more_btn)
        self.downLayout.addWidget(self.view_all_btn)
        self.downLayout.addWidget(self.update_btn)

        self.left_layout.addLayout(self.downLayout)

        self.current_end_idx = 0
        self.parts = []

        self.setLayout(self.main_layout)

        self.updating = False

        self.selected_details_view = QLabel("Выбрано деталей: 0")
        self.r_scrollable = QEasyScrollDetails(callback=self.clear_selection, manager=self)
        self.r_scrollWidgetLayout = self.r_scrollable.scrollWidgetLayout
        self.r_scrollWidget = self.r_scrollable.scrollWidget

        self.files_drop = QFilesDrop("Переместите сюда файлы детали проекта для их добавления", callback=self.on_file_drop)
        #self.files_drop.setFixedHeight()

        self.open_distribution_btn = QInitButton("Перейти к распределению")
        self.clear_selection_btn = QInitButton("Очистить выбор", callback=self.clear_right_selection)
        self.change_status_btn = QInitButton("Изменить состояние", callback=self.change_status)

        self.right_layout.addWidget(self.selected_details_view)
        self.right_layout.addWidget(self.clear_selection_btn)
        self.right_layout.addWidget(self.files_drop)
        self.right_layout.addWidget(self.r_scrollable)
        self.right_layout.addWidget(self.open_distribution_btn)
        self.right_layout.addWidget(self.change_status_btn)

        self.loaded_ids = []
        self.selected_ids = []
        self.restrictions = []

        self.update_data(update_network=True)

    def open_resolve_deletion_dialog(self):
        utils.message("Некоторые детали утеряны. Перейдите в ProtoWorks для решения этой проблемы.")

    def deletion_warning(self):
        self.btn_resolve_deletion.show()
        self.btn_resolve_deletion.setStyleSheet(UI.stylesheets.adapt(UI.stylesheets.RED_HIGHLIGHT, "QLabel", "QInitButton"))

    def on_file_drop(self, files):
        parts, not_parts = env.part_manager.indentify_parts(files)
        parts_real = []
        for p in parts:
            if p != None:
                if p["id"] not in self.restrictions:
                    parts_real.append(p)
                    self.restrictions.append(p["id"])
        self.accept_details_right(parts_real)

    def choose_from_to(self):
        st = -1
        end = -1
        unselect = False
        for i in range(len(self.parts_entries)):
            e = self.parts_entries[i]
            if e.selected:
                if st == -1:
                    st = i
                else:
                    if end == -1:
                        end = i
                    else:
                        unselect = True                    
                        break

        if not unselect:
            if st == -1:
                st = 0
            if end == -1:
                end = len(self.parts_entries)-1
        
            for i in range(st, end+1):
                self.parts_entries[i].selected = True
                self.parts_entries[i].check_selected()
        else:
            for e in self.parts_entries:
                e.selected = False
                e.check_selected()

    def update_all_convertation(self):
        utils.message("Требуется обновить детали через ProtoWorks.")


    def change_status(self):
        if len(self.selected_part_entries) > 0:
            dlg = QSelectOneFromList("Выберите", list(PART_STATUS_TRANSLATIONS_BACKWARDS.keys()), self.changed_status)
            dlg.show()
    def changed_status(self, answer):
        if answer != None:
            answer = PART_STATUS_TRANSLATIONS_BACKWARDS[answer]
            parts = []
            for e in self.selected_part_entries:
                e.part["status"] = int(answer)
                parts.append(e.part)
            env.part_manager.update_parts(self.project, parts)
            for p in self.selected_part_entries:
                p.update_view()

    def accept_details_right(self, parts=None):
        transfer = []
        parts_entries_to_del = []
        if parts == None:
            for e in self.parts_entries:
                if e.selected:
                    transfer.append(e.part)
                    e.selected = False
                    if e.parent() != None:
                        e.setParent(None)
                    parts_entries_to_del.append(e)
            i = 0
            while i < len(self.parts_entries):
                part = self.parts_entries[i]
                if part in parts_entries_to_del:
                    del self.parts_entries[i]
                    i-=1
                i += 1
        else:
            ids = []
            for p in parts:
                ids.append(p["id"])
            self.update_data(no_move=True)
            transfer = parts

        transfer = sorted(transfer, key=lambda key: (-key["status"], key["id"]))
        for part in transfer:
            e = PartListEntry(self.project, part, self)
            #self.scrollWidgetLayout.insertWidget(i, e)
            self.r_scrollable.scrollWidgetLayout.addWidget(e)
            self.r_scrollable.scrollWidgetLayout.setAlignment(e, Qt.AlignmentFlag.AlignTop)
            self.selected_part_entries.append(e)
            self.selected_ids.append(part["id"])
            #if self.current_start_id
                    
        self.selected_details_view.setText(f"Выбрано деталей: {len(self.selected_part_entries)}")

    def clear_selection(self):
        for e in self.parts_entries:
            e.selected = False
            e.check_selected()

    def clear_right_selection(self):
        self.restrictions = []
        for e in self.selected_part_entries:
            if e.parent() != None:
                e.setParent(None)
        self.selected_part_entries = []
        self.selected_ids = []
        self.selected_details_view.setText(f"Выбрано деталей: {len(self.selected_part_entries)}")
        self.update_data(update_network=True)

    def update_filters(self, filters):
        self.filters = filters
        self.update_data(update_network=True)
    
    def update_search(self, search):
        self.search = search
        self.update_data(update_network=True)

    def open_search(self):
        if not self.search_opened:
            self.search_view.show()
        else:
            self.search_view.hide()
        self.search_opened = not self.search_opened

    def open_filters(self):
        if not self.filters_opened:
            self.filters_view.show()
        else:
            self.filters_view.hide()
        self.filters_opened = not self.filters_opened

    def set_view_type(self, view_type):
        self.view_type = view_type
        self.update_data()

    def set_process_running(self, dc):
        try:
            text = dc["text"]
            stylesheet = dc["stylesheet"]
            if self.process_running_label.parent != None:
                self.process_running_label.setText(text)
                self.process_running_label.setStyleSheet(stylesheet)
        except Exception as e:
            print(e)

    def check_warnings_thread(self, parts):
        dc = {"text": "Состояние: Проверка деталей", "stylesheet": UI.stylesheets.CYAN_HIGHLIGHT}
        self.change_status_signals.update.emit(dc)
        try:
            for p in parts:
                if env.part_manager.check_part_up_to_date_with_origin(self.project, p) == 0:
                    self.btn_update_convertation.setStyleSheet(UI.stylesheets.adapt(UI.stylesheets.YELLOW_HIGHLIGHT, "QLabel", "QPushButton"))
                elif env.part_manager.check_part_up_to_date_with_origin(self.project, p) == -1:
                    self.deletion_warning()
        except:
            pass
        dc = {"text": "Состояние: Детали проверены.", "stylesheet": UI.stylesheets.NO_HIGHLIGHT}
        self.change_status_signals.update.emit(dc)


    def update_data(self, update_network=False, all=False, no_move=False):
        if self.updating:
            return
        self.updating = True

        self.btn_resolve_deletion.hide()
        self.btn_update_convertation.setStyleSheet(UI.stylesheets.DEFAULT_BUTTON)

        if update_network:
            start_idx = 0
            self.current_end_idx = 0
            parts = env.net_manager.parts.get_parts(self.project["id"])

            name = self.project["name"]
            env.task_manager.append_task(lambda: self.check_warnings_thread(parts), f"[{name}] Проверка деталей")

            parts = sorted(parts, key=lambda key: key["id"])
            self.parts = parts
            self.details_view_all.setText(f"Общее количество деталей: {len(parts)}")

            self.filtered_parts = []
            for p in parts:
                st = True
                if self.search != "":
                    if self.search not in p["name"]:
                        st = False
                if not st:
                    continue
                if self.filters["formats"] != []:
                    files = env.part_manager.get_available_part_files_by_id(self.project, p["id"])
                    formats = []
                    for f in files:
                        formats.append(f.path.split(".")[-1])
                    st = False
                    for f in self.filters["formats"]:
                        if f in formats:
                            st = True
                            break
                if not st:
                    continue
                
                if self.filters["statuses"] != []:
                    if p["status"] not in self.filters["statuses"]:
                        st = False
                if st:
                    self.filtered_parts.append(p)

            if self.view_type == "list":
                self.scrollable.show()
                for e in self.parts_entries:
                    if e.parent() != None:
                        e.setParent(None)

                self.parts_entries = []
                self.loaded_ids = []

        if self.view_type == "list":

            start_idx = 0

            if not all:
                if not no_move:
                    start_idx = self.current_end_idx
                    self.current_end_idx += 10
                else:
                    start_idx = self.current_end_idx - 10
            else:
                start_idx = self.current_end_idx
                self.current_end_idx = len(self.filtered_parts)

            if self.current_end_idx > len(self.filtered_parts):
                self.current_end_idx = len(self.filtered_parts)
            if start_idx >= len(self.filtered_parts):
                start_idx = len(self.filtered_parts)-1
            if start_idx < 0:
                start_idx = 0

            for i in range(start_idx, self.current_end_idx):
                part = self.filtered_parts[i]
                if part["id"] in self.loaded_ids or part["id"] in self.restrictions:
                    continue
                e = PartListEntry(self.project, part, self)
                self.loaded_ids.append(part["id"])
                #self.scrollWidgetLayout.insertWidget(i, e)
                self.scrollWidgetLayout.addWidget(e)
                #self.scrollWidgetLayout.setAlignment(e, Qt.AlignmentFlag.AlignTop)
                self.parts_entries.append(e)
                #if self.current_start_id

            #else:
                #self.scrollable.hide()
        
        self.details_view_current.setText(f"Количество загруженных деталей: {len(self.parts_entries)}")

        self.updating = False
        self.update()
