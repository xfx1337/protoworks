from singleton import singleton

import utils

import json

@singleton
class Monitoring:
    def __init__(self, db):
        self.db = db
        connection, cursor = self.db.get_conn_cursor()

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS monitoring (
            id serial,
            device VARCHAR(255) PRIMARY KEY,
            time_scanned INT,
            status VARCHAR(255),
            info VARCHAR(1048576)
        )
        """)
        self.db.close(connection)
    
    def update(self, date, device, status, info):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute("INSERT INTO monitoring (device, time_scanned, status, info) VALUES (%s, %s, %s, %s) ON CONFLICT (device) DO UPDATE SET time_scanned=excluded.time_scanned, status=excluded.status, info=excluded.info", 
        (device, date, status, info))
        connection.commit()
        self.db.close(connection)
    
    def get_device(self, device):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"SELECT * FROM monitoring WHERE device='{device}'")
        c = cursor.fetchone()
        if c == None:
            d = {"device": device, "date": 0, "status": "not registered", "info": {}}
        else:
            try:
                x = json.loads(c[4])
            except:
                x = {}
            d = {"device": device, "date": c[2], "status": c[3], "info": x}
        self.db.close(connection)
        return d
    
    def get_by_status(self, status):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"SELECT * FROM monitoring WHERE status={status}")
        d = cursor.fetchall()
        devices = []
        for c in d:
            dev = {"device": device, "date": c[2], "status": c[3], "info": json.loads(c[4])}
            devices.append(dev)
        
        self.db.close(connection)
        return devices

    def clear_db(self):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute("DELETE FROM monitoring")
        connection.commit()
        self.db.close(connection)