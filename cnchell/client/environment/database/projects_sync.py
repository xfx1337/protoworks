from singleton import singleton

@singleton
class ProjectsSync:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 
        self.db = db
        
        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS projects_sync (
            id serial,
            project_id INT UNIQUE,
            last_synced_client_date INT,
            update_id TEXT
        )
        """)
    
    def get_projects_sync_data(self):
        sql = "SELECT * from projects_sync"
        self.cursor.execute(sql)
        content = self.cursor.fetchall()
        ret = {}
        if content != None:
            for p in content:
                ret[p[1]] = {"date": p[2], "update_id": p[3]}
        return ret
    
    def set_project_sync_date(self, project_id, date, update_id):
        write_sql = f"INSERT INTO projects_sync (project_id, last_synced_client_date, update_id) VALUES ({project_id}, {date}, '{update_id}') ON CONFLICT (project_id) DO UPDATE SET last_synced_client_date=excluded.last_synced_client_date, update_id=excluded.update_id"
        self.cursor.execute(write_sql)
        self.connection.commit()
    