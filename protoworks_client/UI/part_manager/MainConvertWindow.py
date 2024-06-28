from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox
from PySide6.QtCore import QTimer


import utils
from defines import *

import UI.stylesheets as stylesheets
from UI.widgets.QClickableLabel import QClickableLabel
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QListEntry import QListEntry
from UI.widgets.QDictShow import QDictShow
from UI.widgets.QPathInput import QPathInput
from UI.widgets.QChooseManyCheckBoxes import QChooseManyCheckBoxes
from UI.widgets.QFilesListSureDialog import QFilesListSureWidget

from UI.part_manager.NewPartsTab import NewPartsTab

from UI.widgets.QEasyScroll import QEasyScroll

from UI.part_manager.PartListEntry import PartListEntry

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()

from environment.environment import Environment
env = Environment()

class MainConvertWindow(QWidget):
    def __init__(self, project, parts):
        super().__init__()

        self.project = project
        self.parts = parts

        self.setStyleSheet(stylesheets.TOOLTIP)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.left_layout = QVBoxLayout()

        self.setWindowTitle(f"Конвертирование деталей")
        self.setWindowIcon(env.templates_manager.icons["proto"])
        #self.setFixedSize(QSize(1000, 600))

        name = self.project["name"]
        self.project_label = QLabel(f"Проект: {name}")
        self.details_view_all = QLabel(f"Общее количество деталей: {len(self.parts)}")


        self.update_by_origin_btn = QCheckBox("Обновлять по изначальному файлу")
        self.update_by_origin_btn.setToolTip("При включении данного пункта, файлы деталей будут обновлены с учётом изменений изначального файла. Иначе будет использоваться версия, которая была последний раз зарегестрирована")
        self.update_by_origin_btn.setChecked(True)

        self.start_idx = 0
        self.current_end_idx = 0

        self.scrollable = QEasyScroll()
        self.scrollWidgetLayout = self.scrollable.scrollWidgetLayout
        self.scrollWidget = self.scrollable.scrollWidget

        self.downLayout = QHBoxLayout()
        self.view_more_btn = QInitButton("Загрузить больше", callback=lambda: self.update_data())
        self.view_all_btn = QInitButton("Загрузить все", callback=lambda: self.update_data(all=True))
        self.downLayout.addWidget(self.view_more_btn)
        self.downLayout.addWidget(self.view_all_btn)


        self.left_layout.addWidget(self.project_label)
        self.left_layout.addWidget(self.details_view_all)
        self.left_layout.addWidget(self.update_by_origin_btn)
        self.left_layout.addWidget(self.scrollable)
        self.left_layout.addLayout(self.downLayout)

        self.layout.addLayout(self.left_layout, 50)
        self.layout.addWidget(QWidget(), 50)

        self.parts_entries = []
        self.loaded_ids = []

        self.update_data()

    def update_data(self, all=False):

        parts = sorted(self.parts, key=lambda key: key["id"])
        self.parts = parts

        if not all:
            self.start_idx = self.current_end_idx
            self.current_end_idx += 10
        else:
            self.start_idx = self.current_end_idx
            self.current_end_idx = len(self.parts)

        if self.current_end_idx > len(self.parts):
            self.current_end_idx = len(self.parts)
        if self.start_idx >= len(self.parts):
            self.start_idx = len(self.parts)-1
        if self.start_idx < 0:
            self.start_idx = 0

        for i in range(self.start_idx, self.current_end_idx):
            part = self.parts[i]
            if part["id"] in self.loaded_ids:
                continue
            e = PartListEntry(self.project, part, self, _disable_context_menu=True)
            self.loaded_ids.append(part["id"])
            #self.scrollWidgetLayout.insertWidget(i, e)
            self.scrollWidgetLayout.addWidget(e)
            #self.scrollWidgetLayout.setAlignment(e, Qt.AlignmentFlag.AlignTop)
            self.parts_entries.append(e)
            #if self.current_start_id

        self.update()