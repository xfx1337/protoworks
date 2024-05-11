import utils
import json
from database.database import Database
db = Database()

def update_monitoring(e):
    date = utils.time_now()
    device = str(e["device"])
    status = str(e["status"])
    try:
        info = e["info"]
    except:
        info = {}

    db.monitoring.update(date, device, status, json.dumps(info))

def get_monitoring_configuration():
    # TODO: changable
    conf = {
        "slaves": [],
        "machines": []
    }

    slaves = db.slaves.get_slaves_list(-1)
    for s in slaves:
        idx = s["id"]
        conf["slaves"].append({"ip": s["ip"], "id": idx})
    machines = db.machines.get_machines_list(-1)
    for m in machines:
        ip = db.slaves.get_slave(m["slave_id"])["ip"]
        idx = m["id"]
        conf["machines"].append({"ip": ip, "unique_info": m["unique_info"], "check_work_status": True, "check_envinronment": True, 
        "id": idx})
    
    return conf