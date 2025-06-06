from singleton import singleton

import os
from environment.tab_manager.tab_manager import TabManager
from environment.task_manager.task_manager import TaskManager
from environment.network_manager.network_manager import NetworkManager
from environment.config_manager.config_manager import Config
from environment.templates_manager.templates_manager import TemplatesManager
from environment.file_manager.file_manager import FileManager
from environment.database.db import Database
from environment.part_manager.part_manager import PartManager
from environment.machine_utils.machine_utils import MachineUtils
from environment.calculations.calculations import Calculations
from environment.server_executor.server_executor import ServerExecutor

import utils

@singleton
class Environment():
    def __init__(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        self.cwd = dirname + "\\"
    
        self.tab_manager = TabManager(self)

        self.task_manager = TaskManager(self)
        self.net_manager = NetworkManager(self)
        self.config_manager = Config("config.ini", self)

        self.templates_manager = TemplatesManager(self)
        self.file_manager = FileManager(self)

        self.db = Database()

        self.part_manager = PartManager(self)
        self.machine_utils = MachineUtils(self)

        self.calculations = Calculations(self)

        self.server_executor = ServerExecutor(self)

        self.main_signals = None
        self.main_window = None

        self.get_from_config()

    def get_from_config(self):
        if "server" in self.config_manager:
            if "host" in self.config_manager["server"]:
                self.net_manager.host = self.config_manager["server"]["host"]

            if "auto_login_enabled" in self.config_manager["server"]:
                if self.config_manager.getboolean("server", "auto_login_enabled"):
                    self.net_manager._auto_login = True
                    if "auto_login_username" in self.config_manager["server"]:
                        self.net_manager.username = self.config_manager["server"]["auto_login_username"]
                    if "auto_login_password" in self.config_manager["server"]:
                        self.net_manager.password = self.config_manager["server"]["auto_login_password"]
