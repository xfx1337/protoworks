from PySide6.QtCore import Signal, QObject

class MainSignals(QObject):
    task_status_changed = Signal()
    message = Signal(tuple)
    open_calculations_jobs_finder_window = Signal(dict)