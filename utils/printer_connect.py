import requests
import json
from tqdm import tqdm
import time
from functools import reduce
host = "http://192.168.8.46:5000"
port = "/dev/ttyUSB1"


def checksum(command):
    return reduce(lambda x, y: x ^ y, map(ord, command))

def convert(command, lineno):
    prefix = "N" + str(lineno) + " " + command
    command = prefix + "*" + str(checksum(prefix))
    return command

def convert2(command, linenumber):
    command_to_send = "N" + str(linenumber) + " " + command
    checksum = 0
    for c in bytearray(command_to_send.encode("ascii")):
        checksum ^= c
    command_to_send = command_to_send + "*" + str(checksum)
    return command_to_send

def send(line):
    r = requests.post(host + "/api/machines/send_line", json={"port": port, "line": line})
    if r.status_code != 200:
        print("send failed")

def send_lines(lines):
    r = requests.post(host + "/api/machines/send_lines", json={"port": port, "lines": lines})
    if r.status_code != 200:
        print("send failed")

def read(ret=False):
    r = requests.post(host + "/api/machines/read", json={"port": port})
    if r.status_code != 200:
        print("read failed")
    else:
        if ret:
            return r.json()["data"]
        print(r.json()["data"])

def start_exec_file(file):
    with open(file, "r") as f:
        send("M28 " + file)
        lines = f.readlines()
        lines_c = []
        k = 0
        for i in range(len(lines)):
            if len(lines[i]) > 0:
                if lines[i][0] == ";":
                    k+=1
                    continue
            else:
                k+=1
                continue

            if ";" in lines[i]:
                lines[i] = lines[i].split(";")[0]
            if lines[i] == "\n":
                k+=1
                continue
            lines_c.append(convert2(lines[i].replace("\n", ""), i-k+1))
        breakpoint()
        send_lines(lines_c)

        send("M29")

while True:
    inp = input(port + " >>> ")
    if inp == "read":
        read()
        continue
    if inp == "exit":
        exit()

    if inp.startswith("start"):
        if len(inp.split()) > 1:
            start_exec_file(inp.split()[-1])
        continue

    send(inp)
    read()