from environment.task_manager.statuses import *

import time
import os, sys
import traceback

from PySide6.QtCore import QRunnable

import utils

import exceptions

from environment.task_manager.ProcessSignals import ProcessSignals
from environment.task_manager.Task import Task
from environment.task_manager.Progress import Progress

class Process(QRunnable):
    def __init__(self, control_func, name, manager=None, progress=None):
        super(Process, self).__init__()

        self.manager = manager
        self.env = self.manager.env
        self.tasks = {}
        self.control_func = control_func
        self.progress = progress

        self.name = name

        self.id = utils.get_unique_id()
        self.status = RUNNING
        self._error = None
        self._error_data = None

        self.time_started = time.time()
        self.time_stopped = None

        self._disable_process_end_on_func_end = True

        self.signals = ProcessSignals()

    def run(self):
        try: 
            self.control_func(process=self)
            if not self._disable_process_end_on_func_end:
                self.end_process()
        except exceptions.CANCELED:
            self.status = CANCELED
            self.end_process(CANCELED)

        except Exception as e:
            self.status = FAILED
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

            self._error = e
            self._error_data = {"exc_type": exc_type, "exc_obj": exc_obj, "exc_tb": exc_tb, "fname": fname, "func_name": self.control_func}
            self.end_process(FAILED)
    
    def run_silent_task(self, fn):
        task = Task(fn, "silent")
        self.manager.start(task)

    def append_task(self, fn, name, progress=None):
        task = Task(fn, name, manager=self.manager, progress=progress, process_child=self)
        self.tasks[task.id] = task 
        self.manager.start(task)

        self.env.main_signals.task_status_changed.emit()
        
        return task

    def end_process(self, status=ENDED):
        self.status = status
        self.time_stopped = time.time()
        if self.manager != None:
            self.manager.env.main_signals.task_status_changed.emit()
        self.signals.process_status_changed.emit()

    def set_status(self, status=RUNNING):
        self.status = status
        self.signals.process_status_changed.emit()