from PySide6.QtCore import Signal, QObject

class ProgressSignals(QObject):
    progress_changed = Signal(int)
    add = Signal(int)