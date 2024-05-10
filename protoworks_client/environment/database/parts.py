from singleton import singleton

@singleton
class Parts:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 
        self.db = db

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS parts (
            id serial PRIMARY KEY,
            project_id INT,
            name VARCHAR(255),
            origin_path VARCHAR(255),
            count_need INT,
            count_done INT,
            status INT
        )
        """)

    def add_part(self, project_id, part_name, part_id, origin_path):
        pass