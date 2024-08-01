from flask import Flask, jsonify, request, Response
from flask_socketio import SocketIO, emit, send
from flask_socketio import ConnectionRefusedError
from flask_cors import CORS

import sys


from engineio.async_drivers import gevent

sys.dont_write_bytecode = True # no pycache now

app = Flask(__name__)

import tempfile

import json
import os

from playsound import playsound

temp_path = tempfile.gettempdir()

@app.route('/api/play_sound', methods=['POST'])
def main_page():
    return play_sound_wrapper(request), 200


def play_sound_wrapper(request):
    data = request.files['json']
    obj = json.loads(data.read())

    path = os.path.join(temp_path, obj["filename"])

    f = request.files['file']
    f.save(path)

    playsound(path)

app.run(debug=True, host="0.0.0.0", port=2358)