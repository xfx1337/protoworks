import os

import utils

from database.database import Database
db = Database()

from config import Config
config = Config("config.ini")

from common import *

def get_projects(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    ret = db.projects.get_projects()
    return ret, 200

def get_project_info(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    ret = db.projects.get_project_info(data["project_id"])
    return ret, 200

def create_project(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    path = os.path.join((config["path"]["projects_path"]), data["name"])

    try: 
        os.mkdir(path)
        os.mkdir(os.path.join(path, "ДЕТАЛИ-PW"))
        os.mkdir(os.path.join(path, "МАТЕРИАЛЫ-PW"))
    except: return "Не удалось создать папку на сервере с таким именем. Пожалуйста решите проблему вручную или назовите проект другим именем.", 500


    ret = db.projects.create_project(name=data["name"], 
        customer=data["customer"], 
        deadline=int(data["deadline"]), 
        description=data["description"], path=path)

    if not ret:
        return "Не удалось создать проект", 400
    return ret, 200

def delete_project(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    ret = db.projects.delete_project(id=data["id"])
    if not ret:
        return "Не удалось удалить проект", 400
    return "Проект удалён", 200

def pass_project(request):
    data = request.get_json()
    ret = db.users.valid_token(data["token"])
    if not ret:
        return "Токен не валиден", 403
    
    ret = db.projects.pass_project(id=data["id"])
    if not ret:
        return "Не удалось сдать проект", 400
    return "Проект сдан"