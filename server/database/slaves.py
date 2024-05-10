from singleton import singleton

@singleton
class Slaves:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 
        self.db = db

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS slaves (
            id serial PRIMARY KEY,
            hostname VARCHAR(255),
            ip VARCHAR(255),
            type INT
        )
        """)
    
    def add(self, hostname, ip, s_type):
        self.cursor.execute(f"INSERT INTO slaves (hostname, ip, type) VALUES ('{hostname}', '{ip}', {s_type})")
        self.connection.commit()
    
    def get_slaves_list(self, type_s):
        if type_s == -1:
            self.cursor.execute("SELECT * FROM slaves")
        else:
            self.cursor.execute(f"SELECT * FROM slaves WHERE type={int(type_s)}")
        content = self.cursor.fetchall()

        slaves = []
        for s in content:
            slave = {"id": s[0], "hostname": s[1], "ip": s[2], "type": s[3]}
            slaves.append(slave)
        return slaves
    
    def edit(self, idx, ip, hostname):
        self.cursor.execute(f"UPDATE slaves SET ip='{ip}', hostname='{hostname}' WHERE id={str(idx)}")
        self.connection.commit()