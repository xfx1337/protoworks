import serial.tools.list_ports

def list_serial():
    devices_get = list(serial.tools.list_ports.comports())
    devices = []
    for device in devices_get:
        devices.append(device.device)
    return devices

def get_main_page():
    return "CNCHell HUB VER0.1"