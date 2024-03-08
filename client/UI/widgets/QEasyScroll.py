from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QScrollArea, QWidget

class QEasyScroll(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.scrollWidgetLayout = QVBoxLayout()
        self.scrollWidgetLayout.setSpacing(0)
        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollWidgetLayout)
        self.setWidget(self.scrollWidget)

        self.scrollWidgetLayout.addStretch()