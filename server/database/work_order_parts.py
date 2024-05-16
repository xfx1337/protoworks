from singleton import singleton

@singleton
class WorkOrderParts:
    def __init__(self, db):
        self.db = db
        
        connection, cursor = self.db.get_conn_cursor()

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS work_order_parts (
            id serial PRIMARY KEY,
            machine_id VARCHAR(255),
            work_time INT,
            work_start INT,
            status VARCHAR(255)
        )
        """)

        self.db.close(connection)