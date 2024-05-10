from PySide6.QtCore import Signal, QObject

class MainSignals(QObject):
    task_status_changed = Signal()