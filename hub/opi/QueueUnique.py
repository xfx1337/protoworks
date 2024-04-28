from copy import deepcopy

import uuid

class QueueUnique:
    def __init__(self):
        self.queue = {}
    
    def add(self, obj):
        id = uuid.uuid4()
        self.queue[id] = obj
        return id
    
    def read(self):
        keys = list(self.queue.keys())
        if len(keys) == 0:
            return None

        obj = deepcopy(self.queue[keys[0]])
        del self.queue[keys[0]]
        return {"obj": obj}