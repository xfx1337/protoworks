from PySide6.QtCore import Signal, QObject

class PartListViewChangeStatusSignal(QObject):
    update = Signal(dict)