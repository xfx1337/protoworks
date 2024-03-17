from singleton import singleton

from datetime import datetime as dt

import common

@singleton
class Projects:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS projects (
            id serial PRIMARY KEY,
            name VARCHAR(255),
            customer VARCHAR(255),
            description VARCHAR(2048),
            time_registered INT,
            time_deadline INT,
            status INT DEFAULT 0,
            server_path VARCHAR(255)
        )
        """)
    
    def get_projects(self):
        self.cursor.execute(f"""
        SELECT * FROM projects
        """)
        content = self.cursor.fetchall()
        print(content)
        data = {"projects": []}
        for p in content:
            project = {"id": p[0], "name": p[1], "customer": p[2], "description": p[3], "time_registered": p[4], "time_deadline": p[5], "status": p[6], "server_path": p[7]}
            data["projects"].append(project)
        return data
    
    def get_project_info(self, project_id):
        self.cursor.execute(f"""
        SELECT * FROM projects WHERE id = %s
        """, [project_id])
        p = self.cursor.fetchone()
        project = {"id": p[0], "name": p[1], "customer": p[2], "description": p[3], "time_registered": p[4], "time_deadline": p[5], "status": p[6], "server_path": p[7]}
        return project

    def create_project(self, name, customer, description, deadline, path):
        self.cursor.execute(f"""
        INSERT INTO projects (name, description, customer, time_registered, time_deadline, server_path) VALUES(%s,%s,%s,%s,%s,%s) RETURNING ID
        """, [name, description, customer, dt.now().timestamp(),deadline, path])

        self.connection.commit()
        return str(self.cursor.fetchone()[0])
    
    def delete_project(self, id):
        self.cursor.execute(f"""
        DELETE FROM projects WHERE id = %s""", [id])
        self.connection.commit()
        return 1
    
    def pass_project(self, id):
        self.cursor.execute(f"""
        UPDATE projects SET status = %s WHERE id = %s""", [common.PROJECT_DONE, id])
        self.connection.commit()
        return 1