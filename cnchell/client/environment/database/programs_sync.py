from singleton import singleton

@singleton
class ProgramsSync:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 
        self.db = db
        
        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS programs_sync (
            id serial PRIMARY KEY,
            program_name VARCHAR(255) UNIQUE,
            last_synced_client_date INT,
            update_id TEXT
        )
        """)
    
    def get_programs_sync_data(self):
        sql = "SELECT * from programs_sync"
        self.cursor.execute(sql)
        content = self.cursor.fetchall()
        ret = {}
        if content != None:
            for p in content:
                ret[p[1]] = {"date": p[2], "update_id": p[3]}
        return ret
    
    def set_program_sync_date(self, program_name, date, update_id):
        write_sql = f"INSERT INTO programs_sync (program_name, last_synced_client_date, update_id) VALUES ('{program_name}', {date}, '{update_id}') ON CONFLICT (program_name) DO UPDATE SET last_synced_client_date=excluded.last_synced_client_date, update_id=excluded.update_id"
        self.cursor.execute(write_sql)
        self.connection.commit()
    