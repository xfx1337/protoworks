from singleton import singleton

from uuid import uuid4
from datetime import datetime, timedelta

@singleton
class Users:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor
        self.connection = db.connection 

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id serial PRIMARY KEY,
            username VARCHAR(255),
            password VARCHAR(255),
            privileges VARCHAR(255)
        ) 
        """)

        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS tokens (
            id serial PRIMARY KEY,
            username VARCHAR(255),
            token VARCHAR(255),
            expiration INT
        )
        """)

    def register(self, username, password, privileges="user"):
        self.cursor.execute(f"""
        SELECT * FROM users WHERE username = %s
        """, [username])
        content = self.cursor.fetchone()

        if content != None:
            if password != content[2] or privileges != content[3]:
                with self.lock:
                    self.cursor.execute(f"""
                    UPDATE users SET password = %s WHERE username = %s
                    """, [password, username])
                    self.cursor.execute(f"""
                    UPDATE users SET privileges = %s WHERE username = %s
                    """, [privileges, username])
                    self.connection.commit()
                return 0

            return "nothing changed"
        self.cursor.execute(f"""
        INSERT INTO users (username, password, privileges) VALUES (%s, %s, %s)
        """, [username, password, privileges])
        self.connection.commit()
        return 0

    
    def login(self, username, password):
        content = None
        self.cursor.execute(f"""
        SELECT * FROM users WHERE username = %s
        """, [username])

        content = self.cursor.fetchone()
        
        if content == None:
            return -1, "No user with username", 
            
        if content[2] != password:
            return -1, "Wrong password"
        return 0, self.get_token(username)

    def register_token(self, username):
        rand_token = str(uuid4())
        expiration = datetime.now() + timedelta(hours=24)
        self.cursor.execute(f"""
        INSERT INTO tokens (username, token, expiration) VALUES (%s, %s, %s)
        """, [username, rand_token, int(round(expiration.timestamp()))])
        self.connection.commit()

        return rand_token

    def valid_token(self, token):
        if token == None:
            return False
        self.cursor.execute(f"""
        SELECT * FROM tokens WHERE token = %s
        """, [token])    
        
        content = self.cursor.fetchone()
        if content == None:
            return False

        return datetime.now().timestamp() <= content[3]

    def valid_bearer(self, token):
        if token == None:
            return False
        return valid(token.split()[1])

    def get_token(self, username):
        content = None
        self.cursor.execute(f"""
        SELECT * FROM tokens WHERE username = %s
        """, [username])
        content = self.cursor.fetchone()

        if content == None:
            return self.register_token(username)

        if datetime.now().timestamp() > content[3]:
            self.cursor.execute(f"""
            DELETE FROM tokens WHERE token = %s
            """, [content[2]])
            self.connection.commit()
            return self.register_token(username)

        self.renew_token(username)
        return content[2]

    def remove_token(self, username):
        self.cursor.execute(f"""
        SELECT * FROM tokens WHERE username = %s
        """, [username])
        content = self.cursor.fetchone()

        if content == None:
            return 0, "Token removed"
        self.cursor.execute(f"""
        DELETE FROM tokens WHERE token = %s
        """, [content[2]])
        self.connection.commit()
        
        return 0, "Token removed"


    def get_username(self, token):
        if "Bearer" in token:
            token = token.split()[1]
        self.cursor.execute(f"""
        SELECT username FROM tokens
        WHERE TOKEN=%s
        """, [token])
        self.connection.commit()

        return self.cursor.fetchone()[0]

    def renew_token(self, username):
        content = None
        self.cursor.execute(f"""
        SELECT token FROM tokens WHERE username = %s
        """, [username])
        content = self.cursor.fetchone()

        if content == None:
            return self.register_token(username)
            
        expiration = datetime.now() + timedelta(hours=24)

        self.cursor.execute(f"""
        UPDATE tokens SET expiration = %s WHERE username = %s
        """, [int(round(expiration.timestamp())), username])
        self.connection.commit()
        
        return 0