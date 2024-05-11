import os, shutil

from flask import Flask, Response, request
from flask import stream_with_context

import utils

import json
import requests

def ui_fix(unique_info):
    breakpoint()
    return json.loads(unique_info.replace("'", '"'))

def send_request(ip, link, data={}, method='POST', ret_text=False):
    if method == "POST":
        try:
            r = requests.post(ip + link, 
            json=data)
        except:
            return -1
    else:
        try:
            r = requests.get(ip + link)
        except:
            return -1

    if not ret_text:
        return r.json()
    return r.text

def check_status(ip, idx):
    r = send_request(ip, "/api/machines/check_online", {"id": idx})
    if r != -1:
        return r["status"]

def check_work_status(ip, idx):
    r = send_request(ip, "/api/machines/check_work_status", {"id": idx})
    if r != -1:
        return r["status"]

def check_envinronment(ip, idx):
    r = send_request(ip, "/api/machines/check_envinronment", {"id": idx})
    if r != -1:
        return r["envinronment"]

def setup_all(data):
    for s in data:
        r = send_request(s["ip"], "/api/machines/setup_all", {"machines": s["machines"]}, ret_text=True)
