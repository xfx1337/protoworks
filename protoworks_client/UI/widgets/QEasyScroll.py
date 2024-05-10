from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QAbstractScrollArea

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

# class QEasyScrollAbstract(QAbstractScrollArea):
#     def __init__(self):
#         super().__init__()
#         self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
#         self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
#         #self.setWidgetResizable(True)

#         self.scrollWidgetLayout = QVBoxLayout()
#         self.scrollWidgetLayout.setSpacing(0)
#         self.scrollWidget = QWidget()
#         self.scrollWidget.setLayout(self.scrollWidgetLayout)
#         self.setViewport(self.scrollWidget)
#         self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

#     def update_after_add(self):
#         self.setViewport(self.scrollWidget)
#         areaSize = self.viewport().size()
#         widgetSize = self.scrollWidget.size()
#         self.verticalScrollBar().setPageStep(areaSize.height())
#         self.verticalScrollBar().setRange(0, widgetSize.height() - areaSize.height())
#         self.verticalScrollBar.setSingleStep(20)

#         self.scrollWidgetLayout.addStretch()