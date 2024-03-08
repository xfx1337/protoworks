from singleton import singleton

@singleton
class Materials:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS materials (
            id serial PRIMARY KEY,
            project_id INT,
            material_name VARCHAR(255),
            server_path VARCHAR(255),
            url VARCHAR(255)
        )
        """)
