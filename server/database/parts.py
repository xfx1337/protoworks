from singleton import singleton

import common

@singleton
class Parts:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS parts (
            row_id serial PRIMARY KEY,
            id INT,
            project_id INT,
            name VARCHAR(255),
            origin_path VARCHAR(255),
            count_need INT,
            count_done INT,
            status INT
        )
        """)
    
    def get_parts(self, project_id):
        sql = f"SELECT * FROM parts WHERE project_id={project_id}"
        self.cursor.execute(sql)

        parts = []
        content = self.cursor.fetchall()
        for p in content:
            part = {"id": p[1], "name": p[2], "path": [3], "count_need": p[4], "count_done": p[5], "status": p[6]}
            parts.append(part)
        
        return parts
    
    def register_parts(self, project_id, parts):
        sql = f"SELECT max(id) FROM parts WHERE project_id={project_id}"
        start_id = self.cursor.fetchone()
        if start_id == None:
            start_id = 0
        else:
            start_id = start_id + 1

        sql_insert = "INSERT INTO parts (id, project_id, name, origin_path, count_need, count_done, status) VALUES "
        for i in range(len(parts)):
            name = parts[i]["name"]
            origin_path = parts[i]["origin_path"]
            sql_p = f"\n({start_id+i}, {project_id}, '{name}', '{origin_path}', 0, 0, {common.PART_IN_COORDINATION}),"
            sql_insert += sql_p
        sql_insert = sql_insert[:-1]

        self.cursor.execute(sql_insert)
        self.connection.commit()

        return start_id 
