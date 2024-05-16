from singleton import singleton

from datetime import datetime as dt

import common

@singleton
class Projects:
    def __init__(self, db):
        self.db = db
        connection, cursor = self.db.get_conn_cursor()
        
        cursor.execute(f"""
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
        self.db.close(connection)
    
    def get_projects(self):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"""
        SELECT * FROM projects
        """)
        content = cursor.fetchall()
        data = {"projects": []}
        for p in content:
            project = {"id": p[0], "name": p[1], "customer": p[2], "description": p[3], "time_registered": p[4], "time_deadline": p[5], "status": p[6], "server_path": p[7]}
            data["projects"].append(project)
        self.db.close(connection)
        return data
    
    def get_project_info(self, project_id):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"""
        SELECT * FROM projects WHERE id = %s
        """, [project_id])
        p = cursor.fetchone()
        project = {"id": p[0], "name": p[1], "customer": p[2], "description": p[3], "time_registered": p[4], "time_deadline": p[5], "status": p[6], "server_path": p[7]}
        self.db.close(connection)
        return project

    def create_project(self, name, customer, description, deadline, path):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"""
        INSERT INTO projects (name, description, customer, time_registered, time_deadline, server_path) VALUES(%s,%s,%s,%s,%s,%s) RETURNING ID
        """, [name, description, customer, dt.now().timestamp(),deadline, path])

        connection.commit()
        self.db.close(connection)
        return str(cursor.fetchone()[0])
    
    def delete_project(self, id):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"""
        DELETE FROM projects WHERE id = %s""", [id])
        connection.commit()
        self.db.close(connection)
        return 1
    
    def pass_project(self, id):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"""
        UPDATE projects SET status = %s WHERE id = %s""", [common.PROJECT_DONE, id])
        connection.commit()
        self.db.close(connection)
        return 1