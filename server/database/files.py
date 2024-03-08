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
            file_size INT
        )
        """)
    
    def register_update(self, data):
        write_sql = "REPLACE INTO files (path, date_modified, file_size) VALUES "
        for f in data["files"]:
            path = f["path"]
            date = int(f["date_modified"])
            file_size = int(f["size"])
            row = f"({path}, {date}, {file_size}),"
            write_sql += row
        write_sql = write_sql[:-2]
        write_sql += ";"

        self.cursor.execute(write_sql)
        self.connection.commit()

