import sys

from PySide6.QtWidgets import QApplication, QPushButton, QLabel, QLineEdit, QVBoxLayout, QFrame, QGridLayout, QCheckBox
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QUserInput import QUserInput


from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()


class MachineInteractiveMover(QFrame):
    def __init__(self, move_callback=None, move_available_callback=None, up_down_enabled=True, extruder_enabled=True):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.move_callback = move_callback
        self.move_available_callback = move_available_callback

        self.layout = QVBoxLayout()

        self.mover_layout = QGridLayout()
        
        self.allow_btn = QCheckBox("Разблокировать движение")
        self.allow_btn.stateChanged.connect(self.allow)

        self.forward = QInitButton("", callback=lambda: self.move("forward"))
        self.back = QInitButton("", callback=lambda: self.move("back"))
        self.left = QInitButton("", callback=lambda: self.move("left"))
        self.right = QInitButton("", callback=lambda: self.move("right"))
        self.home = QInitButton("", callback=lambda: self.move("home"))

        self.up = QInitButton("", callback=lambda: self.move("up"))
        self.down = QInitButton("", callback=lambda: self.move("down"))

        self.ext_forward = QInitButton("", callback=lambda: self.move("ext_forward"))
        self.ext_back = QInitButton("", callback=lambda: self.move("ext_back"))

        self.forward.setIcon(templates_manager.icons["up_arrow_full"])
        self.back.setIcon(templates_manager.icons["down_arrow_full"])
        self.left.setIcon(templates_manager.icons["left_arrow"])
        self.right.setIcon(templates_manager.icons["right_arrow"])

        self.up.setIcon(templates_manager.icons["up_arrow"])
        self.down.setIcon(templates_manager.icons["down_arrow"])

        self.home.setIcon(templates_manager.icons["home"])
        self.ext_forward.setIcon(templates_manager.icons["extrude_more"])
        self.ext_back.setIcon(templates_manager.icons["cross"])



        self.length = QUserInput("Расстояние мм: ")

        self.mover_layout.addWidget(self.forward, 0, 1, 1, 1)
        #self.mover_layout.addWidget(self.cancel, 1, 1, 1, 1)
        self.mover_layout.addWidget(self.back, 2, 1, 1, 1)
        self.mover_layout.addWidget(self.left, 1, 0, 1, 1)
        self.mover_layout.addWidget(self.right, 1, 2, 1, 1)
        self.mover_layout.addWidget(self.home, 1, 1, 1, 1)
        if up_down_enabled:
            self.mover_layout.addWidget(self.up, 0, 4, 1, 1)
            self.mover_layout.addWidget(self.down, 2, 4, 1, 1)
        if extruder_enabled:
            self.mover_layout.addWidget(self.ext_back, 3, 0, 1, 1)
            self.mover_layout.addWidget(self.ext_forward, 3, 2, 1, 1)
        


        self.layout.addWidget(self.allow_btn)
        self.layout.addLayout(self.mover_layout)
        self.layout.addWidget(self.length)
        
        self.setLayout(self.layout)
        self.allow()

    def allow(self):
        st = self.allow_btn.isChecked()
        if self.move_available_callback:
            stx = self.move_available_callback()
            if not stx:
                st = False
            self.forward.setEnabled(st)
            self.back.setEnabled(st)
            self.left.setEnabled(st)
            self.right.setEnabled(st)
            self.length.setEnabled(st)
            self.up.setEnabled(st)
            self.down.setEnabled(st)
            self.home.setEnabled(st)
            self.ext_back.setEnabled(st)
            self.ext_forward.setEnabled(st)

    def move(self, dirx):
        dist = self.length.get_input()
        if dist == "":
            dist = 1
        if self.move_callback:
            self.move_callback(dirx, dist)