import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QSplitter, QLabel, QMessageBox
from PySide6.QtCore import QTimer

from UI.widgets.QUserInput import QUserInput
from UI.widgets.QInitButton import QInitButton

from environment.environment import Environment
env = Environment()

import utils

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"Аутентификация")
        self.setWindowIcon(env.templates_manager.icons["proto"])
        self.setFixedSize(QSize(320, 200))

        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.host_input = QUserInput("Сервер: ", corner_align=True)
        self.host_input.set_input(env.net_manager.host)

        self.username_input = QUserInput("Имя пользователя:", corner_align=True)
        self.username_input.set_input(env.net_manager.username)

        self.password_input = QUserInput("Пароль:", corner_align=True, password=True)
        self.password_input.set_input(env.net_manager.password)

        self.login_btn = QInitButton("Войти", callback=self.submit)
        
        self.layout.addWidget(self.host_input)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_btn)

        QTimer.singleShot(10, self.center_window)

    
    def center_window(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        if env.net_manager._auto_login:
            self.submit()

    def closeEvent(self, event):
        if env.net_manager.username == "":
            #sys.exit() # no auth - no app, yes?
            print("error here??? auth_window")
        event.accept()
    
    def submit(self):
        env.net_manager.set_host(self.host_input.get_input())
        ret = env.net_manager.auth.login(self.username_input.get_input(), self.password_input.get_input())

        if ret != 0:
            utils.message(ret)
        else:
            env.config_manager.write_host(self.host_input.get_input())
            self.close()