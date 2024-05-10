from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QWidget, QSplitter, QLabel, QMessageBox, QCalendarWidget, QCheckBox
from PySide6.QtCore import QTimer

from UI.widgets.QUserInput import QUserInput
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QDoubleLabel import QDoubleLabel

from UI.widgets.QEasyScroll import QEasyScroll

class QChooseManyCheckBoxes(QFrame):
    def __init__(self, text, elements, checking_callback=None, allow_only_one=False):
        super().__init__()
        
        self.elements = elements
        self.checking_callback = checking_callback
        self.allow_only_one = allow_only_one

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel(text)
        self.label.setFixedSize(self.label.sizeHint())
        self.layout.addWidget(self.label)

        self.scrollable = QEasyScroll()

        self.scrollWidgetLayout = self.scrollable.scrollWidgetLayout
        self.scrollWidget = self.scrollable.scrollWidget

        self.entries = []

        self.layout.addWidget(self.scrollable)

        self.selecting = False

        self.update_data()

    def update_data(self):
        for p in self.entries:
            if p.parent() != None:
                p.setParent(None)

        self.entries = []

        for i in range(len(self.elements)):
            e = self.elements[i]
            cb = QCheckBox(e)
            self.entries.append(cb)
            fn = (lambda i: lambda: self.checking_callback_here(i))(i)
            cb.toggled.connect(fn)

            self.scrollWidgetLayout.insertWidget(i, cb)
            self.scrollWidgetLayout.setAlignment(cb, Qt.AlignmentFlag.AlignTop)

    def checking_callback_here(self, number):
        if self.selecting:
            return
        if self.allow_only_one:
            self.selecting = True
            for i in range(len(self.elements)):
                if i != number:
                    self.entries[i].setChecked(False)
            self.selecting = False
        if self.checking_callback != None:
            self.checking_callback()
        

    def get_selected(self):
        selected = []
        for i in range(len(self.entries)):
            if self.entries[i].isChecked():
                selected.append(self.elements[i])
        
        return selected