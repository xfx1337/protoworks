import sys

from PySide6.QtCore import QSize, Qt, QPoint
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QSplitter, QLabel

from environment.environment import Environment
env = Environment()

from environment.task_manager.statuses import *

import environment.tab_manager.tabs_aliases as tabs_aliases

import UI.stylesheets as stylesheets
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QSystemBar import QSystemBar

from UI.paper_print.PaperPrintMenu import PaperPrintMenu

import utils

import pythoncom, win32com

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        env.task_manager.run_system_task(env.kompas3d.kompas_api_thread, "[СИСТЕМА] КОМПАС-3D")
        env.templates_manager.load_templates() # before i cant init fucking pixmap before app starts..
        env.main_window = self
        self.get_tab_by_alias = tabs_aliases.get_tab_by_alias
        self.tabs_aliases = tabs_aliases.TABS_ALIASES

        self.setWindowTitle(f"ProtoWorks [{env.cwd}]")
        self.setWindowIcon(env.templates_manager.icons["proto"])
        self.setMinimumSize(QSize(1280, 720))

        #env.tab_manager.set_refresh_callback(self.refresh_blank_widget)

        main_vertical_layout = QVBoxLayout()

        app_bar_layout = QHBoxLayout()
        app_bar_layout_left = QHBoxLayout()
        app_bar_layout_right = QHBoxLayout()

        app_bar_layout_left.addWidget(
            QInitButton("Программы", callback=lambda: self.open_tab(None))
        )

        app_bar_layout_left.addWidget(
            QInitButton("Проекты", callback=lambda: self.open_tab("projects"))
        )

        app_bar_layout_left.addWidget(
            QInitButton("Настройки", callback=lambda:self.open_tab("settings"))
        )

        app_bar_layout_right.addWidget(
            QInitButton("Закрыть все вкладки", callback=lambda: env.tab_manager.close_all())
        )

        app_bar_layout_right.addWidget(
            QInitButton("Принтер по бумаге", callback=self.open_paper_print_menu)
        )

        app_bar_layout_right.addWidget(
            QInitButton("Станки", callback=lambda: self.open_tab(None))
        )

        app_bar_layout_right.addWidget(
            QInitButton("Общие задачи", callback=lambda: self.open_tab(None))
        )

        app_bar_layout_right.addWidget(
            QInitButton("ПОМОГИТЕ", callback=lambda: self.open_tab(None))
        )

        # building app bar
        app_bar_layout.addLayout(app_bar_layout_left)
        app_bar_layout.setAlignment(app_bar_layout_left, Qt.AlignmentFlag.AlignLeft)

        app_bar_layout.addLayout(app_bar_layout_right)
        app_bar_layout.setAlignment(app_bar_layout_right, Qt.AlignmentFlag.AlignRight)

        app_bar_widget = QWidget()
        app_bar_widget.setFixedHeight(50)
        app_bar_widget.setLayout(app_bar_layout)

        main_vertical_layout.addWidget(app_bar_widget)

        # build body container. storage for tabs

        self.body_container = QWidget()
        self.body_container_layout = QHBoxLayout()
        self.body_container.setStyleSheet(stylesheets.DEFAULT_BORDER_STYLESHEET)
        main_vertical_layout.addWidget(self.body_container, 99)

        self.body_splitter = QSplitter()
        self.body_container_layout.addWidget(self.body_splitter)
        self.body_container.setLayout(self.body_container_layout)

        bg_style = """
        QSplitter { background-image: url("UI/templates/images/backgrounds/protoworks_logo.png"); 
        background-repeat: no-repeat; 
        background-position: center; }
        """
        self.body_splitter.setStyleSheet(bg_style)

        self.botom_bar = QSystemBar()

        env.main_signals.task_status_changed.connect(self.on_operation_change)

        main_vertical_layout.addWidget(self.botom_bar, 1)
        main_vertical_layout.setAlignment(self.botom_bar, Qt.AlignmentFlag.AlignBottom)

        main_container = QWidget()
        main_container.setLayout(main_vertical_layout)

        self.setCentralWidget(main_container)   

    def open_paper_print_menu(self):
        self.wnd = PaperPrintMenu()
        self.wnd.show()

    def on_operation_change(self):
        tasks = env.task_manager.get_tasks()
        tasks_sorted = sorted(tasks, key=lambda key: (tasks[key].time_started, -tasks[key].status))

        task = tasks[tasks_sorted[0]]
        if task.status == ENDED:
            self.botom_bar.set_operation("Нет операции")
        else:
            self.botom_bar.set_operation(task.name)
        
        self.botom_bar.set_operation_color_by_task_status(task.status)
        
        #self.botom_bar.update()

    def open_tab(self, alias):
        if alias == None:
            return

        tab = tabs_aliases.get_tab_by_alias(alias)()

        id = env.tab_manager.open_tab(tab)
        self.body_splitter.addWidget(tab)