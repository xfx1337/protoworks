from singleton import singleton

@singleton
class Machines:
    def __init__(self, db):
        self.db = db
        connection, cursor = self.db.get_conn_cursor()

        cursor.execute(f"""
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
        self.db.close(connection)
    
    def add_machine(self, name, slave_id, unique_info, plate, delta, gcode_manager, baudrate):
        connection, cursor = self.db.get_conn_cursor()
        x = plate["x"]
        y = plate["y"]
        z = plate["z"]
        delta_radius = delta["radius"]
        delta_height = delta["height"]
        unique_info = str(unique_info)
        cursor.execute("INSERT into machines (name, x, y, z, unique_info, slave_id, delta_radius, delta_height, gcode_manager, baudrate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
        (name, x, y, z, unique_info, slave_id, delta_radius, delta_height, gcode_manager, baudrate))
        connection.commit()
        self.db.close(connection)

    def edit_machine(self, idx, name, unique_info, plate, delta, gcode_manager, baudrate):
        connection, cursor = self.db.get_conn_cursor()
        x = plate["x"]
        y = plate["y"]
        z = plate["z"]
        delta_radius = delta["radius"]
        delta_height = delta["height"]
        unique_info = str(unique_info)
        cursor.execute("UPDATE machines SET name=%s, x=%s, y=%s, z=%s, unique_info=%s, slave_id=%s, delta_radius=%s, delta_height=%s, gcode_manager=%s, baudrate=%s", 
        (name, x, y, z, unique_info, slave_id, delta_radius, delta_height, gcode_manager, baudrate))
        connection.commit()
        self.db.close(connection)

    def get_machines_list(self, slave_idx):
        connection, cursor = self.db.get_conn_cursor()
        if slave_idx == -1:
            cursor.execute("SELECT * FROM machines")
        else:
            cursor.execute(f"SELECT * FROM machines WHERE slave_id={int(slave_idx)}")
        content = cursor.fetchall()

        machines = []
        for s in content:
            machine = {"id": s[0], "plate": {"x": s[2], "y": s[3], "z": s[4]}, "name": s[1], "unique_info": s[5], "slave_id": s[6],
            "delta": {"radius": s[7], "height": s[8]}, "gcode_manager": s[9], "baudrate": s[10]}
            machines.append(machine)
        self.db.close(connection)
        return machines

    def get_machine(self, idx):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"SELECT * FROM machines WHERE id={int(idx)}")
        s = cursor.fetchone()
        self.db.close(connection)
        if s == None:
            return None
        machine = {"id": s[0], "plate": {"x": s[2], "y": s[3], "z": s[4]}, "name": s[1], "unique_info": s[5], "slave_id": s[6],
            "delta": {"radius": s[7], "height": s[8]}, "gcode_manager": s[9], "baudrate": s[10]}
        return machine

    def delete(self, idx):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"""
        DELETE FROM machines WHERE id = %s""", [idx])
        connection.commit()
        self.db.close(connection)