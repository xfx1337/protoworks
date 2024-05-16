from singleton import singleton

@singleton
class Storage:
    def __init__(self, db):
        self.db = db
        
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS storage (
            id serial PRIMARY KEY,
            name VARCHAR(255),
            count INT,
            status VARCHAR(255)
        )
        """)
        self.db.close(connection)
