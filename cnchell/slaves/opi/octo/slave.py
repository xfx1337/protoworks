import os, sys
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
import socket
import json
import serial
import serial.tools.list_ports

import subprocess
import requests
from requests_toolbelt import MultipartEncoder
import re
import threading
import time
thread_event = threading.Event()

from flask import Flask, jsonify, request, Response
#from flask_socketio import SocketIO, emit, send, Namespace
#from flask_socketio import ConnectionRefusedError
from flask_cors import CORS

sys.dont_write_bytecode = True # no pycache now

app = Flask(__name__)
CORS(app)
#socketio = SocketIO(app, async_mode='threading') # should be somthing like gunicorn, gevent or else...

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    host = s.getsockname()[0]
    s.close()
    return host


def replace_all(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    #Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)

def list_serial():
    devices_get = list(serial.tools.list_ports.comports())
    devices = []
    for device in devices_get:
        devices.append(device.device)
    return devices


def get_available_machines(request):
    machines = list_serial()
    return json.dumps({"machines": machines}), 200

def get_unique_machine_data(port):
    def clear_string(s): # fuck it
        return s.rstrip().replace("\n", "").replace("\r", "").replace("\\n", "").replace("\'b", "").replace("\\'", "").replace("\'", "").replace('"', "")

    process = subprocess.Popen(f"udevadm info -q all -n {port} --attribute-walk", shell=True, stdout=subprocess.PIPE)
    out = ""
    for line in process.stdout:
        out += str(line)
    process.wait()

    found = re.findall("ATTRS\{idProduct\}==(.*?)ATTRS", out)

    groups = []

    for i in range(len(found)):
        groups.append({})
        groups[i]["idProduct"] = clear_string(found[i])

    found = re.findall("ATTRS\{idVendor\}==(.*?)ATTRS", out)
    for i in range(len(found)):
        groups[i]["idVendor"] = clear_string(found[i])

    # found = re.findall("ATTRS\{devpath\}==(.*?)ATTRS", out)
    # for i in range(len(found)):
    #     groups[i]["devpath"] = clear_string(found[i])

    return groups

def get_port_by_unique_info(unique_info):
    ports = list_serial()
    port = None
    for p in ports:
        ui = get_unique_machine_data(p)
        if ui == unique_info["data"]:
            port = p
            break

    return port

def kill_octo(idx):
    os.system(f"screen -S {idx} -X quit")
    os.system(f"rm -rf /home/octoprint/.octoprint{idx}")
    print("octo killed")

def write_octo(idx):
    os.system("chmod -R 777 /home/octoprint")
    os.system(f"runuser -l octoprint -c 'cp -R /home/octoprint/.octoprint /home/octoprint/.octoprint{idx}'")
    replace_all(f"/home/octoprint/.octoprint{idx}/users.yaml", "apikey: null", "apikey: Flvbybcnhfnjh")
    os.system(f"chmod -R 777 /home/octoprint/.octoprint{idx}")
    print("octo written")

def run_octo(idx, port):
    os.system(f"runuser -l octoprint -c 'screen -dmS {idx} /home/octoprint/OctoPrint/venv/bin/octoprint serve --port={5001+int(idx)} --config /home/octoprint/.octoprint{idx}/config.yaml --basedir /home/octoprint/.octoprint{idx}/'")
    print("octo started up")

def octo_command(idx, link, data, ret_text=False, method="POST"):
    headers = {"Authorization": "Bearer Flvbybcnhfnjh"}
    if method == "POST":
        r = requests.post(f"http://127.0.0.1:{5001+int(idx)}{link}", json = data, headers=headers)
    else:
        r = requests.get(f"http://127.0.0.1:{5001+int(idx)}{link}", json = data, headers=headers)
    if ret_text:
        return r.text
    return r.json()

def get_running_port(idx):
    script_name = f"{idx}.txt"
    port = None
    if os.path.exists(f"octo_instances/{script_name}"):
        with open(f"octo_instances/{script_name}", "r") as f:
            port = f.readline()
    return port

def restart_handler_back(unique_info, idx):
    port = get_port_by_unique_info(unique_info)
    if port == None:
        return "machine not connected", 300

    if not os.path.isdir("octo_instances"):
        os.mkdir("octo_instances")
    
    script_name = f"{idx}.txt"
    if os.path.exists(f"octo_instances/{script_name}"):
        try:
            kill_octo(idx)
        except:
            pass
    try:
        os.remove(f"octo_instances/{script_name}")
    except:
        pass
    with open(f"octo_instances/{script_name}", "w") as f:
        f.write(port)

    write_octo(idx)
    run_octo(idx, port)

def reconnect_handler_back(idx, baudrate):
    script_name = f"{idx}.txt"
    port = None
    if os.path.exists(f"octo_instances/{script_name}"):
        with open(f"octo_instances/{script_name}", "r") as f:
            port = f.readline()
    if port == None:
        return "couldn't connect", 500
    
    tx = octo_command(idx, "/api/connection", {"command": "connect", "port": port, "baudrate": int(baudrate), "printerProfile": "_default", "save": True, "autoconnect": True}, ret_text=True)


print("opi octo slave server v0.1")


@app.route("/", methods=['GET'])
def main_page():
    return "CNCHell OCTO SLAVE VER0.1", 200

@app.route('/api/restart', methods=['GET'])
def restart_req():
    print("[system] rebooting.")
    os.system("reboot")
    return "rebooting.", 200

@app.route('/api/machines/get_available_machines', methods=['GET'])
def get_available_machines_req():
    return get_available_machines(request)

@app.route('/api/machines/get_unique_info', methods=['POST'])
def get_unique_info_req():
    data = request.get_json()
    port = data["port"]
    return json.dumps({"data": get_unique_machine_data(port)}), 200

@app.route('/api/machines/get_available_machines_info', methods=['GET'])
def get_device_info_req():
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb").decode()
    devices = []
    for i in df.split('\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                devices.append(dinfo)
    return json.dumps({"data": devices}), 200

@app.route('/api/machines/restart_handler', methods=['POST'])
def restart_handler():
    data = request.get_json()
    unique_info = data["unique_info"]
    idx = data["id"]

    restart_handler_back(unique_info, idx)

    return "done", 200

@app.route('/api/machines/reconnect', methods=['POST'])
def machine_reconnect():
    if not os.path.isdir("octo_instances"):
        return "no instances running", 300
    
    data = request.get_json()
    idx = data["id"]
    baudrate = data["baudrate"]

    reconnect_handler_back(idx, baudrate)
    
    return "done", 200

@app.route('/api/machines/send_gcode', methods=['POST'])
def send():
    if not os.path.isdir("octo_instances"):
        return "no instances running", 300
    
    data = request.get_json()
    unique_info = data["unique_info"]
    idx = data["id"]
    command = data["command"]

    if not get_running_port(idx):
        return "not running", 300

    if type(command) == list:
        for c in command:
            tx = octo_command(idx, "/api/printer/command", {"command": c}, ret_text=True)
    tx = octo_command(idx, "/api/printer/command", {"command": command}, ret_text=True)

    return "done", 200

@app.route('/api/machines/check_online', methods=['POST'])
def check_online():
    if not os.path.isdir("octo_instances"):
        return json.dumps({"status": "offline"}), 200
    
    data = request.get_json()
    idx = data["id"]
    if not get_running_port(idx):
        return json.dumps({"status": "offline"}), 200

    return json.dumps({"status": "online"}), 200

@app.route('/api/machines/check_work_status', methods=['POST'])
def check_work_status():
    if not os.path.isdir("octo_instances"):
        return json.dumps({"status": "offline"}), 200
    
    data = request.get_json()
    idx = data["id"]

    ret = octo_command(idx, "/api/connection", {}, method='GET')
    return json.dumps({"status": ret["current"]["state"]}), 200

@app.route('/api/machines/check_envinronment', methods=['POST'])
def check_envinronment():
    if not os.path.isdir("octo_instances"):
        return json.dumps({"status": "offline"}), 200
    
    data = request.get_json()
    idx = data["id"]
    ret = octo_command(idx, "/api/printer", {}, method='GET')
    return json.dumps({"envinronment": ret}), 200

@app.route('/api/machines/cancel_job', methods=['POST'])
def cancel_job():
    if not os.path.isdir("octo_instances"):
        return "no instances running", 300
    
    data = request.get_json()
    unique_info = data["unique_info"]
    idx = data["id"]
    if not get_running_port(idx):
        return "not running", 300

    ret = octo_command(idx, "/api/job", {"command": "cancel"},)
    return ret, 200

@app.route('/api/machines/upload_gcode', methods=['POST'])
def upload_gcode():
    if not os.path.isdir("octo_instances"):
        return "no instances running", 300
    
    data = request.files['json']
    obj = json.loads(data.read())

    filename = obj["filename"]

    try:
        os.mkdir("temp")
    except: pass
    path = os.path.join("temp", filename)

    f = request.files['file']
    f.save(path)

    unique_info = obj["unique_info"]
    idx = obj["id"]
    if not get_running_port(idx):
        return "not running", 300
    
    encoder = MultipartEncoder(fields={'file': (filename, open(path, "rb"), 'application/octet-stream')}
    )
    
    r = requests.post(
        f"http://127.0.0.1:{5001+int(idx)}" + "/api/files/local", data=encoder, headers={'Content-Type': encoder.content_type, "Authorization": "Bearer Flvbybcnhfnjh"},
    )

    try:
        os.remove(path)
    except: pass

    return r.text, 200

@app.route('/api/machines/start_job', methods=['POST'])
def start_job():
    if not os.path.isdir("octo_instances"):
        return "no instances running", 300
    
    data = request.get_json()
    unique_info = data["unique_info"]
    idx = data["id"]
    file = data["file"]
    if not get_running_port(idx):
        return "not running", 300

    ret = octo_command(idx, f"/api/files/local/{file}", {"command": "select", "print": True})
    return ret, 200

def connect_all(machines):
    while thread_event.is_set():
        for m in machines:
            while True:
                try:
                    ret = octo_command(m["id"], "/api/server", {}, method='GET')
                    break
                except: pass
                time.sleep(2)
            try:
                reconnect_handler_back(m["id"], m["baudrate"])
            except:
                pass
        break

@app.route('/api/machines/setup_all', methods=['POST'])
def setup_all():
    data = request.get_json()
    machines = data["machines"]

    for m in machines:
        restart_handler_back(m["unique_info"], m["id"])

    thread_event.set()

    t = threading.Thread(target=connect_all, args=(machines, ))
    t.start()

    return "sent", 200

@app.route('/api/machines/get_host', methods=['POST'])
def get_host():
    data = request.get_json()
    idx = data["machine_id"]
    if not os.path.isdir("octo_instances"):
        return "no instances running", 300
    
    idx = data["id"]
    if not get_running_port(idx):
        return "not running", 300

    host = get_local_ip()
    host = "http://" + host + ":" + str(5001+int(idx)) + "/"
    return json.dumps({"host": host}), 200


app.run(threaded=True, debug=False, host="0.0.0.0", port=3719)
CORS(app)