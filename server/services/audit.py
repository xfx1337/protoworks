import utils

from database.database import Database

from common import *

import json

db = Database()

def get_projects_sync_data(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    return json.dumps(db.audit.get_projects_sync_data()), 200