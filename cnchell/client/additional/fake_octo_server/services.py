import requests

from Creds import Creds
creds = Creds()

def request(url, data={}):
    data["token"] = creds.token
    try: return requests.post("http://127.0.0.1:5000" + url, json = data)
    except: raise

def get_machine(idx):
    r = request("/api/machines/get_machine", {"id": idx})
    if r.status_code != 200:
        if r.status_code == 404:
            return
        raise
    
    return r.json()["machine"]