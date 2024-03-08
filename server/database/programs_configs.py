from singleton import singleton

@singleton
class ProgramsConfigs:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS programs_configs (
            id serial PRIMARY KEY,
            program_name VARCHAR(255),
            name VARCHAR(255),
            description VARCHAR(255),
            sync BOOLEAN,
            path VARCHAR(255)
        )
        """)