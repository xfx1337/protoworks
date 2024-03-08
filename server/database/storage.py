from singleton import singleton

@singleton
class Storage:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS storage (
            id serial PRIMARY KEY,
            name VARCHAR(255),
            count INT,
            status VARCHAR(255)
        )
        """)