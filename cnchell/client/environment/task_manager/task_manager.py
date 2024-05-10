from singleton import singleton

import utils

from PySide6.QtCore import QThreadPool

from environment.task_manager.Task import Task
from environment.task_manager.Process import Process
from environment.task_manager.Progress import Progress

from environment.task_manager.statuses import *

@singleton
class TaskManager(QThreadPool):
    def __init__(self, env):
        self.env = env
        super().__init__()
        self.tasks = {}

    def create_process(self, control_func, name, progress=None):
        process = Process(control_func, name, manager=self, progress=progress)
        self.tasks[process.id] = process 
        self.start(process)

        return process

    def run_system_task(self, fn, name):
        task = Task(fn, name, manager=self, system=True)
        self.tasks[task.id] = task
        self.start(task)
        self.env.main_signals.task_status_changed.emit()
        return task

    def run_silent_task(self, fn):
        task = Task(fn, "silent")
        self.start(task)

    def append_task(self, fn, name, progress=None):
        task = Task(fn, name, manager=self, progress=progress)
        self.tasks[task.id] = task 
        self.start(task)

        self.env.main_signals.task_status_changed.emit()
        
        return task

    def replace_task(self, task_id, fn):
        name = self.tasks[task_id].name
        progress = self.tasks[task_id].progress
        task = Task(fn, name, manager=self, progress = progress)
        self.tasks[task_id] = task
        self.start(task)

        self.env.main_signals.task_status_changed.emit()
        
        return task


    def get_tasks(self):
        return self.tasks
    
    def _task_status_changed(self, id):
        self.env.main_signals.task_status_changed.emit()