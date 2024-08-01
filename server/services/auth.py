import utils

from database.database import Database

from common import *

import json

db = Database()

def login(request):
    data = request.get_json()
    ret, token = db.users.login(data["username"], data["password"])
    if ret != 0:
        return token, 400
    else:
        return utils.json_str({"token": token}), 200

def get_users_list(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    users = db.users.get_users_list()
    return json.dumps({"users": users}), 200

def register_user(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    username = data["username"]
    password = data["password"]

    db.users.register(username, password)

    return "registered", 200

def remove_user(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403

    username = data["username"]

    db.users.remove_user(username)
    return "removed", 200