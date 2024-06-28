import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QSplitter, QLabel, QMessageBox
from PySide6.QtCore import QTimer

from UI.widgets.QUserInput import QUserInput
from UI.widgets.QInitButton import QInitButton

from environment.environment import Environment
env = Environment()

import utils
import defines

class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"О программе")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        #self.setFixedSize(QSize(320, 400))

        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        
        self.logo = QLabel()
        pixmap = env.templates_manager.backgrounds["cnchell_logo_mini"]
        self.logo.setPixmap(pixmap)

        self.layout.addWidget(self.logo)

        self.main_label = QLabel("CNCHell - часть комплекса программного обеспечения ProtoWorks. Выполняет функцию взаимодействия со станками.")
        self.main_label.setWordWrap(True)
        self.layout.addWidget(self.main_label)

        self.ver_label = QLabel(f"Версия: v{defines.PROTOWORKS_VERSION}")
        self.layout.addWidget(self.ver_label)

        self.username_label = QLabel(f"Выполнен вход в пользователя: {env.net_manager.username}")
        self.host_label = QLabel(f"Сервер: {env.net_manager.host}")
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.host_label)

        self.docs_label = QLabel("Документация находится в директории программы")
        self.layout.addWidget(self.docs_label)

        self.year_label = QLabel("2024")
        self.layout.addWidget(self.year_label)

        #QTimer.singleShot(10, self.center_window)

    
    def center_window(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())