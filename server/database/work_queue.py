from singleton import singleton

@singleton
class WorkQueue:
    def __init__(self, db):
        self.db = db
        
        connection, cursor = self.db.get_conn_cursor()

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS work_queue (
            id serial PRIMARY KEY,
            machine_id VARCHAR(255),
            work_time INT,
            work_start INT,
            status VARCHAR(255),
            index INT
        )
        """)

        self.db.close(connection)