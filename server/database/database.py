from singleton import singleton

import psycopg2

from database.users import Users
from database.projects import Projects
from database.files import Files
from database.materials import Materials
from database.parts import Parts
from database.programs_configs import ProgramsConfigs
from database.machines import Machines
from database.work_order_parts import WorkOrderParts
from database.storage import Storage
from database.audit import Audit
from database.files_logging import FilesLogging
from database.machines import Machines
from database.slaves import Slaves
from database.hub import Hub
from database.monitoring import Monitoring

import exceptions

@singleton
class Database:
    def __init__(self):
        try: self.connection = psycopg2.connect(dbname='protoworks', user='postgres', password='Flvbybcnhfnjh', host='localhost')
        except: raise exceptions.DatabaseInitFailed("failed to init db")
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

        self.users = Users(self)
        self.projects = Projects(self)
        self.files = Files(self)
        self.materials = Materials(self)
        self.parts = Parts(self)
        self.programs_configs = ProgramsConfigs(self)
        self.machines = Machines(self)
        self.work_order_parts = WorkOrderParts(self)
        self.storage = Storage(self)
        self.audit = Audit(self)
        self.files_logging = FilesLogging(self)
        self.hub = Hub(self)
        self.slaves = Slaves(self)
        self.machines = Machines(self)
        self.monitoring = Monitoring(self)