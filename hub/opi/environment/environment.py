from singleton import singleton

import os

from environment.database.db import Database
from environment.machines.machines import Machines

import utils
import defines

@singleton
class Environment():
    def __init__(self):
        self.state = defines.NOT_STARTED
        self.db = Database()

        self.machines = Machines()