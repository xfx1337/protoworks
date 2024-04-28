from singleton import singleton

@singleton
class Machines:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 
        self.db = db

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS machines (
            id serial PRIMARY KEY,
            name VARCHAR(255),
            x INT,
            y INT,
            Z INT,
            port VARCHAR(255),
            type INT
        )
        """)