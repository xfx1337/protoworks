from singleton import singleton

from SerialConnection import SerialConnection

import exceptions
import defines

@singleton
class Machines:
    def __init__(self):
        self.connections = {}
    
    def connect_machine(self, port):
        try:
            conn = SerialConnection(port)
            self.connections[port] = conn 
        except:
            raise exceptions.MACHINE_CONNECTION_ERROR
    
    def send_line(self, line, port):
        try:
            self.connections[port].send(line)
        except:
            raise exceptions.MACHINE_CONNECTION_ERROR

    def read(self, port):
        try:
            return self.connections[port].read()
        except:
            raise exceptions.MACHINE_CONNECTION_ERROR
    
    def close(self, port):
        self.connections[port].close()
    
    def state(self, port):
        if self.connections[port].exit:
            return False
        return True