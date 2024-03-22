from singleton import singleton

@singleton
class Materials:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS materials (
            id serial,
            project_id INT,
            path VARCHAR(255) PRIMARY KEY UNIQUE,
            type INT
        )
        """)

    def add(self, project_id, files, m_type):
        write_sql = "INSERT INTO materials (project_id, path, type) VALUES "
        for f in files:
            row = f"({project_id}, '{f}', {m_type}),"
            write_sql += row
        write_sql = write_sql[:-1]
        write_sql += "\nON CONFLICT (path) DO UPDATE SET type=excluded.type"
        self.cursor.execute(write_sql)
        self.connection.commit()
    
    def get(self, project_id, m_type):
        data = {"materials": []}
        if m_type == None:
            sql_get = f"SELECT * FROM materials WHERE project_id={project_id}"
        else:
            sql_get = f"SELECT * FROM materials WHERE project_id={project_id} AND type={m_type}"

        self.cursor.execute(sql_get)
        content = self.cursor.fetchall()
        for d in content:
            data["materials"].append({"path": d[2], "type": d[3]})

        return data