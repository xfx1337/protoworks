from singleton import singleton

import json

@singleton
class Configs:
    def __init__(self, db):
        self.cursor = db.cursor
        self.connection = db.connection 
        self.db = db
        
        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS configs (
            id serial PRIMARY KEY,
            program_name TEXT UNIQUE,
            links TEXT,
            files TEXT,
            dirs TEXT,
            program_exe_path TEXT
        )
        """)

    def get_configs_data(self, program_name): # fuck that serializing
        sql = f"SELECT * from configs WHERE program_name='{program_name}'"
        self.cursor.execute(sql)
        content = self.cursor.fetchone()
        out = []
        for i in range(len(content)):
            try:
                out.append(content[i])
                out[i] = json.loads('{"content": ' + content[i].replace("'", '"') + "}")["content"]
            except:
                pass
        content = out
        ret = {"program_name": content[1], "links": content[2], "files": content[3], "dirs": content[4], "program_exe_path": content[5]}
        return ret

    def set_configs(self, program_name, links='', dirs='', files='', program_exe_path=''):
        try:
            data = self.get_configs_data(program_name)
            if links == '':
                links = data["links"]
            if dirs == '':
                dirs = data["dirs"]
            if files == '':
                files = data["files"]
            if program_exe_path == '':
                program_exe_path = data["program_exe_path"]
        except:
            pass

        self.cursor.execute("INSERT INTO configs (program_name, links, files, dirs, program_exe_path) VALUES (?,?,?,?,?) ON CONFLICT (program_name) DO UPDATE SET links=excluded.links, files=excluded.files, dirs=excluded.dirs, program_exe_path=excluded.program_exe_path",
        (program_name, str(links), str(files), str(dirs), program_exe_path))
        self.connection.commit()