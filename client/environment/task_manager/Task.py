from environment.task_manager.statuses import *

import time
import os, sys

from PySide6.QtCore import QRunnable

import utils

import exceptions

from environment.task_manager.TaskSignals import TaskSignals

class Task(QRunnable):
    def __init__(self, funcs, name, manager=None, progress=None):
        super(Task, self).__init__()

        self.manager = manager
        self.progress = progress

        if type(funcs) != list:
            self.funcs = [funcs]
        else:
            self.funcs = funcs
        self.name = name

        self.id = utils.get_unique_id()
        self.status = RUNNING
        self._error = None
        self._error_data = None

        self.time_started = time.time()
        self.time_stopped = None

        self._disable_task_end_on_func_end = False

        self.signals = TaskSignals()

    def run(self):
        try: 
            for fn in self.funcs:
                fn()
            if not self._disable_task_end_on_func_end:
                self.end_task()
        except exceptions.CANCELED:
            self.status = CANCELED
            self.end_task(CANCELED)

        except Exception as e:
            self.status = FAILED
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self._error = e
            self._error_data = {"exc_type": exc_type, "exc_obj": exc_obj, "exc_tb": exc_tb, "fname": fname}
            self.end_task(FAILED)
        

    def end_task(self, status=ENDED):
        self.status = status
        self.time_stopped = time.time()
        self.manager.env.main_signals.task_status_changed.emit()
        self.signals.task_status_changed.emit()

    def set_status(self, status=RUNNING):
        self.status = status
        self.signals.task_status_changed.emit()