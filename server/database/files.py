from singleton import singleton

@singleton
class Files:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS files (
            id serial,
            path VARCHAR(255) PRIMARY KEY,
            date_modified INT,
            file_size INT,
            project_id INT
        )
        """)
    
    def register_update(self, data):
        write_sql = "INSERT INTO files (path, date_modified, file_size) VALUES "
        for f in data:
            path = f["path"]
            date = int(f["date_modified"])
            file_size = int(f["size"])
            row = f"('{path}', {date}, {file_size}),"
            write_sql += row
        write_sql = write_sql[:-1]
        write_sql += "\nON DUPLICATE KEY UPDATE date_modified=VALUES(date_modified), file_size=VALUES(file_size)"
        breakpoint()
        self.cursor.execute(write_sql)
        self.connection.commit()

