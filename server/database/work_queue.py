from singleton import singleton

import json

@singleton
class WorkQueue:
    def __init__(self, db):
        self.db = db
        
        connection, cursor = self.db.get_conn_cursor()

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS work_queue (
            id serial PRIMARY KEY,
            machine_id INT,
            work_time INT,
            work_start INT,
            status VARCHAR(255),
            index INT,
            unique_info VARCHAR(1024)
        )
        """)

        self.db.close(connection)

    def get_jobs(self, idx):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute("SELECT * FROM work_queue WHERE machine_id=%s", [idx])
        content = cursor.fetchall()
        self.db.close(connection)
        queue = []
        for c in content:
            try:
                unique_info = json.loads(c[6])
            except:
                unique_info = c[6]
            w = {"id": c[0], "machine_id": c[1], "work_time": c[2], "work_start": c[3], "status": c[4], "index": c[5], "unique_info": unique_info}
            queue.append(w)
        
        queue = sorted(queue, key=lambda d: d["index"])
        return queue

    def get_last_index(self, machine_id):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute("SELECT index FROM work_queue WHERE machine_id=%s ORDER BY index DESC LIMIT 1", [machine_id])
        last_index = cursor.fetchone()
        if last_index == None:
            last_index = -1
        else:
            last_index = last_index[0]

        self.db.close(connection)
        return last_index

    def insert_job(self, job, idx=-1):
        connection, cursor = self.db.get_conn_cursor()

        machine_id = job["machine_id"]
        work_time = job["work_time"]
        work_start = job["work_start"]
        status = job["status"]
        unique_info = json.dumps(job["unique_info"])

        if idx == -1:
            idx = self.get_last_index(machine_id)+1

        cursor.execute("UPDATE work_queue SET index = index + 1 WHERE index >= %s and machine_id = %s", [idx, machine_id])
        cursor.execute("INSERT INTO work_queue (machine_id, work_time, work_start, status, index, unique_info) VALUES (%s, %s, %s, %s, %s, %s)", 
        [machine_id, work_time, work_start, status, idx, unique_info])
        connection.commit()

        self.db.close(connection)

    def delete_jobs(self, indexes, machine_id):
        connection, cursor = self.db.get_conn_cursor()
        if type(indexes[0]) == list:
            indexes = indexes[0] # fuck
        for idx in indexes:
            cursor.execute("DELETE FROM work_queue WHERE index = %s AND machine_id = %s", [idx, machine_id])
        indexes = sorted(indexes, reverse=True)
        for idx in indexes:
            cursor.execute("UPDATE work_queue SET index = index - 1 WHERE index >= %s AND machine_id = %s", [idx, machine_id])
        connection.commit()

        self.db.close(connection)

    def overwrite_job(self, id, job):
        connection, cursor = self.db.get_conn_cursor()

        machine_id = job["machine_id"]
        work_time = job["work_time"]
        work_start = job["work_start"]
        status = job["status"]
        unique_info = json.dumps(job["unique_info"])
        index = job["index"]

        cursor.execute("UPDATE work_queue SET machine_id=%s, work_time=%s, work_start=%s, status=%s, index=%s, unique_info=%s WHERE id=%s", 
        [machine_id, work_time, work_start, status, index, unique_info, id])

        connection.commit()
        self.db.close(connection)

    def get_job_by_id(self, idx):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute("SELECT * FROM work_queue WHERE id=%s", [idx])
        c = cursor.fetchone()
        self.db.close(connection)    
        if c == None:
            return c
        ret = {"id": c[0], "machine_id": c[1], "work_time": c[2], "work_start": c[3], "status": c[4], "index": c[5], "unique_info": json.loads(c[6])}

        return ret

    def move_job(self, from_index, to_index, machine_id):
        connection, cursor = self.db.get_conn_cursor()
        if to_index == -1:
            cursor.execute("SELECT max(index) FROM work_queue WHERE machine_id=%s", [machine_id])
            to_index = cursor.fetchone()
            print(to_index)
            if to_index == None:
                to_index = 0
            elif type(to_index) == list or type(to_index) == tuple:
                to_index = to_index[0]
            else:
                to_index = to_index


        cursor.execute("UPDATE work_queue SET index = %s WHERE index = %s AND machine_id = %s", [-1, from_index, machine_id])
        if to_index < from_index:
            cursor.execute("UPDATE work_queue SET index = index + 1 WHERE index >= %s AND index < %s AND machine_id = %s", [to_index, from_index, machine_id])
        else: # to_index > from_index
            cursor.execute("UPDATE work_queue SET index = index - 1 WHERE index >= %s and index <= %s AND machine_id = %s", [from_index, to_index, machine_id])

        cursor.execute("UPDATE work_queue SET index = %s WHERE index = %s AND machine_id = %s", [to_index, -1, machine_id])

        connection.commit()
        self.db.close(connection)