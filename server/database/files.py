from singleton import singleton

@singleton
class Files:
    def __init__(self, db):
        self.db = db
        connection, cursor = self.db.get_conn_cursor()
        
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS files (
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
        cursor.execute(write_sql)
        connection.commit()
        self.db.close(connection)

        self.db.files_logging.register_update(data)

    def delete_file(self, file_path):
        connection, cursor = self.db.get_conn_cursor()
        delete_sql = f"DELETE FROM files WHERE path = '{file_path}'"
        cursor.execute(delete_sql)
        connection.commit()
        self.db.close(connection)

    def remove_logs(self, project_id):
        connection, cursor = self.db.get_conn_cursor()
        delete_sql = f"DELETE FROM files WHERE project_id={project_id}"
        cursor.execute(delete_sql)
        connection.commit()
        self.db.close(connection)
        self.db.files_logging.remove_logs(project_id)
        


    def get_modification_time_for_list(self, files):
        connection, cursor = self.db.get_conn_cursor()
        files_str = ""
        for f in files:
            files_str += ("'" + f + "', ")
        files_str = files_str[:-2]
        if len(files_str) < 1:
            return {}
        read_sql = f"SELECT path, date_modified FROM files WHERE path in ({files_str})"
        cursor.execute(read_sql)
        content = cursor.fetchall()

        if content == None:
            return []
        
        dc = {}
        for row in content:
            dc[row[0]] = int(row[1])
        self.db.close(connection)
        return dc