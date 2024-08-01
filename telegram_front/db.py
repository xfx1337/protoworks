import sqlite3
import threading

connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

lock = threading.Lock()

def exists() -> bool:
    cursor.execute(f"""
    SELECT name FROM sqlite_master WHERE type='table' AND name='users';
    """)

    connection.commit()

    return bool(len(cursor.fetchall()))

def create_database():
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER,
        username TEXT,
        privileges TEXT,
        PRIMARY KEY(id AUTOINCREMENT)
    ) 
    """)

    connection.commit()

    cursor.execute("SELECT * FROM users WHERE username = 'xfx1337'")
    content = cursor.fetchall()
    if content == []:
        cursor.execute(f"""
        INSERT INTO users (username, privileges) VALUES (?, ?)
        """, ["xfx1337", "owner"])
        connection.commit()

    connection.commit()

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER,
        logs_text TEXT,
        PRIMARY KEY(id AUTOINCREMENT)
    ) 
    """)

    connection.commit()

def recheck_owner():
    cursor.execute("SELECT * FROM users WHERE username = 'xfx1337'")
    content = cursor.fetchall()
    if content == []:
        cursor.execute(f"""
        INSERT INTO users (username, privileges) VALUES (?, ?)
        """, ["xfx1337", "owner"])
        connection.commit()

def get_users_list():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    content = cursor.fetchall()
    out = []
    for c in content:
        out.append({"username": c[1], "privileges": c[2]})
    return out

def add_user(username):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (username, privileges) VALUES (?, ?)", [username, "admin"])
    connection.commit()
    recheck_owner()

def delete_user(username):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE username=?", [username])
    recheck_owner()

def check_admin_sql(req):
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username=?", [req])
    content = cursor.fetchone()
    return content

def check_admin(message):
    i = message.chat.id
    ret = check_admin_sql(i)
    if ret == None:
        i = message.chat.username
        ret = check_admin_sql(i)
        return ret is not None

    return ret is not None

def get_logs():
    cursor = connection.cursor()
    cursor.execute("SELECT logs_text FROM logs")
    content = cursor.fetchone()
    if content == None:
        content = ""
    else:
        content = content[0]
    return content

def set_logs(logs):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM logs")
    connection.commit()
    cursor.execute("INSERT INTO logs (logs_text) VALUES (?)", [logs])
    connection.commit()