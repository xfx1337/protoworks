import serial.tools.list_ports
import socket
from contextlib import closing

import ping3
from ping3 import ping
ping3.EXCEPTIONS = True


def list_serial():
    devices_get = list(serial.tools.list_ports.comports())
    devices = []
    for device in devices_get:
        devices.append(device.device)
    return devices

def get_main_page():
    return "CNCHell HUB VER0.1"

def get_ping(ip):
    p = -1
    host_s = ip.split("//")[-1]
    try:
        if len(ip.split(":")) > 1:
            port = ip.split(":")[-1]
            if "//" not in port:
                try:
                    available = check_socket(host_s.split(":")[0], int(port))
                except:
                    available = False
                if available:
                    p = ping(host_s.split(":")[0], unit="ms", timeout=3)
            else:
                p = ping(host_s.split(":")[0], unit="ms", timeout=3)
        else:
            p = ping(host_s.split(":")[0], unit="ms", timeout=3)
    except:
        pass
    
    if p == None:
        return -1
    return int(p)

def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            return True
        else:
            return False