import os, sys
import socket
import json
import requests

from flask import Flask, jsonify, request, Response
from flask_socketio import SocketIO, emit, send
from flask_socketio import ConnectionRefusedError
from flask_cors import CORS

import threading
import time
import datetime

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
import services.slaves
import services.machines
import services.monitoring
import services.work_queue
import services.bindings
import services.actions
import services.events
import services.configs

from common import *

from engineio.async_drivers import gevent

sys.dont_write_bytecode = True # no pycache now

app = Flask(__name__)
socketio = SocketIO(app)

print("ProtoWorks server v" + SERVER_VERSION)

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

def backup_watchdog():
    x = time.gmtime()
    ep = datetime.datetime(x.tm_year,x.tm_mon,x.tm_mday,0,0,0).timestamp()+cfg["backup"]["first"]
    if time.time() > ep:
        ep += cfg["backup"]["delay"]
    
    while True:
        time.sleep(5)
        if time.time() >= ep:
            ep += cfg["backup"]["delay"]
            utils.backup(cfg["path"]["projects_path"], cfg["backup"]["backup_path"])

if cfg["backup"]["enabled"]:
    print("[backup] running checking thread")
    backup_thread = threading.Thread(target=backup_watchdog)
    #backup_thread.start()

print(f"[main] running flask server")
print("")


db.monitoring.clear_db()
services.monitoring.update_monitoring({"device": "MAIN_HUB", "status": "offline"})

def main_hub_watchdog():
    print("[main] running main hub watch dog")
    while True:
        st = db.monitoring.get_device("MAIN_HUB")["status"]
        if st == "online":
            pass
        else:
            services.hardware.send_hub_command("/api/server_ip_update", {"server": utils.get_local_ip()})

        time.sleep(3)

mhd = threading.Thread(target=main_hub_watchdog)
mhd.start()

@app.route('/', methods=['GET'])
def main_page():
    return utils.get_main_page(), 200

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

@app.route('/api/files/get_server_path', methods = ['POST'])
def get_server_path():
    return services.files.get_server_path(request)

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

@app.route('/api/hardware/get_hub_info', methods=['POST'])
def get_hub_info():
    return services.hardware.get_hub_info(request)

@app.route('/api/hardware/set_hub_info', methods=['POST'])
def set_hub_info():
    return services.hardware.set_hub_info(request)

@app.route('/api/hardware/restart_hub', methods=['POST'])
def restart_hub():
    return services.hardware.restart_hub(request)

@app.route('/api/hardware/ping', methods=['POST'])
def check_ping():
    return services.hardware.check_ping(request)

@app.route('/api/hardware/send_get_request', methods=['POST'])
def send_get_request():
    return services.hardware.send_get_request(request)

@app.route('/api/parts/get_parts', methods=['POST'])
def get_parts():
    return services.parts.get_parts(request)

@app.route('/api/parts/register_parts', methods=['POST'])
def register_parts():
    return services.parts.register_parts(request)

@app.route('/api/parts/update_parts', methods=['POST'])
def update_parts():
    return services.parts.update_parts(request)

@app.route('/api/parts/delete_parts', methods=['POST'])
def delete_parts():
    return services.parts.delete_parts(request)

@app.route('/api/parts/indentify_parts', methods=['POST'])
def indentify_parts():
    return services.parts.indentify_parts(request)

@app.route('/api/parts/get_part_info', methods=['POST'])
def get_part_info():
    return services.parts.get_part_info(request)

@app.route('/api/slaves/add', methods=['POST'])
def add_slave():
    return services.slaves.add_slave(request)

@app.route('/api/slaves/list', methods=['POST'])
def get_slaves_list():
    return services.slaves.get_slaves_list(request)

@app.route('/api/slaves/edit', methods=['POST'])
def edit_slave():
    return services.slaves.edit(request)

@app.route('/api/slaves/restart', methods=['POST'])
def restart_slave():
    return services.slaves.restart(request)

@app.route('/api/slaves/send_request', methods=['POST'])
def send_slave_request():
    return services.slaves.send_request(request)

@app.route('/api/slaves/get', methods=['POST'])
def get_slave():
    return services.slaves.get_slave(request)
@app.route('/api/slaves/delete', methods=['POST'])
def delete_slave():
    return services.slaves.delete_slave(request)


@app.route('/api/machines/check_online', methods=['POST'])
def check_online():
    return services.machines.check_online(request)

@app.route('/api/machines/add', methods=['POST'])
def add_machine():
    return services.machines.add_machine(request)

@app.route('/api/machines/edit', methods=['POST'])
def edit_machine():
    return services.machines.edit_machine(request)

