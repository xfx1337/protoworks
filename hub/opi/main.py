import os, sys
import socket
import json

from flask import Flask, jsonify, request, Response
#from flask_socketio import SocketIO, emit, send, Namespace
#from flask_socketio import ConnectionRefusedError
from flask_cors import CORS

from exceptions import *
import utils

import services.machines

sys.dont_write_bytecode = True # no pycache now

app = Flask(__name__)
CORS(app)
#socketio = SocketIO(app, async_mode='threading') # should be somthing like gunicorn, gevent or else...

print("hub server v0.1")

@app.route('/api/machines/get_available_machines', methods=['POST'])
def get_available_machines():
    return services.machines.get_available_machines(request)

@app.route('/api/machines/connect', methods=['POST'])
def connect():
    return services.machines.connect(request)

@app.route('/api/machines/state', methods=['POST'])
def get_machine_state():
    return services.machines.get_state(request)

@app.route('/api/machine/disconnect', methods=['POST'])
def disconnect():
    return sevices.machines.disconnect(request)

@app.route('/api/machines/read', methods=['POST'])
def read():
    return services.machines.read(request)

@app.route('/api/machines/send_line', methods=['POST'])
def send_line():
    return services.machines.send_line(request)

@app.route('/api/machines/send_lines', methods=['POST'])
def send_lines():
    return services.machines.send_lines(request)

app.run(threaded=True, debug=False, host="0.0.0.0")
CORS(app)
#socketio.run(app)