from singleton import singleton

@singleton
class ProgramsConfigs:
    def __init__(self, db):
        self.db = db
        connection, cursor = self.db.get_conn_cursor()

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS programs_configs (
            id serial,
            program_name VARCHAR(255) UNIQUE,
            program_user_alias VARCHAR(255),
            last_synced_date INT,
            update_id TEXT
        )
        """)
        self.db.close(connection)
    
    def get_configs_sync_data(self):
        connection, cursor = self.db.get_conn_cursor()
        sql = "SELECT * from programs_configs"
        cursor.execute(sql)
        content = cursor.fetchall()
        self.db.close(connection)

        ret = {}
        if content != None:
            for p in content:
                ret[p[1]] = {"date": p[3], "update_id": p[4], "program_user_alias": p[2], "program_name": p[1]}
        return ret
    
    def set_program_data(self, program_name, program_user_alias=None, last_synced_date=None, update_id=None):
        connection, cursor = self.db.get_conn_cursor()

        data = self.get_configs_sync_data()
        if program_name in data:
            if last_synced_date == None:
                last_synced_date = data[program_name]["date"]
            if update_id == None:
                update_id = data[program_name]["update_id"]
            if program_user_alias == None:
                program_user_alias = data[program_name]["program_user_alias"]

        write_sql = f"INSERT INTO programs_configs (program_name, last_synced_date, update_id, program_user_alias) VALUES ('{program_name}', {last_synced_date}, '{update_id}', '{program_user_alias}') ON CONFLICT (program_name) DO UPDATE SET last_synced_date=excluded.last_synced_date, update_id=excluded.update_id, program_user_alias=excluded.program_user_alias"
        cursor.execute(write_sql)
        connection.commit()
        self.db.close(connection)
    
    def delete(self, program_name):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute("DELETE FROM programs_configs WHERE program_name=%s", [program_name])
        connection.commit()
        self.db.close(connection)