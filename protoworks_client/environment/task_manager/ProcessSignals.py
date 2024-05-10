from PySide6.QtCore import Signal, QObject

class ProcessSignals(QObject):
    process_status_changed = Signal()