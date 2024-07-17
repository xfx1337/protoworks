from singleton import singleton

import psycopg2
import sqlite3

from environment.database.projects_sync import ProjectsSync
from environment.database.parts import Parts

@singleton
class Database:
    def __init__(self):
        # try: self.connection = psycopg2.connect(dbname='protoworks_client', user='postgres', password='Flvbybcnhfnjh', host='localhost')
        # except: raise exceptions.DatabaseInitFailed("failed to init db")
        try: self.connection = sqlite3.connect("database_protoworks.db", check_same_thread=False)
        except: raise exceptions.DatabaseInitFailed("failed to init db")
        #self.connection.autocommit = True
        self.cursor = self.connection.cursor()

        self.projects_sync = ProjectsSync(self)
        self.parts = Parts(self)