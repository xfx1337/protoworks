from singleton import singleton

@singleton
class Parts:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS parts (
            id serial PRIMARY KEY,
            number INT,
            project_id INT,
            name VARCHAR(255),
            count_need INT,
            count_done INT
        )
        """)