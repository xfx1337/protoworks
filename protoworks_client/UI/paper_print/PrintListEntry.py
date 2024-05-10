from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox
from PySide6.QtCore import QTimer

from UI.widgets.QEasyScroll import QEasyScroll
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QAskForFilesDialog import QAskForFilesDialog
from UI.widgets.QAreUSureDialog import QAreUSureDialog

import utils

statuses = {
    512: "Ошибка. Блокировано",
    4096: "Печатный процесс закончен",
    256: "Задача удалена",
    4: "Удаляется",
    2: "Ошибка",
    0: "Неизвестно",
    32: "Принтер недоступен",
    64: "В принтере нет такой бумаги",
    1: "Задача приостановлена",
    128: "Напечатано",
    16: "Печатается",
    2048: "Перезапуск",
    8192: "Задача добавлена",
    8: "Буферизация",
    1024: "Принтер ожидает помощи"
}

from environment.environment import Environment
env = Environment()

class PrintListEntry(QWidget):
    def __init__(self, job):
        super().__init__()
        self.job = job

        self.context_menu = QMenu(self)
        cancel = self.context_menu.addAction("Отменить")
        cancel.triggered.connect(self.cancel)


        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.doc_label = QLabel(job["pDocument"])
        status = job["Status"]

        if status in statuses:
            status = statuses[status]
        else:
            status = "хуй знает"

        self.status = QLabel(status)
        self.pages = QLabel(str(job["TotalPages"]))
        self.date = QLabel(utils.time_by_unix(int(job["Submitted"])))

        self.layout.addWidget(self.doc_label)
        self.layout.addWidget(self.status)
        self.layout.addWidget(self.pages)
        self.layout.addWidget(self.date)

    def contextMenuEvent(self, event):
        self.context_menu.exec(event.globalPos())

    def cancel(self):
        env.task_manager.run_silent_task(lambda: env.net_manager.hardware.cancel_paper_printing(self.job["JobId"]))
        