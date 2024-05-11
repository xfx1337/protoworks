from copy import deepcopy

import uuid

class QueueAutoDelete:
    def __init__(self, limit=10000):
        self.queue = []
        self.limit = limit
    
    def add(self, obj):
        self.queue.append(obj)
        if len(self.queue) > self.limit:
            i = len(self.limit) - self.limit
            del self.queue[0:i]
    
    def read(self):
        if len(self.queue) == 0:
            return None

        q = deepcopy(self.queue)
        self.queue = []
        return q
    
    def read_line(self):
        s = self.queue[0]
        del self.queue[0]
        return s
    
    def read_string(self):
        s = "\n".join(self.queue)
        self.queue = []
        return s