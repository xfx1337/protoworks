from datetime import datetime as dt
import time
import uuid

def seconds_to_str(seconds: int) -> str:
    mm, ss = divmod(seconds, 60)
    hh, mm = divmod(mm, 60)
    return "%02d час, %02d мин, %02d сек" % (hh, mm, ss)

def time_by_unix(t, date_only=False):
    if not date_only:
        return dt.fromtimestamp(t).strftime("%d/%m/%Y, %H:%M:%S")
    else:
        return dt.fromtimestamp(t).strftime("%d/%m/%Y")

def get_unique_id():
    return str(uuid.uuid1())