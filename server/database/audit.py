from singleton import singleton

import utils

import json

@singleton
class Audit:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 
        self.db = db

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS audit (
            id serial PRIMARY KEY,
            event VARCHAR(255),
            date INT,
            info VARCHAR(1048576),
            project_id INT
        )
        """)
    
    def register_event(self, data):
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
        self.cursor.execute(write_sql)
        self.connection.commit()
        return data
    
    def get_projects_sync_data(self):
        projects = self.db.projects.get_projects()["projects"]
        ids = []
        for p in projects:
            ids.append(p["id"])

        ret = {"projects": {}}
        for i in ids:
            sql = f"SELECT * from audit WHERE project_id={i} ORDER BY date DESC limit 1"
            self.cursor.execute(sql)
            info = self.cursor.fetchone()
            if info != None:
                ret["projects"][int(info[-1])] = {"date": int(info[-3]), "update_id": str(json.loads(info[-2])["update_id"])}
        return ret