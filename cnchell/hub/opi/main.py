import os, sys
import socket
import json

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from socketIO_client import SocketIO, LoggingNamespace

import threading
import time

from exceptions import *
import utils

import services.machines
from services.watchdog import Watchdog
watchdog = Watchdog()

sys.dont_write_bytecode = True # no pycache now

app = Flask(__name__)
CORS(app)

from SerialConnection import SerialConnection

print("hub server v0.1")

@app.route("/", methods=['GET'])
def main_page():
    return utils.get_main_page(), 200

@app.route("/api/restart", methods=['GET'])
def restart():
    print("[system] rebooting.")
    os.system("sleep 5; reboot -r now")
    return "rebooting.", 200

@app.route("/api/server_ip_update", methods=['POST'])
def server_ip_update():
    data = request.get_json()
    watchdog.server_ip = data["server"]
    return "changing", 200

@app.route("/api/set_monitoring_configuration", methods=['POST'])
def server_request():
    data = request.get_json()
    watchdog.set_monitoring_configuration(data["conf"])
    print(data["conf"])
    return "setting", 200

@app.route("/api/machines/setup_all", methods=['POST'])
def setup_all():
    data = request.get_json()["data"]
    services.machines.setup_all(data)
    return "sent", 200

def on_connect():
    watchdog.connected = True
    print("connected to server")

def on_disconnect():
    watchdog.connected = False

def on_reconnect():
    watchdog.connected = True
    print('reconnected to server')

def ret(*args):
    pass


def server_watchdog_thread():
    while True:
        watchdog.socketIO = None
        while not watchdog.connected:
            if watchdog.server_ip != None:
                try:
                    watchdog.socketIO = SocketIO(watchdog.server_ip, 5000, LoggingNamespace)
                    watchdog.socketIO.on('connect', on_connect)
                    watchdog.socketIO.on('disconnect', on_disconnect)
                    watchdog.socketIO.on('reconnect', on_reconnect)
                    watchdog.socketIO.on('ret', ret)
                    watchdog.connected = True
                    break
                except:
                    watchdog.connected = False
                    pass
            time.sleep(3)
        
        while watchdog.connected:
            try:
                event_gen = watchdog.get_events_slave()
                for data in event_gen:
                    watchdog.socketIO.emit("send_monitoring_update", json.dumps(data))
                event_gen = watchdog.get_events_machines()
                for data in event_gen:
                    watchdog.socketIO.emit("send_monitoring_update", json.dumps(data))
                watchdog.socketIO.wait(seconds=2)
            except Exception as e:
                print(e)
                #watchdog.connected = False

            time.sleep(3)
        
        time.sleep(3)

def arduino_watchdog_thread():
    while True:
        while not watchdog.arduino_hub_connected:
            ports = utils.list_serial()
            if len(ports) > 0:
                try:
                    watchdog.arduino_serial_connection = SerialConnection(ports[0])
                    watchdog.arduino_hub_connected = True
                except:
                    watchdog.arduino_hub_connected = False

            time.sleep(3)

        while watchdog.connected and watchdog.arduino_hub_connected:
            data = watchdog.arduino_serial_connection.read()
            events = data.split("\n")
            events_send = []
            for e in events:
                events_send.append(e.strip().replace("\r", ""))

            for e in events_send:
                watchdog.socketIO.emit("event", json.dumps({"event": e}))
            time.sleep(1)

        time.sleep(3)

server_watchdod = threading.Thread(target=server_watchdog_thread)
server_watchdod.start()

arduino_watchdog = threading.Thread(target=arduino_watchdog_thread)
arduino_watchdog.start()

app.run(debug=False, host="0.0.0.0", port=5001)
#CORS(app)