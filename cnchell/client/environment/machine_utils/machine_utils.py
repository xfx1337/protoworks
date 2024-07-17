from singleton import singleton

import exceptions

import os

from defines import *

import utils

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
        if file.split(".")[-1] in ["gcode", "gco"]:
            with open(file, "r", encoding="utf-8") as f:
                content = f.readlines()
            for l in content:
                if ";TIME:" in l:
                    return int(l.split(";TIME:")[-1])
                if "; estimated printing time (normal mode) = " in l:
                    t = l.split("; estimated printing time (normal mode) = ")[-1]
                    secs = 0
                    for s in t.split(" "):
                        secs += utils.get_seconds(s)
                    return secs

        return 0
    
    def calculate_job_time(self, job):
        return job["work_time"]*(job["unique_info"]["job_count_need"]-job["unique_info"]["job_count_done"])
        return 0

    def get_machine_id_from_filename(self, f):
        o = ""
        x = f.split("_PWM")[-1]
        for l in x:
            if l.isdigit():
                o += l
            else:
                break
        return int(o)

    def get_part_id_from_filename(self, f):
        o = ""
        x = f.split("_PW")[1]
        for l in x:
            if l.isdigit():
                o += l
            else:
                break
        return int(o)