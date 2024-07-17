import sys
port = int(sys.argv[1])
machine_id = int(sys.argv[2])
config = sys.argv[3]
username = sys.argv[4]
password = sys.argv[5]

from config_manager import Config
config_manager = Config(config)

from Creds import Creds
creds = Creds()
creds.config_manager = config_manager
creds.username = username
creds.password = password
creds.auth()

import json
import requests
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from flask import request
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

import time
import os

import services

sys.dont_write_bytecode = True # no pycache now

app = Flask(__name__)
CORS(app)


@app.route("/", methods=['GET'])
def main_page():
    machine = services.get_machine(machine_id)

    idx = machine["id"]
    slave_id = machine["slave_id"]
    name = machine["name"]
    plate = machine["plate"]
    delta = machine["delta"]
    unique_info = machine["unique_info"]
    status = machine["status"]
    working_state = machine["work_status"]

    actual = "N/A"
    target = "N/A"
    actual_t = "N/A"
    target_t = "N/A"

    if "info" in machine:
        if "envinronment" in machine["info"] and machine["info"]["envinronment"] != "offline":
            try:
                tempertures = machine["info"]["envinronment"]["temperature"]
                actual = tempertures["bed"]["actual"]
                target = tempertures["bed"]["target"]
                actual_t = tempertures["tool0"]["actual"]
                target_t = tempertures["tool0"]["target"]
            except:
                pass

    txt = f"""
<meta http-equiv="refresh" content="3" /> 
ProtoWorks OctoPrint Fake Web Server <br>
id: {idx} <br>
slave_id: {slave_id} <br>
name: {name} <br>
plate: {plate} <br>
delta: {delta} <br>
status: {status} <br>
working state: {working_state} <br>
actual bed temp: {actual} <br>
target bed temp: {target} <br>
actual ext temp: {actual_t} <br>
target ext temp: {target_t} <br>
    """
    return txt, 200


@app.route("/api/shutdown_server", methods=['GET'])
def shutdown():
    shutdown_server()

@app.route("/api/status_server", methods=['GET'])
def status():
    return "running", 200

@app.route('/api/version', methods=['GET'])
def version():
    return {"api": "0.1",
     "server": "1.10.0",
      "text": "OctoPrint 1.10.0"}, 200

@app.route('/api/files/local', methods=['POST'])
def upload_gcode():
    filename = request.files['file'].filename
    path = os.path.join(config_manager["path"]["calculation_path"], (filename.split(".")[0] + f"_PWM{machine_id}" + "." + filename.split(".")[-1]))

    f = request.files['file']
    f.save(path)

    return "done", 200


app.run(debug=False, host="0.0.0.0", port=port)