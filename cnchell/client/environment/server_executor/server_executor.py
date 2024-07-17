from singleton import singleton

import exceptions

import os
import shutil
import subprocess


import threading
import time

import utils

from defines import *

from environment.server_executor.Server import Server, FakeOctoServer

@singleton
class ServerExecutor:
    def __init__(self, env):
        self.env = env
        self.servers = []

    def run_server(self, server):
        server.set_id(utils.get_unique_id())
        self.servers.append(server)
        server.run()
    
    def stop_server(self, id):
        for i in range(len(self.servers)):
            if self.servers[i].id == id:
                self.servers[i].stop()
                del servers[i]
                break

    def get_server_by_port(self, port):
        for i in range(len(self.servers)):
            try:
                if self.servers[i].port == port:
                    return self.servers[i]
                    break
            except:
                pass

    def setup_servers(self):
        # setting up fake octo servers
        while self.env.net_manager.token == "":
            time.sleep(3)
        
        machines = self.env.net_manager.machines.get_machines_list()["machines"]
        slaves = self.env.net_manager.slaves.get_slaves_list()
        slaves_dc = {}
        for s in slaves["slaves"]:
            slaves_dc[s["id"]] = s
        for m in machines:
            if m["slave_id"] in slaves_dc:
                if slaves_dc[m["slave_id"]]["type"] in [FDM_DIRECT, FDM_OCTO, FDM_KLIPPER]:
                    server = FakeOctoServer(FAKE_OCTO_FIRST_PORT+m["id"], self.env.net_manager.username, self.env.net_manager.password, m["id"], self.env.config_manager.get_abs_path())
                    self.run_server(server)

    def kill_all(self):
        for s in self.servers:
            s.stop()