from singleton import singleton

import psycopg2
from psycopg2 import pool

from database.users import Users
from database.projects import Projects
from database.files import Files
from database.materials import Materials
from database.parts import Parts
from database.programs_configs import ProgramsConfigs
from database.machines import Machines
from database.work_queue import WorkQueue
from database.storage import Storage
from database.audit import Audit
from database.files_logging import FilesLogging
from database.machines import Machines
from database.slaves import Slaves
from database.hub import Hub
from database.monitoring import Monitoring
from database.external_bindings import Bindings
from config import Config
import exceptions

@singleton
class Database:
    def __init__(self):
        self.connected = 0

        cfg = {}
        try: cfg = Config('config.ini')
        except InvalidConfig as e:
            print(e)
            sys.exit()
        
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(5, 50, dbname='protoworks', 
            user='postgres', password=cfg["database"]["db_pass"], host='localhost')
        except:
            raise exceptions.DatabaseInitFailed("failed to init db")
        if not self.connection_pool:
            raise exceptions.DatabaseInitFailed("failed to init db")

        connection = self.connection_pool.getconn()
        connection.autocommit = True
        self.connection_pool.putconn(connection)

        self.users = Users(self)
        self.projects = Projects(self)
        self.files = Files(self)
        self.materials = Materials(self)
        self.parts = Parts(self)
        self.programs_configs = ProgramsConfigs(self)
        self.machines = Machines(self)
        self.work_queue = WorkQueue(self)
        self.storage = Storage(self)
        self.audit = Audit(self)
        self.files_logging = FilesLogging(self)
        self.hub = Hub(self)
        self.slaves = Slaves(self)
        self.machines = Machines(self)
        self.monitoring = Monitoring(self)
        self.bindings = Bindings(self)

    def get_conn_cursor(self):
        self.connected += 1
        connection = self.connection_pool.getconn()
        cursor = connection.cursor()
        return connection, cursor
    def close(self, conn):
        conn.cursor().close()
        self.connection_pool.putconn(conn)
        self.connected -= 1
        #print(f"connected: {self.connected}/20")
        # sometime before, without that line program was just crashing