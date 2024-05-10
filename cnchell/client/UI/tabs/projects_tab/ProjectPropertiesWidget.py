from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication
from PySide6.QtCore import QTimer


import utils

import UI.stylesheets as stylesheets
from UI.widgets.QClickableLabel import QClickableLabel
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QListEntry import QListEntry
from UI.widgets.QDictShow import QDictShow

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()


class ProjectPropertiesWidget(QWidget):
    def __init__(self, project):
        super().__init__()

        self.project = project

        self.setWindowTitle(f"Свойства проекта")
        self.setWindowIcon(templates_manager.icons["cnchell"])
        self.setFixedSize(QSize(600, 600))

        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.layout = QVBoxLayout()

        key_space = 30

        name_s = QDictShow("Название:", self.project["name"], key_space)
        customer_s = QDictShow("Заказчик:", self.project["customer"], key_space)
        description_s = QDictShow("Описание:", self.project["description"], key_space)
        time_registered_s = QDictShow("Начало работ:", utils.time_by_unix(self.project["time_registered"]), key_space)
        time_deadline_s = QDictShow("Дедлайн:", utils.time_by_unix(self.project["time_deadline"]), key_space)
        status_s = QDictShow("Состояние:", utils.project_status(self.project["status"]), key_space)
        path_s = QDictShow("Путь на сервере:", self.project["server_path"], key_space)

        self.layout.addWidget(name_s)
        self.layout.addWidget(customer_s)
        self.layout.addWidget(description_s)
        self.layout.addWidget(time_registered_s)
        self.layout.addWidget(time_deadline_s)
        self.layout.addWidget(status_s)
        self.layout.addWidget(path_s)

        if "last_synced_server" in self.project:
            last_synced_server_s = QDictShow("Последнее обновление на сервере:", utils.time_by_unix(self.project["last_synced_server"]), key_space)
            self.layout.addWidget(last_synced_server_s)
        if "last_synced_client" in self.project:
            last_synced_client_s = QDictShow("Последнее обновление на клиенте:", utils.time_by_unix(self.project["last_synced_client"]), key_space)
            self.layout.addWidget(last_synced_client_s)
        
        if "update_id_server" in self.project:
            update_id_server_s = QDictShow("Идентификатор обновления на сервере:", self.project["update_id_server"], key_space)
            self.layout.addWidget(update_id_server_s)
        if "update_id_client" in self.project:
            update_id_client_s = QDictShow("Идентификатор обновления на клиенте:", self.project["update_id_client"], key_space)
            self.layout.addWidget(update_id_client_s)
    
        self.setLayout(self.layout)

        QTimer.singleShot(10, self.center_window)
    
    def center_window(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        event.accept()