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
            id INT UNIQUE,
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
            part = {"id": p[1], "name": p[3], "path": p[4], "count_need": p[5], "count_done": p[6], "status": p[7]}
            parts.append(part)
        
        return parts
    
    def register_parts(self, project_id, parts):
        sql = f"SELECT max(id) FROM parts WHERE project_id={project_id}"
        self.cursor.execute(sql)
        start_id = self.cursor.fetchone()
        if start_id == None:
            start_id = 0
        elif start_id[0] == None:
            start_id = 0
        else:
            start_id = start_id[0] + 1


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

    def register_update(self, project_id, parts):
        ids_s = "("
        for p in parts:
            ids_s += (str(p["id"]) + ", ")
        ids_s = ids_s[:-2]
        ids_s += ")"
        sql_update = f"UPDATE parts SET status={common.PART_IN_WORK} WHERE status={common.PART_IN_COORDINATION} AND id IN {ids_s} AND project_id={project_id}"
        self.cursor.execute(sql_update)
        self.connection.commit()

        parts_db = f"SELECT * from parts WHERE id IN {ids_s}"
        self.cursor.execute(parts_db)
        content = self.cursor.fetchall()
        parts_db_dc = {}
        for p in content:
            d = p[1]
            parts_db_dc[d] = {"name": p[3], "path": p[4], "count_need": p[5], "count_done": p[6], "status": p[7]}

        sql_update = f"INSERT INTO parts (id, count_need, count_done, status) VALUES "
        for p in parts:
            if "count_need" not in p:
                p["count_need"] = parts_db_dc[p["id"]]["count_need"]
            if "count_done" not in p:
                p["count_done"] = parts_db_dc[p["id"]]["count_done"]
            if "status" not in p:
                p["status"] = parts_db_dc[p["id"]]["status"]
            
            count_need = p["count_need"]
            count_done = p["count_done"]
            status = p["status"]
            i = p["id"]

            row = f"\n({i}, {count_need}, {count_done}, {status}),"
            sql_update += row
        sql_update = sql_update[:-1]
        sql_update += "\nON CONFLICT (id) DO UPDATE SET count_need=excluded.count_need, count_done=excluded.count_done, status=excluded.status"
        self.cursor.execute(sql_update)
        self.connection.commit()
