from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QWidget, QSplitter, QLabel, QMessageBox, QSizePolicy, QCalendarWidget
from PySide6.QtCore import QTimer

from UI.stylesheets import *


from environment.environment import Environment
env = Environment()

from defines import *

from UI.widgets.QInitButton import QInitButton

class QProgramWidget(QFrame):
    def __init__(self, text, logo_name, btn_text, callback, pixmap_sizes=[], additional_buttons=[], additional_text=[]):
        super().__init__()

        self.callback = callback

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.main_layout = QVBoxLayout()

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(text)
        self.label.setStyleSheet(DISABLE_BORDER)

        self.drop = QLabel()
        self.drop.setStyleSheet(DISABLE_BORDER)
        try:
            pixmap = env.templates_manager.backgrounds[logo_name]
        except:
            pixmap = env.templates_manager.backgrounds["not_found"]
        if len(pixmap_sizes) > 0:
            pixmap = pixmap.scaled(pixmap_sizes[0], pixmap_sizes[1], Qt.KeepAspectRatio)
        self.drop.setPixmap(pixmap)
        #self.drop.setScaledContents(True)
        self.layout.addWidget(self.drop)
        self.layout.addWidget(self.label)
        self.layout.addStretch()

        self.layout.setAlignment(self.drop, Qt.AlignmentFlag.AlignLeft)
        self.layout.setAlignment(self.label, Qt.AlignmentFlag.AlignLeft)

        self.main_layout.addLayout(self.layout)
        
        self.h_layout = QHBoxLayout()
        self.v2_layout = QVBoxLayout()

        self.open_btn = QInitButton(btn_text, callback=callback)
        self.open_btn.setStyleSheet(DEFAULT_BORDER_STYLESHEET)
        self.v2_layout.addWidget(self.open_btn)

        self.buttons = []
        for btn in additional_buttons:
            btn_r = QInitButton(btn[0], callback=btn[1])
            btn_r.setStyleSheet(DEFAULT_BORDER_STYLESHEET)
            self.buttons.append(btn_r)
            self.v2_layout.addWidget(btn_r)

        self.labels = []
        for lbl in additional_text:
            lbl_r = QLabel(lbl)
            lbl_r.setStyleSheet(DISABLE_BORDER)
            self.labels.append(lbl_r)
            self.v2_layout.addWidget(lbl_r)

        self.h_layout.addLayout(self.v2_layout)
        self.h_layout.addStretch()

        self.main_layout.addLayout(self.h_layout)

        self.setLayout(self.main_layout)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        QTimer.singleShot(10, self.window_size_readjust)

    def window_size_readjust(self):
        self.adjustSize()
        self.resize(self.minimumSize())
        # self.setFixedHeight(self.height())
        # self.setFixedWidth(self.width())