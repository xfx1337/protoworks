import requests
import services.machines
import utils

class Watchdog:
    def __init__(self):
        self.devices = []
        self.server_ip = None
        self.connected = False
        self.conf = None

    def get_events_slave(self):
        if self.conf == None:
            return []

        for s in self.conf["slaves"]:
            e = {}

            ip = s["ip"]
            e["info"] = {}
            ping = utils.get_ping(ip)
            e["info"]["ping"] = ping
            if ping >= 0:
                e["status"] = "online"
            else:
                e["status"] = "offline"
            e["device"] = "SLAVE" + str(s["id"])
            yield e
        
    def get_events_machines(self):
        if self.conf == None:
            return []
        for m in self.conf["machines"]:
            try:
                e = {}
                e["info"] = {}
                ip = m["ip"]
                e["device"] = "MACHINE" + str(m["id"])
                e["status"] = services.machines.check_status(ip, m["id"])
                e["info"]["job"] = {}
                if m["check_work_status"]:
                    try:
                        e["info"]["work_status"] = services.machines.check_work_status(ip, m["id"])
                    except:
                        e["info"]["work_status"] = "N/A"
                if m["check_envinronment"]:
                    try:
                        e["info"]["envinronment"] = services.machines.check_envinronment(ip, m["id"])
                    except:
                        e["info"]["envinronment"] = "N/A"
                
                if m["check_job"]:
                    try:
                        e["info"]["job"] = services.machines.check_job(ip, m["id"])
                    except:
                        e["info"]["job"] = "N/A"

                if e["status"] == None:
                    e["status"] = "offline"
                if e["info"]["work_status"] == None:
                    e["info"]["work_status"] = "offline"
                if e["info"]["envinronment"] == None:
                    e["info"]["envinronment"] = "offline"
            except:
                pass

            yield e

    def register_request():
        breakpoint
    
    def set_monitoring_configuration(self, conf):
        self.conf = conf

