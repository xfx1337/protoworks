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
            unique_info VARCHAR(1024),
            slave_id INT,
            delta_radius INT,
            delta_height INT,
            gcode_manager INT,
            baudrate INT
        )
        """)
    
    def add_machine(self, name, slave_id, unique_info, plate, delta, gcode_manager, baudrate):
        x = plate["x"]
        y = plate["y"]
        z = plate["z"]
        delta_radius = delta["radius"]
        delta_height = delta["height"]
        unique_info = str(unique_info)
        self.cursor.execute("INSERT into machines (name, x, y, z, unique_info, slave_id, delta_radius, delta_height, gcode_manager, baudrate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
        (name, x, y, z, unique_info, slave_id, delta_radius, delta_height, gcode_manager, baudrate))
        self.connection.commit()
    
    def edit_machine(self, idx, name, unique_info, plate, delta, gcode_manager, baudrate):
        x = plate["x"]
        y = plate["y"]
        z = plate["z"]
        delta_radius = delta["radius"]
        delta_height = delta["height"]
        unique_info = str(unique_info)
        self.cursor.execute("UPDATE machines SET name=%s, x=%s, y=%s, z=%s, unique_info=%s, slave_id=%s, delta_radius=%s, delta_height=%s, gcode_manager=%s, baudrate=%s", 
        (name, x, y, z, unique_info, slave_id, delta_radius, delta_height, gcode_manager, baudrate))
        self.connection.commit()

    def get_machines_list(self, slave_idx):
        if slave_idx == -1:
            self.cursor.execute("SELECT * FROM machines")
        else:
            self.cursor.execute(f"SELECT * FROM machines WHERE slave_id={int(slave_idx)}")
        content = self.cursor.fetchall()

        machines = []
        for s in content:
            machine = {"id": s[0], "plate": {"x": s[2], "y": s[3], "z": s[4]}, "name": s[1], "unique_info": s[5], "slave_id": s[6],
            "delta": {"radius": s[7], "height": s[8]}, "gcode_manager": s[9], "baudrate": s[10]}
            machines.append(machine)
        return machines

    def get_machine(self, idx):
        self.cursor.execute(f"SELECT * FROM machines WHERE id={idx}")
        s = self.cursor.fetchone()
        machine = {"id": s[0], "plate": {"x": s[2], "y": s[3], "z": s[4]}, "name": s[1], "unique_info": s[5], "slave_id": s[6],
            "delta": {"radius": s[7], "height": s[8]}, "gcode_manager": s[9], "baudrate": s[10]}
        return machine
