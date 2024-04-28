import os, shutil

from flask import Flask, Response, request
from flask import stream_with_context

import utils

import json

from environment.environment import Environment
env = Environment()

def get_available_machines(request):
    machines = utils.list_serial()
    return json.dumps({"machines": machines}), 200

def send_line(request):
    data = request.get_json()
    line = data["line"]
    port = data["port"]

    try: 
        env.machines.send_line(line, port)
        return "sent", 200
    except Exception as e:
        return str(e), 500

def connect(request):
    data = request.get_json()
    port = data["port"]
    env.machines.connect_machine(port)
    return "done", 200

def disconnect(request):
    data = request.get_json()
    port = data["port"]
    state = False
    try:
        state = env.machines.state(port)
    except:
        pass

    if state:
        env.machines.close(port)
        return "disconnected", 200
    else:
        return "already disconnected", 200

def get_state(request):
    data = request.get_json()
    port = data["port"]

    try:
        state = env.machines.state(port)
        return json.dumps({"state": state}), 200
    except Exception as e:
        return str(e), 500

def read(request):
    data = request.get_json()
    port = data["port"]

    try:
        data = env.machines.read(port)
        return json.dumps({"data": data}), 200
    except Exception as e:
        return str(e), 500

def send_line(request):
    data = request.get_json()
    port = data["port"]
    line = data["line"]

    try:
        env.machines.send_line(line, port)
        return "sent", 200
    except Exception as e:
        return str(e), 500

def send_lines(request):
    data = request.get_json()
    port = data["port"]
    lines = data["lines"]

    try:
        env.machines.send_line(lines, port)
        return "sent", 200
    except Exception as e:
        return str(e), 500