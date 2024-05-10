from PySide6.QtCore import Signal, QObject

class TaskSignals(QObject):
    task_status_changed = Signal()