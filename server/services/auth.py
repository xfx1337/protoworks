import utils

from database.database import Database

from common import *

db = Database()

def login(request):
    data = request.get_json()
    ret, token = db.users.login(data["username"], data["password"])
    if ret != 0:
        return token, 400
    else:
        return utils.json_str({"token": token}), 200