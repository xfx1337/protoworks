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

import utils

import os

from UI.additional_windows.QueueManagerWindow import QueueManagerWindow

from UI.help_window import HelpWindow

from UI.additional_windows.CalculationsJobsFinderWindow import CalculationsJobsFinderWindow

from UI.widgets.QYesOrNoDialog import QYesOrNoDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        env.templates_manager.load_templates() # before i cant init fucking pixmap before app starts..
        env.task_manager.run_system_task(env.calculations.calculation_check_thread, "[СИСТЕМА] Система расчётов")
        env.task_manager.run_system_task(env.server_executor.setup_servers, "[СИСТЕМА] Запуск серверов")
        env.main_window = self
        self.get_tab_by_alias = tabs_aliases.get_tab_by_alias
        self.tabs_aliases = tabs_aliases.TABS_ALIASES

        self.setWindowTitle(f"CNCHell [{env.cwd}]")
        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        self.setMinimumSize(QSize(1280, 720))

        #env.tab_manager.set_refresh_callback(self.refresh_blank_widget)

        main_vertical_layout = QVBoxLayout()

        app_bar_layout = QHBoxLayout()
        app_bar_layout_left = QHBoxLayout()
        app_bar_layout_right = QHBoxLayout()

        app_bar_layout_left.addWidget(
            QInitButton("Программы", callback=lambda: self.open_tab("programs"))
        )

        app_bar_layout_left.addWidget(
            QInitButton("Проекты", callback=lambda: self.open_tab("projects"))
        )

        app_bar_layout_left.addWidget(
            QInitButton("Менеджер Очередей", callback=lambda: self.open_window("queue_man"))
        )

        app_bar_layout_left.addWidget(
            QInitButton("Станки", callback=lambda: self.open_tab("machines"))
        )

        app_bar_layout_left.addWidget(
            QInitButton("Настройки", callback=lambda: self.open_tab("settings"))
        )

        app_bar_layout_right.addWidget(
            QInitButton("Закрыть все вкладки", callback=lambda: env.tab_manager.close_all())
        )

        app_bar_layout_right.addWidget(
            QInitButton("ПОМОГИТЕ", callback=lambda: self.open_tab("help"))
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
        QSplitter { background-image: url("UI/templates/images/backgrounds/cnchell_logo.png"); 
        background-repeat: no-repeat; 
        background-position: center; }
        """
        self.body_splitter.setStyleSheet(bg_style)

        self.botom_bar = QSystemBar()

        env.main_signals.task_status_changed.connect(self.on_operation_change)
        env.main_signals.message.connect(utils.message)
        env.main_signals.open_calculations_jobs_finder_window.connect(self._open_calculations_jobs_finder_window)

        main_vertical_layout.addWidget(self.botom_bar, 1)
        main_vertical_layout.setAlignment(self.botom_bar, Qt.AlignmentFlag.AlignBottom)

        main_container = QWidget()
        main_container.setLayout(main_vertical_layout)

        self.setCentralWidget(main_container)   

    def open_window(self, window):
        if window == "queue_man":
            self.queue_man_wnd = QueueManagerWindow()
            self.queue_man_wnd.show()

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

        if alias == "help":
            self.help_wnd = HelpWindow()
            self.help_wnd.show()
            return

        self.tab = tabs_aliases.get_tab_by_alias(alias)() # self because garbage collector deletes it...

        id = env.tab_manager.open_tab(self.tab)
        self.body_splitter.addWidget(self.tab)

    
    def _open_calculations_jobs_finder_window(self, dc):
        self.calculations_jobs_finder_wnd = CalculationsJobsFinderWindow(dc)
        self.calculations_jobs_finder_wnd.show()

    def closeEvent(self, event):
        self.dlg = QYesOrNoDialog("Вы действительно хотите закрыть приложение?")
        self.dlg.exec()
        if not self.dlg.answer:
            event.ignore()
            return
        event.accept()
        env.server_executor.kill_all()
        os._exit(0)
        exit()