from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QFrame, QLabel, QScrollArea, QMenu, QFileDialog, QApplication
from PySide6.QtGui import QIntValidator


import os

from environment.tab_manager.Tab import Tab

from environment.environment import Environment
env = Environment()

import utils

import UI.stylesheets
from UI.widgets.QClickableLabel import QClickableLabel
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QPathInput import QPathInput
from UI.widgets.QUserInput import QUserInput
from UI.widgets.QYesOrNoDialog import QYesOrNoDialog
from UI.widgets.QSelectOneFromList import QSelectOneFromList

from UI.tabs.machines_tab.AddSlaveWindow import AddSlaveWindow
from UI.tabs.machines_tab.HubSettingsWindow import HubSettingsWindow
from UI.tabs.machines_tab.SlavesListWindow import SlavesListWindow
from UI.tabs.machines_tab.AddMachineWindow import AddMachineWindow
from UI.tabs.machines_tab.MachinesListWindow import MachinesListWindow

import defines

from PySide6.QtCore import Signal, QObject

# Хаб статус + рестарт
# слейвов онлайн + рестарт
# станков онлайн + рестарт
# Добавить станок
# Добавить слейв
# Открыть список слейвов
# Открыть список станков
# Приостановить все станки
# Отключить все станки
# Открыть терминал хаба

class GetInfo(QObject):
    hub_info = Signal(dict)
    change_slaves_count = Signal(dict)
    change_machines_count = Signal(dict)