@app.route('/api/machines/list', methods=['POST'])
def list_machines():
    return services.machines.list_machines(request)

@app.route('/api/machines/get_machine', methods=['POST'])
def get_machine():
    return services.machines.get_machine(request)

@app.route('/api/machines/restart_handler', methods=['POST'])
def restart_handler():
    return services.machines.restart_handler(request)

@app.route('/api/machines/reconnect', methods=['POST'])
def reconnect():
    return services.machines.reconnect(request)

@app.route('/api/machines/send_request', methods=['POST'])
def send_command():
    return services.machines.send_request(request)

@app.route('/api/machines/send_gcode', methods=['POST'])
def send_gcode():
    return services.machines.send_gcode(request)

@app.route('/api/machines/cancel_job', methods=['POST'])
def cancel_job():
    return services.machines.cancel_job(request)

@app.route('/api/machines/upload_gcode', methods=['POST'])
def upload_gcode():
    return services.machines.upload_gcode(request)

@app.route('/api/machines/start_job', methods=['POST'])
def start_job():
    return services.machines.start_job(request)

@app.route('/api/hardware/restart_all', methods=['POST'])
def restart_all():
    services.hardware.hub_setup_all_machines()
    return "sent", 200

@app.route('/api/machines/get_host', methods=['POST'])
def get_host():
    return services.machines.get_host(request)

@app.route('/api/machines/delete', methods=['POST'])
def delete_machine():
    return services.machines.delete(request)

@app.route('/api/work_queue/add_jobs', methods=['POST'])
def add_job_to_order():
    return services.work_queue.add_jobs(request)

@app.route('/api/work_queue/get_jobs', methods=['POST'])
def get_order():
    return services.work_queue.get_jobs(request)

@app.route('/api/work_queue/delete_jobs', methods=['POST'])
def delete_from_order():
    return services.work_queue.delete_jobs(request)

@app.route('/api/work_queue/get_job_by_id', methods=['POST'])
def get_job_by_id():
    return services.work_queue.get_job_by_id(request)

@app.route('/api/work_queue/move_job', methods=['POST'])
def move_job():
    return services.work_queue.move_job(request)

@app.route('/api/work_queue/overwrite_job', methods=['POST'])
def overwrite_job():
    return services.work_queue.overwrite_job(request)

@app.route('/api/work_queue/overwrite_job_files', methods=['POST'])
def overwrite_job_files():
    return services.work_queue.overwrite_job_files(request)

@app.route('/api/work_queue/find_jobs_by_parts', methods=['POST'])
def find_jobs_by_parts():
    return services.work_queue.find_jobs_by_parts(request)

@app.route('/api/work_queue/find_jobs_by_files', methods=['POST'])
def find_jobs_by_files():
    return services.work_queue.find_jobs_by_files(request)

@app.route('/api/bindings/add', methods=['POST'])
def add_bind():
    return services.bindings.add(request)

@app.route('/api/bindings/remove', methods=['POST'])
def remove_bind():
    return services.bindings.remove(request)

@app.route('/api/bindings/get_event_by_action', methods=['POST'])
def get_event_by_action():
    return services.bindings.get_event_by_action(request)

@app.route("/api/actions/execute", methods=['POST'])
def execute_event():
    return services.actions.execute(request)


@app.route('/api/configs/get_sync', methods=['POST'])
def get_configs_sync():
    return services.configs.get_sync(request)

@app.route('/api/configs/upload_zip', methods=['POST'])
def upload_config_zip():
    return services.configs.upload_zip(request)

@app.route('/api/configs/get_zip', methods=['POST'])
def get_config_zip():
    return services.configs.get_zip(request)

@app.route('/api/configs/delete', methods=['POST'])
def delete_config():
    return services.configs.delete(request)


@socketio.on("send_monitoring_update")
def check_online(message):
    services.monitoring.update_monitoring(json.loads(message))
    emit('ret', {'data': 'got it.'})

@socketio.on("event")
def execute_action_io(message):
    services.events.event_io(json.loads(message))
    emit('ret', {'data': 'got it'})

@socketio.on('connect')
def connect():
    print("main hub connected")
    services.monitoring.update_monitoring({"device": "MAIN_HUB", "status": "online"})
    emit('ret', {'data': "connected"})
    conf = services.monitoring.get_monitoring_configuration()
    services.hardware.send_hub_command("/api/set_monitoring_configuration", {"conf": conf})

@socketio.on('disconnect')
def disconnect():
    print("main hub disconnected")
    services.monitoring.update_monitoring({"device": "MAIN_HUB", "status": "offline"})


socketio.run(app, debug=True, host="0.0.0.0")