from singleton import singleton

@singleton
class Parts:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS parts (
            id serial PRIMARY KEY,
            project_id INT,
            name VARCHAR(255),
            parent VARCHAR(255),
            count INT,
            server_path VARCHAR(255),
            dimensions VARCHAR(255)
        )
        """)