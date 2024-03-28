import os, sys
import socket
import json

from flask import Flask, jsonify, request, Response
from flask_socketio import SocketIO, emit, send, Namespace
from flask_socketio import ConnectionRefusedError
from flask_cors import CORS

from exceptions import *
import utils
from config import Config

from database.database import Database

import services.auth
import services.projects
import services.files
import services.audit
import services.materials
import services.hardware
import services.parts

sys.dont_write_bytecode = True # no pycache now

app = Flask(__name__)
CORS(app)
#socketio = SocketIO(app, async_mode='threading') # should be somthing like gunicorn, gevent or else...


print("ProtoWorks server v0.1")

cfg = {}
try: cfg = Config('config.ini')
except InvalidConfig as e:
    print(e)
    sys.exit()

print("[db] initializing")
try: db = Database()
except DatabaseInitFailed as e:
    print(e)
    sys.exit()

# registering users
print("[main] checking userlist")
utils.check_userlist()

print(f"[main] running flask server")
print("")


@app.route('/api/valid_token', methods=['POST'])
def valid_token():
    if not db.users.valid_bearer(request.headers.get("Authorization")): 
        return 'Token is not valid', 403
    return "Token is valid", 200

@app.route('/api/login', methods = ['POST'])
def login():
    return services.auth.login(request)

@app.route('/api/projects/get_projects', methods = ['POST'])
def get_projects():
    return services.projects.get_projects(request)

@app.route('/api/projects/create', methods = ['POST'])
def create_project():
    return services.projects.create_project(request)

@app.route('/api/projects/delete', methods = ['POST'])
def delete_project():
    return services.projects.delete_project(request)

@app.route('/api/projects/pass', methods = ['POST'])
def pass_project():
    return services.projects.pass_project(request)

@app.route('/api/projects/get_project_info', methods = ['POST'])
def get_project_info():
    return services.projects.get_project_info(request)

@app.route('/api/files/create_dirs', methods=['POST'])
def create_dirs():
    return services.files.create_dirs(request)

@app.route('/api/files/upload_data_zip', methods=['POST'])
def upload_big():
    return services.files.upload_data_zip(request)

@app.route('/api/files/delete_path', methods = ['POST'])
def delete_path():
    return services.files.delete_path(request)

@app.route('/api/files/delete_files_of_project', methods= ['POST'])
def delete_files():
    return services.files.delete_files(request)

@app.route('/api/files/mkdir', methods = ['POST'])
def mkdir():
    return services.files.mkdir(request)

@app.route('/api/files/dir_tree', methods = ['POST'])
def dir_tree():
    return services.files.dir_tree(request)

@app.route('/api/files/files_list', methods = ['POST'])
def files_list():
    return services.files.files_list(request)

@app.route('/api/files/files_list_for_project', methods = ['POST'])
def files_list_for_project():
    return services.files.files_list_for_project(request)

@app.route('/api/files/get_zipped_path', methods = ['POST'])
def get_zipped_path():
    return services.files.get_zipped_path(request)

@app.route('/api/files/get_zipped_files', methods = ['POST'])
def get_zipped_files():
    return services.files.get_zipped_files(request)

@app.route('/api/audit/get_projects_sync_data', methods = ['POST'])
def get_projects_sync_data():
    return services.audit.get_projects_sync_data(request)

@app.route('/api/files/delete_logs', methods = ['POST'])
def delete_project_file_logs():
    return services.files.delete_logs(request)

@app.route('/api/files/get_all_files_that_ever_created_in_project', methods=['POST'])
def get_all_files_that_ever_created_in_project():
    return services.files.get_all_files_that_ever_created_in_project(request)

@app.route('/api/materials/add', methods=['POST'])
def add_materials():
    return services.materials.add_by_files(request)

@app.route('/api/materials/get', methods=['POST'])
def get_materials():
    return services.materials.get(request)

@app.route('/api/hardware/paper_print', methods=['POST'])
def paper_print():
    return services.hardware.paper_print(request)

@app.route('/api/audit/get_project_audit', methods=['POST'])
def get_project_audit():
    return services.audit.get_project_audit(request)

@app.route('/api/hardware/paper_print_from_upload', methods=['POST'])
def paper_print_from_upload():
    return services.hardware.paper_print_from_upload(request)

@app.route('/api/hardware/paper_print_text', methods=['POST'])
def paper_print_text():
    return services.hardware.paper_print_text(request)

@app.route('/api/hardware/paper_print_get_jobs', methods=['POST'])
def paper_print_get_jobs():
    return services.hardware.paper_print_get_jobs(request)

@app.route('/api/hardware/cancel_paper_printing', methods=['POST'])
def cancel_paper_printing():
    return services.hardware.cancel_paper_printing(request)

@app.route('/api/parts/get_parts', methods=['POST'])
def get_parts():
    return services.parts.get_parts(request)

@app.route('/api/parts/register_parts', methods=['POST'])
def register_parts():
    return services.parts.register_parts(request)

app.run(threaded=True, debug=False, host="0.0.0.0")
CORS(app)
#socketio.run(app)