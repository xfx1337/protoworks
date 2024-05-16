from singleton import singleton

import utils

import json

@singleton
class Audit:
    def __init__(self, db):
        self.db = db

        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS audit (
            id serial PRIMARY KEY,
            event VARCHAR(255),
            date INT,
            info VARCHAR(1048576),
            project_id INT
        )
        """)
        self.db.close(connection)
    
    def register_event(self, data):
        connection, cursor = self.db.get_conn_cursor()
        event = data["event"]
        project_id = None
        if "project_id" in data:
            project_id = int(data["project_id"])
        info = None
        if "info" in data:
            info = data["info"]
        date = utils.time_now()
        data["date"] = date
        write_sql = f"INSERT INTO audit (event, date, info, project_id) VALUES ('{event}', {date}, '{info}', {project_id})"
        cursor.execute(write_sql)
        connection.commit()
        self.db.close(connection)
        return data
    
    def get_projects_sync_data(self):
        connection, cursor = self.db.get_conn_cursor()
        projects = self.db.projects.get_projects()["projects"]
        ids = []
        for p in projects:
            ids.append(p["id"])

        ret = {"projects": {}}
        for i in ids:
            sql = f"SELECT * from audit WHERE project_id={i} ORDER BY date DESC limit 1"
            cursor.execute(sql)
            info = cursor.fetchone()
            if info != None:
                ret["projects"][int(info[-1])] = {"date": int(info[-3]), "update_id": str(json.loads(info[-2])["update_id"])}
        self.db.close(connection)
        return ret
    
    def get_project_audit(self, project_id, from_id, to_id):
        connection, cursor = self.db.get_conn_cursor()
        sql = f"SELECT * FROM audit WHERE project_id={project_id} ORDER BY date DESC LIMIT {to_id-from_id} OFFSET {from_id}"

        ret = {"audit": []}

        cursor.execute(sql)
        info = cursor.fetchall()
        if info != None:
            for a in info:
                ret["audit"].append({"event": a[1], "date": a[2], "info": a[3]})
        self.db.close(connection)
        return ret