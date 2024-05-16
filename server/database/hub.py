from singleton import singleton

from ping3 import ping, verbose_ping
import socket

import requests

@singleton
class Hub:
    def __init__(self, db):
        self.db = db
        connection, cursor = self.db.get_conn_cursor()

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS hub (
            id serial PRIMARY KEY,
            hostname VARCHAR(255),
            ip VARCHAR(255)
        )
        """)
        self.db.close(connection)
    
    def get_hub_info(self):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute("SELECT * FROM hub")
        c = cursor.fetchone()
        if c == None:
            return None

        hostname = c[1]
        ip = c[2]
        d = {"hostname": c[1], "ip": c[2]}
        self.db.close(connection)
        return d
        
    
    def set_hub_info(self, hostname, ip):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"INSERT INTO hub (id, hostname, ip) VALUES (0, '{hostname}', '{ip}') ON CONFLICT (id) DO UPDATE SET hostname=excluded.hostname, ip=excluded.ip")
        connection.commit()
        self.db.close(connection)