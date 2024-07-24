import serial

import threading

import time

from QueueUnique import QueueUnique
from QueueAutoDelete import QueueAutoDelete

class SerialConnection(threading.Thread):
    def __init__(self, port, baudrate=115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.exit = False
        self.write_queue = QueueUnique()
        self.read_queue = QueueAutoDelete()
        self.ser = serial.Serial(self.port, self.baudrate)

        data_str = self.ser.read(self.ser.inWaiting()).decode('ascii')
        time.sleep(0.5)
        self.ser.write("indent_hub\r\n".encode())
        time.sleep(1)
        data_str = self.ser.read(self.ser.inWaiting()).decode('ascii')
        if "hub indent" not in data_str:
            if "boot up" not in data_str:
                raise KeyError

        #self.ser.set_low_latency_mode(True)
        self.daemon = True
        self.send_next_after = "ok"
        self.start()

    def _send_line(self, line):
        if len(line) > 2:
            if line[-2:] != "\r\n":
                line += "\r\n"
        else:
            line += "\r\n"

        return self.ser.write(line.encode())

    def set_nextline_check(self, s):
        self.send_next_after = s

    def close(self):
        self.exit = True
        self.ser.close() 

    def send(self, line):
        self.write_queue.add(line)
    
    def read_line(self):
        return self.read_queue.read_line()
    
    def read(self):
        return self.read_queue.read_string()

    def run(self):
        while not self.exit:
            try:
                if(self.ser == None):
                    self.ser = serial.Serial(self.port, self.baudrate)
                    self.read_queue.add("RECONNECTING")
                time.sleep(0.1)
                cmd = self.write_queue.read()
                if cmd != None:
                    cmd = cmd["obj"]
                    if type(cmd) == list:
                        i = 0
                        for c in cmd:
                            cmd = self.write_queue.read()
                            if cmd != None:
                                cmd = cmd["obj"]
                                if cmd == "CANCEL_MULTILINE":
                                    break

                            self._send_line(c)
                            if self.send_next_after != "":
                                while not self.exit:
                                    try:
                                        if(self.ser == None):
                                            self.ser = serial.Serial(self.port, self.baudrate)
                                            self.read_queue.add("RECONNECTING")
                                        data_str = self.ser.read(self.ser.inWaiting()).decode('ascii')
                                        if data_str != "":
                                            self.read_queue.add(data_str)
                                        if "ok" in data_str:
                                            break
                                    except:
                                        print("serial error")
                                        if(not(self.ser == None)):
                                            self.ser.close()
                                            self.ser = None
                                            self.read_queue.add("DISCONNECTING")

                                        self.read_queue.add("NO CONNECTION")
                                        time.sleep(1)

                    else:
                        self._send_line(cmd)
                
                if self.ser.inWaiting() > 0:
                    data_str = self.ser.read(self.ser.inWaiting()).decode('ascii') 
                    self.read_queue.add(data_str)
            except:
                print("serial error")
                if(not(self.ser == None)):
                    self.ser.close()
                    self.ser = None
                    self.read_queue.add("DISCONNECTING")

                self.read_queue.add("NO CONNECTION")
                time.sleep(2)