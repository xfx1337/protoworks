from singleton import singleton

@singleton
class Files:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 
        self.db = db
        
        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS files (
            id serial,
            path VARCHAR(255) PRIMARY KEY UNIQUE,
            date_modified INT,
            file_size INT,
            project_id INT
        )
        """)
    
    def register_update(self, data):
        if len(data) < 1:
            return
        write_sql = "INSERT INTO files (path, date_modified, file_size, project_id) VALUES "
        for f in data:
            path = f["path"]
            date = int(f["date_modified"])
            file_size = int(f["size"])
            project_id = None
            if "project_id" in f:
                project_id = int(f["project_id"])
            row = f"('{path}', {date}, {file_size}, {project_id}),"
            write_sql += row
        write_sql = write_sql[:-1]
        write_sql += "\nON CONFLICT (path) DO UPDATE SET date_modified=excluded.date_modified, file_size=excluded.file_size, project_id=excluded.project_id"
        self.cursor.execute(write_sql)
        self.connection.commit()

