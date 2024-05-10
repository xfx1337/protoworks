from singleton import singleton

from ping3 import ping, verbose_ping
import socket

import requests

@singleton
class Hub:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 
        self.db = db

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS hub (
            id serial PRIMARY KEY,
            hostname VARCHAR(255),
            ip VARCHAR(255)
        )
        """)
    
    def get_hub_info(self):
        self.cursor.execute("SELECT * FROM hub")
        c = self.cursor.fetchone()
        if c == None:
            return None

        hostname = c[1]
        ip = c[2]
        d = {"hostname": c[1], "ip": c[2]}
        return d
        
    
    def set_hub_info(self, hostname, ip):
        self.cursor.execute(f"INSERT INTO hub (id, hostname, ip) VALUES (0, '{hostname}', '{ip}') ON CONFLICT (id) DO UPDATE SET hostname=excluded.hostname, ip=excluded.ip")
        self.connection.commit()