from singleton import singleton

import exceptions

import os
import shutil


import threading
import time

import utils

from defines import *

#Calculations(OrcaSlicer...)
@singleton
class Calculations:
    def __init__(self, env):
        self.env = env

    def calculation_check_thread(self):
        while True:
            time.sleep(5)
            try:
                os.mkdir(os.path.join(self.env.config_manager["path"]["calculation_path"], "Checked"))
            except:
                pass
            path = self.env.config_manager["path"]["calculation_path"]
            filenames = next(os.walk(path), (None, None, []))[2]  # [] if no file
            jobs_to_search = []
            jobs_to_add = []
            for f in filenames:
                if f.split(".")[-1] in MACHINES_FILE_TYPES:
                    machine_id = self.env.machine_utils.get_machine_id_from_filename(f)
                    if f.count("PW") == 2:
                        part_id = self.env.machine_utils.get_part_id_from_filename(f)
                        part_name = f.split("_PW")[0]
                        jobs_to_search.append({"part_id": part_id, "part_name": part_name, "machine_id": machine_id, "filename_s": f.split("PW")[0], "filename": f})
                    else:
                        jobs_to_add.append({"machine_id": machine_id, "filename_s": f.split("_PW")[0] + ".stl", "filename": f})
                    
                    shutil.copy(os.path.join(path, f), os.path.join(path, "Checked", f))
                    os.remove(os.path.join(path, f))

            if len(jobs_to_search) != 0:
                jobs_equals = self.env.net_manager.work_queue.find_jobs_by_parts(jobs_to_search)
                if jobs_equals:
                    self.env.main_signals.open_calculations_jobs_finder_window.emit({"jobs_equals": jobs_equals})
                else:
                    jobs_equals = self.env.net_manager.work_queue.find_jobs_by_parts(jobs_to_search, ignore_machine_equal=True)
                    if jobs_equals:
                        self.env.main_signals.open_calculations_jobs_finder_window.emit({"jobs_equals": jobs_equals})
            

            if len(jobs_to_add) > 0:

                #trying to fix names
                for i in range(len(jobs_to_add)):
                    f = jobs_to_add[i]["filename_s"]
                    if "_PETG" in f:
                        jobs_to_add[i]["filename_s"] = f.split("_PETG")[0] + ".stl"
                    if "_PLA" in f:
                        jobs_to_add[i]["filename_s"] = f.split("_PLA")[0] + ".stl"
                    if "_ABS" in f:
                        jobs_to_add[i]["filename_s"] = f.split("_ABS")[0] + ".stl"

                jobs = self.env.net_manager.work_queue.find_jobs_by_files(jobs_to_add)
                if jobs:
                    self.env.main_signals.open_calculations_jobs_finder_window.emit({"jobs_equals": jobs})
                else:
                    jobs = self.env.net_manager.work_queue.find_jobs_by_files(jobs_to_add, ignore_machine_equal=True)
                    if jobs:
                        self.env.main_signals.open_calculations_jobs_finder_window.emit({"jobs_equals": jobs})