class MachinesWidget(QWidget, Tab):
    def __init__(self):
        super().__init__()

        self.get_data_signals = GetInfo()
        self.get_data_signals.hub_info.connect(self.set_hub_info)
        self.get_data_signals.change_slaves_count.connect(self.change_slaves_count_ui)
        self.get_data_signals.change_machines_count.connect(self.change_machines_count_ui)

        self.machines_entries = []

        self.cwd = env.cwd

        self.setStyleSheet(UI.stylesheets.DEFAULT_BORDER_STYLESHEET)

        self.layout = QVBoxLayout()

        upper_layout = QHBoxLayout()
        
        self.label = QClickableLabel(text=f"Станки")
        self.update_btn = QInitButton("Обновить", callback=self.update_data)
        self.exit_btn = QInitButton("X", callback=self.exit)

        upper_layout.addWidget(self.label, 99)
        upper_layout.addWidget(self.update_btn, 1)
        upper_layout.addWidget(self.exit_btn, 1)
        upper_layout.setSpacing(0)
        upper_layout.setAlignment(self.exit_btn, Qt.AlignmentFlag.AlignRight)


        self.layout.addLayout(upper_layout)
        self.layout.setAlignment(upper_layout, Qt.AlignmentFlag.AlignTop)

        self.scrollable = QScrollArea()
        self.scrollable.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollable.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollable.setWidgetResizable(True)

        self.scrollWidgetLayout = QVBoxLayout()
        self.scrollWidgetLayout.setSpacing(0)
        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollWidgetLayout)
        self.scrollable.setWidget(self.scrollWidget)
        #self.scrollable.setLayout(self.scroll_layout)

        #self.update_data()
        
        self.scrollWidgetLayout.addStretch()

        self.layout.addWidget(self.scrollable)
        self.setLayout(self.layout)

        self.load_ui()

    def load_ui(self):
        i = 0
        self.hub_frame = QFrame()
        self.hub_frame.setStyleSheet(UI.stylesheets.DISABLE_BORDER)
        self.hub_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.hub_frame.setLineWidth(1)
        self.hub_frame_layout = QVBoxLayout()

        self.hub_status_layout = QHBoxLayout()
        self.hub_status_label = QLabel("Hub. Состояние: Ожидание данных.")
        self.hub_status_restart = QInitButton("Перезапустить", callback=self.restart_hub)
        self.hub_frame_layout.addWidget(self.hub_status_label)
        self.hub_frame_layout.addWidget(self.hub_status_restart)

        self.change_hub_settings_btn = QInitButton("Изменить настройки подключение Hub'а", callback=self.change_hub_settings)
        self.hub_frame_layout.addWidget(self.change_hub_settings_btn)

        self.open_terminal_btn = QInitButton("Открыть терминал", callback=self.open_terminal)
        self.hub_frame_layout.addWidget(self.open_terminal_btn)

        self.monitoring_window_btn = QInitButton("Открыть окно мониторинга", callback=self.open_monitoring)
        self.hub_frame_layout.addWidget(self.monitoring_window_btn)

        self.hub_frame.setLayout(self.hub_frame_layout)
        self.scrollWidgetLayout.insertWidget(i, self.hub_frame)
        i+=1

        self.slave_frame = QFrame()
        self.slave_frame.setStyleSheet(UI.stylesheets.DISABLE_BORDER)
        self.slaves_frame_layout = QVBoxLayout()

        self.slaves_status_layout = QHBoxLayout()
        self.slaves_status_label = QLabel("Слейвы. Состояние: Ожидание данных")
        self.slaves_status_restart = QInitButton("Перезапустить", callback=self.restart_slaves)
        self.slaves_frame_layout.addWidget(self.slaves_status_label)
        self.slaves_frame_layout.addWidget(self.slaves_status_restart)

        self.add_slave_btn = QInitButton("Добавить слейв", callback=self.add_slave)
        self.slaves_frame_layout.addWidget(self.add_slave_btn)

        self.open_slave_list_btn = QInitButton("Список слейвов", callback=self.open_slave_list)
        self.slaves_frame_layout.addWidget(self.open_slave_list_btn)

        self.slave_frame.setLayout(self.slaves_frame_layout)
        self.scrollWidgetLayout.insertWidget(i, self.slave_frame)
        self.scrollWidgetLayout.setAlignment(self.slave_frame, Qt.AlignmentFlag.AlignTop)
        i+=1 


        self.machine_frame = QFrame()
        self.machine_frame.setStyleSheet(UI.stylesheets.DISABLE_BORDER)
        self.machines_frame_layout = QVBoxLayout()

        self.machines_status_layout = QHBoxLayout()
        self.machines_status_label = QLabel("Станки. Состояние: Ожидание данных")
        self.machines_status_restart = QInitButton("Перезапустить все соединения", callback=self.restart_machines)
        self.machines_frame_layout.addWidget(self.machines_status_label)
        self.machines_frame_layout.addWidget(self.machines_status_restart)

        self.add_machine_btn = QInitButton("Добавить станок", callback=self.add_machine)
        self.machines_frame_layout.addWidget(self.add_machine_btn)

        self.open_machine_list_btn = QInitButton("Список станков", callback=self.open_machine_list)
        self.machines_frame_layout.addWidget(self.open_machine_list_btn)

        self.pause_machines_btn = QInitButton("Приостановить все станки", callback=self.pause_machines)
        self.machines_frame_layout.addWidget(self.pause_machines_btn)

        self.shutdown_machines_btn = QInitButton("Отключить все станки", callback=self.shutdown_machines)
        self.machines_frame_layout.addWidget(self.shutdown_machines_btn)

        self.machine_frame.setLayout(self.machines_frame_layout)
        self.scrollWidgetLayout.insertWidget(i, self.machine_frame)
        self.scrollWidgetLayout.setAlignment(self.machine_frame, Qt.AlignmentFlag.AlignTop)
        i+=1

        self.update_data()

        #self.scrollWidgetLayout.insertWidget(0, )
        #self.scrollWidgetLayout.setAlignment(self.pathes_label, Qt.AlignmentFlag.AlignTop)

    def set_hub_info(self, data):
        if data == None:
            self.hub_status_label.setText("Hub. Состояние: Не настроен")
            return
        else:
            if int(data["ping"]) > -1 and data["status"] == "online":
                self.hub_status_label.setText("Hub. Состояние: Онлайн")
                self.hub_status_label.setStyleSheet(UI.stylesheets.GREEN_HIGHLIGHT)
            else:
                self.hub_status_label.setText("Hub. Состояние: Оффлайн")
                self.hub_status_label.setStyleSheet(UI.stylesheets.RED_HIGHLIGHT)

    def get_data(self):
        info = env.net_manager.hardware.get_hub_info()
        self.get_data_signals.hub_info.emit(info)
        self.get_slaves_count()
        self.get_machines_count()

    def get_slaves_count(self):
        data = env.net_manager.slaves.get_slaves_list()
        on = 0
        for d in data["slaves"]:
            if d['status'] == "online":
                on+=1
        self.get_data_signals.change_slaves_count.emit({"online": on, "all": len(data["slaves"])})

    def get_machines_count(self):
        data = env.net_manager.machines.get_machines_list(-1)
        on = 0
        for m in data["machines"]:
           if m["status"] == "online":
               on+=1
        self.get_data_signals.change_machines_count.emit({"online": on, "all": len(data["machines"])})

    def change_slaves_count_ui(self, dc):
        on = dc["online"]
        allx = dc["all"]
        self.slaves_status_label.setText(f"Слейвы. Состояние: {on}/{allx} Онлайн")
        if on == allx:
            self.slaves_status_label.setStyleSheet(UI.stylesheets.GREEN_HIGHLIGHT)
        else:
            self.slaves_status_label.setStyleSheet(UI.stylesheets.YELLOW_HIGHLIGHT)

    def change_machines_count_ui(self, dc):
        on = dc["online"]
        allx = dc["all"]
        self.machines_status_label.setText(f"Станки. Состояние: {on}/{allx} Онлайн")
        if on == allx:
            self.machines_status_label.setStyleSheet(UI.stylesheets.GREEN_HIGHLIGHT)
        else:
            self.machines_status_label.setStyleSheet(UI.stylesheets.YELLOW_HIGHLIGHT)

    def update_data(self):
        env.task_manager.run_silent_task(self.get_data)

    def change_hub_settings(self):
        self.wnd = HubSettingsWindow()
        self.wnd.show()

    def open_monitoring(self):
        pass

    def restart_hub(self):
        self.dlg = QYesOrNoDialog("Вы действительно хотите перезапустить Hub?")
        self.dlg.exec()
        if self.dlg.answer:
            env.net_manager.hardware.restart_hub()
            utils.message("Команда отправлена.")

    def restart_slaves(self):
        self.dlg = QYesOrNoDialog("Вы действительно хотите перезапустить все слейвы?")
        self.dlg.exec()
        if self.dlg.answer:
            data = env.net_manager.slaves.get_slaves_list()
            for s in data["slaves"]:
                env.net_manager.slaves.restart(s["id"])
            utils.message("Запросы отправлены.", tittle="Оповещение")
    
    def restart_machines(self):
        self.dlg = QYesOrNoDialog("Вы действительно хотите перезапустить все соединения со станками?")
        self.dlg.exec()
        if self.dlg.answer:
            env.net_manager.hardware.restart_all()
            utils.message("Запрос отправлен.", tittle="Оповещение")
    
    def add_machine(self):
        slaves = env.net_manager.slaves.get_slaves_list()["slaves"]
        ids = []
        for i in range(len(slaves)):
            ids.append(str(slaves[i]["id"]))

        self.slave_selector = QSelectOneFromList("Выберите слейв, к которому будете подключать принтер", ids, self.slave_chosen)
        self.slave_selector.show()
    
    def slave_chosen(self, idx):
        wnd = AddMachineWindow(idx)
        wnd.show()

    def add_slave(self):
        wnd = AddSlaveWindow()
        wnd.show()
    
    def open_slave_list(self):
        self.wnd = SlavesListWindow()
        self.wnd.show()
    
    def open_machine_list(self):
        self.wnd = MachinesListWindow()
        self.wnd.show()

    def pause_machines(self):
        pass

    def shutdown_machines(self):
        pass
    
    def open_terminal(self):
        pass