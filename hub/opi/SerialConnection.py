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
        self.ser = serial.Serial(self.port, baudrate)
        self.daemon = True
        self.start()

    def _send_line(self, line):
        if len(line) > 2:
            if line[-2:] != "\r\n":
                line += "\r\n"
        else:
            line += "\r\n"

        return self.ser.write(line.encode())

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
                time.sleep(1)
                cmd = self.write_queue.read()
                if cmd != None:
                    cmd = cmd["obj"]
                    if type(cmd) == list:
                        print(f"TRANSFER: {len(cmd)}")
                        i = 0
                        for c in cmd:
                            self._send_line(c)
                            if i % 100 == 0:
                                print(c)
                            i+=1
                            tries = 0
                            while not self.exit:
                                if self.ser.inWaiting() > 0:
                                    data_str = self.ser.read(self.ser.inWaiting()).decode('ascii')
                                    if "ok" in data_str:
                                        break
                                    elif "Resend" in data_str and tries < 5:
                                        self._send_line(c)
                                        tries += 1
                                        time.sleep(0.1)
                                    elif "Resend" not in data_str and tries < 5:
                                        time.sleep(0.01)
                                        tries+=1
                                    else:
                                        if tries > 5:
                                            self.read_queue.add("[hub] MACHINE HALT!!!")
                                        time.sleep(0.01)
                                else:
                                    time.sleep(0.01)
                                        
                                    self.read_queue.add(data_str)
                        print("all lines sent")
                    else:
                        self._send_line(cmd)
                
                if self.ser.inWaiting() > 0:
                    data_str = self.ser.read(self.ser.inWaiting()).decode('ascii') 
                    print(data_str)
                    self.read_queue.add(data_str)
            except:
                self.exit = True
                break