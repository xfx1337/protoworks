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

def get_project_audit(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    project_id = data["project_id"]
    from_id = data["from_id"]
    to_id = data["to_id"]

    return json.dumps(db.audit.get_project_audit(project_id, from_id, to_id)), 200