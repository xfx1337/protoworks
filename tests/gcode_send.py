import serial
import time

ser = serial.Serial('COM5', 115200)

time.sleep(2)
ser.write("G28\r\n".encode())
ser.write("M117 ProtoWorks test".encode())
time.sleep(1)
ser.close()
