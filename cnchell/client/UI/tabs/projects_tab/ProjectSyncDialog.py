import sys

from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QCheckBox, QMessageBox

from UI.widgets.QInitButton import QInitButton

import UI.stylesheets as stylesheets

from defines import *

# shit code.

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()


class ProjectSyncDialog(QDialog):
    def __init__(self, callback):
        super().__init__()

        self.callback = callback

        self.setWindowIcon(templates_manager.icons["proto"])
        self.setWindowTitle("Синхронизация проекта")

        self.layout = QVBoxLayout()

        self.checkboxes_disabled = False

        self.message = QLabel("Выберите один из вариантов")
        self.layout.addWidget(self.message)

        self.btn_sync_all_new = QCheckBox(text="Синхронизировать по новейшим изменениям")
        self.btn_server_override = QCheckBox(text="Перезаписать серверную директорию")
        self.btn_client_override = QCheckBox(text="Перезаписать локальную директорию")
        self.btn_sync_new_server = QCheckBox(text="Загрузить только новые файлы с сервера")
        self.btn_sync_new_client = QCheckBox(text="Загрузить только новые файлы с клиента")
        self.btn_sync_edit_server = QCheckBox(text="Загрузить только измененные файлы с сервера")
        self.btn_sync_edit_client = QCheckBox(text="Загрузить только измененные файлы с клиента")
        
        self.btn_sync_all_new.setToolTip("Из файлов сервера и локальных, которые имеют отличия между собой, \nбудут выбраны те, что имеют самое недавнее время изменения.")
        self.btn_server_override.setToolTip("Серверная директория будет удалена и заменена на копию локальной")
        self.btn_client_override.setToolTip("Локальная директория будет удалена и заменена на копию директории сервера")
        self.btn_sync_new_server.setToolTip("Только созданные недавно на сервере файлы будут перенесены в локальную директорию. \nУже существующие до этого измененные в локальной директории и на сервере файлы не будут подлежать копированию")
        self.btn_sync_new_client.setToolTip("Только созданные недавно в локальной директории файлы будут перенесены на сервер. \nУже существующие до этого измененные в локальной директории и на сервере файлы не будут подлежать копированию")
        self.btn_sync_edit_server.setToolTip("Только измененные недавно на сервере файлы будут перенесены в локальную директорию, заменяя те, что были в ней до этого. \nСозданные недавно файлы не будут подлежать копированию")
        self.btn_sync_edit_client.setToolTip("Только измененные недавно в локальной директории файлы будут перенесены на сервер, заменяя те, что были на сервере до этого. \nСозданные недавно файлы не будут подлежать копированию")

        self.setStyleSheet(stylesheets.TOOLTIP)

        self.layout.addWidget(self.btn_sync_all_new)
        self.layout.addWidget(self.btn_server_override)
        self.layout.addWidget(self.btn_client_override)
        self.layout.addWidget(self.btn_sync_new_server)
        self.layout.addWidget(self.btn_sync_new_client)
        self.layout.addWidget(self.btn_sync_edit_server)
        self.layout.addWidget(self.btn_sync_edit_client)

        self.checkboxes = [self.btn_sync_all_new, 
            self.btn_server_override,
            self.btn_client_override,
            self.btn_sync_new_server,
            self.btn_sync_new_client,
            self.btn_sync_edit_server,
            self.btn_sync_edit_client
            ]
        
        for cb in self.checkboxes:
            cb.stateChanged.connect(self.checkbox_enabled)

        self.btn_apply = QInitButton("Выполнить", callback=self.apply)
        self.btn_cancel = QInitButton("Отмена", callback=self.close)

        self.btn_box_layout = QHBoxLayout()
        self.btn_box_layout.addWidget(self.btn_apply)
        self.btn_box_layout.addWidget(self.btn_cancel)

        self.layout.addLayout(self.btn_box_layout)

        self.setLayout(self.layout)
        #self.setFixedSize(self.sizeHint())

    def checkbox_enabled(self):
        if not self.checkboxes_disabled:
            cb = None
            for cb_i in self.checkboxes:
                if cb_i.isChecked():
                    cb = cb_i
                    break 

            self.checkboxes_disabled = True
            for cb_i in self.checkboxes:
                if cb_i != cb:
                    cb_i.setDisabled(True)
        else:
            self.checkboxes_disabled = False
            for cb_i in self.checkboxes:
                cb_i.setDisabled(False)


    def apply(self):
        action = None
        for cb in self.checkboxes:
            if cb.isChecked():
                if cb == self.btn_sync_all_new:
                    action = ACTION_SYNC_ALL_NEW_FILES
                elif cb == self.btn_server_override:
                    action = ACTION_OVERRIDE_SERVER_FILES
                elif cb == self.btn_client_override:
                    action = ACTION_OVERRIDE_CLIENT_FILES
                elif cb == self.btn_sync_new_server:
                    action = ACTION_SEND_ONLY_NEW_FILES_FROM_SERVER
                elif cb == self.btn_sync_new_client:
                    action = ACTION_SEND_ONLY_NEW_FILES_FROM_CLIENT
                elif cb == self.btn_sync_edit_server:
                    action = ACTION_SEND_ONLY_EDITED_FILES_FROM_SERVER
                elif cb == self.btn_sync_edit_client:
                    action = ACTION_SEND_ONLY_EDITED_FILES_FROM_CLIENT
                break
        
        self.callback(action)
        self.close()
        