from singleton import singleton

@singleton
class Slaves:
    def __init__(self, db):
        self.db = db

        connection, cursor = self.db.get_conn_cursor()

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS slaves (
            id serial PRIMARY KEY,
            hostname VARCHAR(255),
            ip VARCHAR(255),
            type INT
        )
        """)
        self.db.close(connection)
    
    def add(self, hostname, ip, s_type):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"INSERT INTO slaves (hostname, ip, type) VALUES ('{hostname}', '{ip}', {s_type})")
        connection.commit()
        self.db.close(connection)
    
    def get_slaves_list(self, type_s):
        connection, cursor = self.db.get_conn_cursor()
        if type_s == -1:
            cursor.execute("SELECT * FROM slaves")
        else:
            cursor.execute(f"SELECT * FROM slaves WHERE type={int(type_s)}")
        content = cursor.fetchall()

        slaves = []
        for s in content:
            slave = {"id": s[0], "hostname": s[1], "ip": s[2], "type": s[3]}
            slaves.append(slave)
        self.db.close(connection)
        return slaves
    
    def edit(self, idx, ip, hostname):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"UPDATE slaves SET ip='{ip}', hostname='{hostname}' WHERE id={str(idx)}")
        connection.commit()
        self.db.close(connection)
    
    def get_slave(self, idx):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"SELECT * FROM slaves WHERE id={idx}")
        s = cursor.fetchone()
        slave = {"id": s[0], "hostname": s[1], "ip": s[2], "type": s[3]}
        self.db.close(connection)
        return slave