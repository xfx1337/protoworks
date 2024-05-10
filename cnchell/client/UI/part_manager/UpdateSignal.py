from PySide6.QtCore import Signal, QObject

class UpdateSignal(QObject):
    update = Signal()