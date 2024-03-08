from singleton import singleton

@singleton
class WorkOrderParts:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS work_order_parts (
            id serial PRIMARY KEY,
            machine_id VARCHAR(255),
            work_time INT,
            work_start INT,
            status VARCHAR(255)
        )
        """)