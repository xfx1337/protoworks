from network_manager.network_manager import NetworkManager
net_manager = NetworkManager()

import utils
import db

def get_users_list_str():
    users = db.get_users_list()
    out = "Список пользователей\n"
    for u in users:
        user = u["username"]
        privileges = u["privileges"]
        out += f"{user} - {privileges}\n"
    return out