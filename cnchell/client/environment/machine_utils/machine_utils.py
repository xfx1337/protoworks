from singleton import singleton

import exceptions

import os

from defines import *

@singleton
class MachineUtils:
    def __init__(self, env=None):
        self.env = env

    def get_manager(self, man):
        if man == -1:
            return GCODE_MARLIN
        return man

    def get_dir(self, dirx):
        if dirx == "forward":
            return "Y"
        elif dirx == "back":
            return "Y-"
        elif dirx == "right":
            return "X"
        elif dirx == "left":
            return "X-"
        elif dirx == "up":
            return "Z"
        elif dirx == "dowm":
            return "Z-"
        elif dirx == "ext_forward":
            return "E"
        elif dirx == "ext_back":
            return "E-"
        else:
            return dirx

    def get_home(self, manager):
        if manager == GCODE_MARLIN:
            return "G28"

    def get_temp_commands(self, temps, manager):
        manager = self.get_manager(manager)
        commands = []
        if manager == GCODE_MARLIN:
            for k in temps.keys():
                if k == "ext0":
                    t = temps[k]
                    commands.append(f"M104 S{t}")
                if k == "bed":
                    t = temps[k]
                    commands.append(f"M140 S{t}")
        return commands

    def get_move_commands(self, dirx, dist, manager, feedrate=0):
        manager = self.get_manager(manager)
        dirx = self.get_dir(dirx)
        if dirx == "home":
            return self.get_home(manager)
        feedrate_s = f"F{feedrate}"
        if feedrate == 0:
            feedrate_s = ""
        if manager == GCODE_MARLIN:
            commands = ["G91"]
            out = f"G0 {dirx}{str(dist)} {feedrate_s}"
            commands.append(out)
            commands.append("G90")
        
        return commands

    def calculate_job_time_by_file(self, file):
        #TODO: make it for FDM
        return 0
    
    def calculate_job_time(self, job):
        return 0