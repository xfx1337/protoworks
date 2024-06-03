from singleton import singleton

import utils

import json

@singleton
class Bindings:
    def __init__(self, db):
        self.db = db

        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS bindings (
            id serial PRIMARY KEY,
            event VARCHAR(255),
            action VARCHAR(255)
        )
        """)
        self.db.close(connection)

    def get_actions(self, event):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute("SELECT * FROM bindings WHERE event=%s", [event])
        rows = cursor.fetchall()
        actions = []
        for a in rows:
            actions.append(json.loads(a[2]))
        
        self.db.close(connection)
        return actions

    def add_bind(self, event, action):
        connection, cursor = self.db.get_conn_cursor()

        cursor.execute("INSERT INTO bindings (event, action) VALUES (%s, %s)", [event, json.dumps(action)])
        connection.commit()

        self.db.close(connection)

    def remove_bind(self, event, action):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute("SELECT * FROM bindings WHERE event=%s AND action=%s", [event, json.dumps(action)])
        c = cursor.fetchone()
        if c != None and c != []:
            idx = c[0]
            cursor.execute("DELETE FROM bindings WHERE id=%s", [idx])
            connection.commit()
        self.db.close(connection)
    
    def get_event_by_action(self, action):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute("SELECT * FROM bindings WHERE action=%s", [json.dumps(action)])
        c = cursor.fetchone()
        if c == None:
            c = ""
        else:
            c = c[1]
        self.db.close(connection)
        return c