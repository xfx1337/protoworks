from environment.task_manager.ProgressSignals import ProgressSignals

from PySide6.QtCore import QMutex


class Progress:
    def __init__(self):
        self.task = None
        self.progress = None
        self.full = 0
        self.current = 0
        self._cancel_task = False
        self.signals = ProgressSignals()
        self.signals.add.connect(self.add)
        self.mutex = QMutex()

    def add(self, i):
        self.mutex.lock()
        self.current += i
        self.mutex.unlock()
        self.signals.progress_changed.emit(self.get_percentage())
    
    def get_percentage(self):
        if self.full != 0:
            return 100 * float(self.current)/float(self.full)
        else:
            return 0
    
    def set_task(self, task):
        self.task = task
    
    def set_progress(self, progress):
        self.progress = progress