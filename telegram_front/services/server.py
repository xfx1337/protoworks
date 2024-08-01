from network_manager.network_manager import NetworkManager
net_manager = NetworkManager()

import utils
from defines import *

def get_status():
    status = net_manager.server.get_status()
    local_ip = status["local_ip"]
    local_ip_override = status["local_ip_override"]
    public_ip = status["public_ip"]
    uptime_str = utils.seconds_to_str(int(status["uptime"]))
    hub_status = status["hub_status"]
    cpu_load = status["cpu_load"]
    ram_total = status["ram_total"]
    ram_used = status["ram_used"]
    ram_free = ram_total - ram_used

    out = f"""
Локальный IP: {local_ip}
Локальный IP(перезапись): {local_ip_override}
Публичный IP: {public_ip}

Uptime: {uptime_str}

Хаб: {hub_status}

[CPU]
Загрузка: {cpu_load}%
[RAM]
Всего: {int(ram_total/1000/1000)} MB
Использовано: {int(ram_used/1000/1000)} MB
Свободно: {int(ram_free/1000/1000)} MB
    """
    return out

def get_lan_clients():
    clients = net_manager.server.get_lan_clients()

    out = f"""
Клиенты локальной сети:
    """

    for c in clients:
        out += f"\n{c}"

    return out

def get_users_list_str():
    users = net_manager.server.get_users_list()
    out = "Пользователи ProtoWorks:\n"
    for u in users:
        username = u["username"]
        privileges = u["privileges"]
        out += f"{username} - {privileges}\n"

    return out

def register_user(username, password):
    net_manager.server.register_user(username, password)

def remove_user(username):
    net_manager.server.remove_user(username)

def get_projects_str():
    projects = net_manager.server.get_projects()
    out = "Проекты:\n"
    for p in projects:
        id = p["id"]
        name = p["name"]
        status = p["status"]
        if status == PROJECT_DONE:
            status = "Сдан"
        if status == PROJECT_IN_WORK:
            status = "Работа"
        deadline = utils.time_by_unix(p["time_deadline"], date_only=True)
        out += f"[{id}] {name} - {status} - {deadline}\n"
    return out

def get_project_info_str(id):
    project = net_manager.server.get_project_info(id)
    p = project

    id = p["id"]
    name = p["name"]
    status = p["status"]
    if status == PROJECT_DONE:
        status = "Сдан"
    if status == PROJECT_IN_WORK:
        status = "Работа"
    desc = p["description"]
    customer = p["customer"]
    registered = utils.time_by_unix(p["time_registered"], date_only=True)
    deadline = utils.time_by_unix(p["time_deadline"], date_only=True)
        
    out = f"[{id}] {name} - {status}\n"
    out += f"Срок сдачи: {deadline}\n"
    out += f"Описание: {desc}\n"
    out += f"Заказчик: {customer}\n"
    out += f"Зарегистрирован: {registered}"
    return out

def make_project_done(id):
    net_manager.server.make_project_done(id)

def get_project_audit_str(id):
    audit = net_manager.server.get_project_audit(id)
    out = "Аудит(последние 10 событий):\n"
    for event in audit:
        event_n = event["event"]
        date = utils.time_by_unix(event["date"])
        out += f"{event_n} - {date}\n"
    return out

def restart_server():
    net_manager.server.restart()

def get_machines_str():
    machines = net_manager.server.get_machines_list()
    out = "Станки:\n"
    for m in machines:
        id = m["id"]
        name = m["name"]
        status = m["status"]
        work_status = m["work_status"]
        out += f"[{id}] {name} - {status} - {work_status}\n"

    return out

def send_action(action):
    net_manager.server.send_action(action)

def paper_print(file):
    net_manager.server.paper_print(file)

def send_voice(file, VOICE_PLAYBACK_SERVER):
    net_manager.server.send_voice(file, VOICE_PLAYBACK_SERVER)