from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox
from PySide6.QtCore import QTimer

import os, shutil

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

from UI.widgets.QEasyScroll import QEasyScroll

from UI.part_manager.PartListEntry import PartListEntry

from UI.widgets.QAreUSureDialog import QAreUSureDialog

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

class ResolvePartDeletionWindow(QWidget):
    def __init__(self, project, parts):
        super().__init__()

        self.project = project
        self.parts = parts

        self.setStyleSheet(stylesheets.TOOLTIP)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.left_layout = QVBoxLayout()

        self.setWindowTitle(f"Разрешение ситуации удаления детали")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        #self.setFixedSize(QSize(1000, 600))

        name = self.project["name"]
        self.project_label = QLabel(f"Проект: {name}")
        self.details_view_all = QLabel(f"Общее количество деталей: {len(self.parts)}")

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
        self.left_layout.addWidget(self.scrollable)
        self.left_layout.addLayout(self.downLayout)

        self.layout.addLayout(self.left_layout, 50)


        self.right_layout = QVBoxLayout()

        self.label = QLabel("Внимание. Важно внимательно полностью понимать свои действия отношении деталей, идущих на удаление. Действия могут быть необратимыми.")
        self.label.setWordWrap(True)

        self.btn_undo_deletion_client = QInitButton("Восстановить оригинальные файлы детали по локальной копии", callback=self.undo_deletion_client)
        
        self.btn_delete_parts = QInitButton("Удалить детали", callback=self.delete_parts)
        self.btn_delete_parts.setToolTip("Данное действие удалит детали, их сконвертированные файлы. Останутся лишь оргинальные файлы на сервере, если они ещё не были удалены.")
        self.btn_delete_parts.setStyleSheet(stylesheets.adapt(stylesheets.RED_HIGHLIGHT, "QLabel", "QInitButton"))

        self.right_layout.addWidget(self.label)
        self.right_layout.addWidget(self.btn_undo_deletion_client)
        self.right_layout.addWidget(self.btn_delete_parts)
        self.right_layout.addStretch()

        self.layout.addLayout(self.right_layout, 50)

        self.parts_entries = []
        self.loaded_ids = []

        self.update_data()

    def delete_parts(self):
        dlg = QAreUSureDialog("Введите название проекта, что бы подтвердить удаление.")
        dlg.exec()
        if dlg.input.text() == self.project["name"]:
            try:
                env.part_manager.delete_parts(self.project, self.parts)
                for p in self.parts_entries:
                    p.setParent(None)
            except:
                pass
            

    def undo_deletion_client(self):
        name = self.project["name"]
        pro = Progress()
        env.task_manager.append_task(lambda: self.undo_deletion_client_thread(pro), f"[{name}] Восстановление оригинальных файлов деталей", progress=pro)
        utils.message("Запущена задача копирования. Вы можете узнать о её завершение в диспетчере задач.", "Уведомление")

    def undo_deletion_client_thread(self, progress):
        size = 0
        copyf = []
        for p in self.parts:
            path = p["path"]
            path = utils.remove_path(self.project["server_path"], path)
            local_dir = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"])
            origin_path = os.path.join(local_dir, path)
            
            filename = path.split("\\")[-1].split(".")[0] + "_PW" + str(p["id"]) + "." + path.split(".")[-1]
            file_copy = os.path.join(local_dir, "ДЕТАЛИ-PW")
            ext_dir = get_dir_name_by_ext(path.split(".")[-1])
            if ext_dir == None:
                ext_dir = path.split(".")[-1]
            file_copy = os.path.join(file_copy, ext_dir)
            file_copy = os.path.join(file_copy, filename)

            if os.path.isfile(file_copy):
                sizef = os.path.getmtime(file_copy)
                size += sizef
                copyf.append([origin_path, file_copy, sizef, p["id"]])

        for p in copyf:
            shutil.copy(p[1], p[0])
            env.file_manager.sync_update_time(p[1], p[0])
            progress.add(p[2])
            self.remove_entry(p[3])

    def remove_entry(self, id):
        for i in range(len(self.parts_entries)):
            if self.parts_entries[i].part["id"] == id:
                self.parts_entries[i].setParent(None)
                del self.parts_entries[i]
                break

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