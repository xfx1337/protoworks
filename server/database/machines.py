from singleton import singleton

@singleton
class Machines:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS machines (
            id serial PRIMARY KEY,
            name VARCHAR(255),
            machine_type VARCHAR(255),
            plate_size VARCHAR(255)
        )
        """)