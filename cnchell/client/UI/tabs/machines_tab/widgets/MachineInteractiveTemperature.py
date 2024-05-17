import sys

from PySide6.QtWidgets import QApplication, QPushButton, QLabel, QLineEdit, QVBoxLayout, QFrame, QGridLayout, QCheckBox, QHBoxLayout
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QUserInput import QUserInput


from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()


class MachineInteractiveTemperature(QFrame):
    def __init__(self, temperatures_dc, submit_callback, check_online=None):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.submit_callback = submit_callback
        self.check_online = check_online

        self.layout = QHBoxLayout()

        self.temperatures = {}

        for t in temperatures_dc:
            tu = QUserInput(t["name"])
            self.layout.addWidget(tu)
            self.temperatures[t["id"]] = tu

        self.submit = QInitButton("Изменить", callback=self.submit_callback)
        self.layout.addWidget(self.submit)

        self.setLayout(self.layout)
    
    def get_temps(self):
        temps = {}
        for k in self.temperatures.keys():
            inp = self.temperatures[k].get_input()
            if inp != "":
                temps[k] = inp
        return temps