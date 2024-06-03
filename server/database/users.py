from singleton import singleton

from uuid import uuid4
from datetime import datetime, timedelta

@singleton
class Users:
    def __init__(self, db):
        self.db = db
        # cursor = db.cursor
        # connection = db.connection 
        
        connection, cursor = self.db.get_conn_cursor()

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id serial PRIMARY KEY,
            username VARCHAR(255),
            password VARCHAR(255),
            privileges VARCHAR(255)
        ) 
        """)

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS tokens (
            id serial PRIMARY KEY,
            username VARCHAR(255),
            token VARCHAR(255),
            expiration INT
        )
        """)

        self.remove_token("BYPASS")
        self.register_token("BYPASS", expiration=datetime.now() + timedelta(weeks=512))

        self.db.close(connection)

    def register(self, username, password, privileges="user"):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"""
        SELECT * FROM users WHERE username = %s
        """, [username])
        content = cursor.fetchone()

        if content != None:
            if password != content[2] or privileges != content[3]:
                with self.lock:
                    cursor.execute(f"""
                    UPDATE users SET password = %s WHERE username = %s
                    """, [password, username])
                    cursor.execute(f"""
                    UPDATE users SET privileges = %s WHERE username = %s
                    """, [privileges, username])
                    connection.commit()
                self.db.close(connection)
                return 0
            self.db.close(connection)
            return "nothing changed"
        cursor.execute(f"""
        INSERT INTO users (username, password, privileges) VALUES (%s, %s, %s)
        """, [username, password, privileges])
        connection.commit()
        self.db.close(connection)
        return 0

    
    def login(self, username, password):
        connection, cursor = self.db.get_conn_cursor()
        content = None
        cursor.execute(f"""
        SELECT * FROM users WHERE username = %s
        """, [username])

        content = cursor.fetchone()
        
        if content == None:
            self.db.close(connection)
            return -1, "No user with username", 
            
        if content[2] != password:
            self.db.close(connection)
            return -1, "Wrong password"
        self.db.close(connection)
        
        return 0, self.get_token(username)

    def register_token(self, username, expiration=-1):
        if expiration == -1:
            expiration = datetime.now() + timedelta(hours=24)
        connection, cursor = self.db.get_conn_cursor()
        rand_token = str(uuid4())
        cursor.execute(f"""
        INSERT INTO tokens (username, token, expiration) VALUES (%s, %s, %s)
        """, [username, rand_token, int(round(expiration.timestamp()))])
        connection.commit()
        self.db.close(connection)
        return rand_token

    def valid_token(self, token):
        if token == None:
            return False
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"""
        SELECT * FROM tokens WHERE token = %s
        """, [token])    
        
        content = cursor.fetchone()
        if content == None:
            return False
        self.db.close(connection)
        return datetime.now().timestamp() <= content[3]

    def valid_bearer(self, token):
        if token == None:
            return False
        return valid(token.split()[1])

    def get_token(self, username):
        connection, cursor = self.db.get_conn_cursor()
        content = None
        cursor.execute(f"""
        SELECT * FROM tokens WHERE username = %s
        """, [username])
        content = cursor.fetchone()

        if content == None:
            return self.register_token(username)

        if datetime.now().timestamp() > content[3]:
            cursor.execute(f"""
            DELETE FROM tokens WHERE token = %s
            """, [content[2]])
            connection.commit()
            return self.register_token(username)

        self.renew_token(username)
        self.db.close(connection)
        return content[2]

    def remove_token(self, username):
        connection, cursor = self.db.get_conn_cursor()
        cursor.execute(f"""
        SELECT * FROM tokens WHERE username = %s
        """, [username])
        content = cursor.fetchone()

        if content == None:
            return 0, "Token removed"
        cursor.execute(f"""
        DELETE FROM tokens WHERE token = %s
        """, [content[2]])
        connection.commit()
        self.db.close(connection)
        return 0, "Token removed"


    def get_username(self, token):
        connection, cursor = self.db.get_conn_cursor()
        if "Bearer" in token:
            token = token.split()[1]
        cursor.execute(f"""
        SELECT username FROM tokens
        WHERE TOKEN=%s
        """, [token])
        connection.commit()
        self.db.close(connection)
        return cursor.fetchone()[0]

    def renew_token(self, username):
        connection, cursor = self.db.get_conn_cursor()
        content = None
        cursor.execute(f"""
        SELECT token FROM tokens WHERE username = %s
        """, [username])
        content = cursor.fetchone()

        if content == None:
            return self.register_token(username)
            
        expiration = datetime.now() + timedelta(hours=24)

        cursor.execute(f"""
        UPDATE tokens SET expiration = %s WHERE username = %s
        """, [int(round(expiration.timestamp())), username])
        connection.commit()
        
        self.db.close(connection)
        return 0