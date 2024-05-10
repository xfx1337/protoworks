from singleton import singleton

import psycopg2

@singleton
class Database:
    def __init__(self):
        try: self.connection = psycopg2.connect(dbname='hub', user='postgres', password='Flvbybcnhfnjh', host='localhost')
        except: raise exceptions.DatabaseInitFailed("failed to init db")
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()