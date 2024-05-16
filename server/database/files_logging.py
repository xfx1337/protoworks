from singleton import singleton

@singleton
class FilesLogging:
    def __init__(self, db):
        self.db = db
        connection, cursor = self.db.get_conn_cursor()
        
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS files_logging (
            id serial,
            path VARCHAR(255) PRIMARY KEY UNIQUE,
            date_modified INT,
            file_size INT,
            project_id INT
        )
        """)
        self.db.close(connection)
    
    def register_update(self, data):
        connection, cursor = self.db.get_conn_cursor()
        if len(data) < 1:
            return
        write_sql = "INSERT INTO files_logging (path, date_modified, file_size, project_id) VALUES "
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
        cursor.execute(write_sql)
        connection.commit()
        self.db.close(connection)
    
    def remove_logs(self, project_id):
        connection, cursor = self.db.get_conn_cursor()
        delete_sql = f"DELETE FROM files_logging WHERE project_id={project_id}"
        cursor.execute(delete_sql)
        connection.commit()
        self.db.close(connection)

    def get(self, project_id):
        connection, cursor = self.db.get_conn_cursor()
        search_sql = f"SELECT * FROM files_logging WHERE project_id={project_id}"
        cursor.execute(search_sql)
        content = cursor.fetchall()
        data = {"files": []}
        for p in content:
            file = {"id": p[0], "path": p[1], "date_modified": p[2], "file_size": p[3], "project_id": p[4]}
            data["files"].append(file)
        self.db.close(connection)
        return data