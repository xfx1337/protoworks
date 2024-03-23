from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox
from PySide6.QtCore import QTimer

from UI.widgets.QEasyScroll import QEasyScroll
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QAskForFilesDialog import QAskForFilesDialog
from UI.widgets.QAreUSureDialog import QAreUSureDialog
from UI.paper_print.PrintListEntry import PrintListEntry


from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()

from environment.environment import Environment
env = Environment()

class PaperPrintMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"Печать на бумажном принтере сервера")
        self.setWindowIcon(templates_manager.icons["proto"])
        self.setFixedSize(QSize(800, 300))


        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.hlayout = QHBoxLayout()
        self.print_btn = QInitButton("Печать", callback=self.print)
        self.print_text_btn = QInitButton("Печать текста", callback=self.print_text)
        self.cancel_all_btn = QInitButton("Отменить все", callback=self.cancel_all)
        self.update_btn = QInitButton("Обновить", callback=self.update_data)

        self.hlayout.addWidget(self.print_btn)
        self.hlayout.addWidget(self.print_text_btn)
        self.hlayout.addWidget(self.cancel_all_btn)
        self.hlayout.addWidget(self.update_btn)



        self.frame_layout = QVBoxLayout()
        self.table_names = QHBoxLayout()
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.frame.setLineWidth(1)
        self.frame.setLayout(self.frame_layout)
        
        self.first_line = QFrame()
        self.first_line.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.first_line.setLineWidth(1)
        self.first_line_layout = QHBoxLayout()
        self.first_line.setLayout(self.first_line_layout)
        self.doc_name = QLabel("Документ")
        self.status = QLabel("Состояние")
        self.pages = QLabel("Кол.во страниц")
        self.date = QLabel("Время")



        self.first_line_layout.addWidget(self.doc_name)
        self.first_line_layout.addWidget(self.status)
        self.first_line_layout.addWidget(self.pages)
        self.first_line_layout.addWidget(self.date)

        self.frame_layout.addWidget(self.first_line)

        self.scrollable = QEasyScroll()

        self.scrollWidgetLayout = self.scrollable.scrollWidgetLayout
        self.scrollWidget = self.scrollable.scrollWidget

        self.print_entries = []

        self.frame_layout.addWidget(self.scrollable)

        self.layout.addLayout(self.hlayout)
        self.layout.addWidget(self.frame)

        self.update_data()


    def update_data(self):
        jobs = env.net_manager.hardware.paper_print_get_jobs()
        for p in self.print_entries:
            if p.parent() != None:
                p.setParent(None)

        for i in range(len(jobs)):
            p = PrintListEntry(jobs[i])
            self.scrollWidgetLayout.insertWidget(i, p)
            self.scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)

            self.print_entries.append(p)


    def cancel_all(self):
        pass

    def print_text(self):
        self.dlg_ask_for_text = QAreUSureDialog("Введите текст на отправку")
        self.dlg_ask_for_text.exec()
        text = self.dlg_ask_for_text.input.text()
        env.net_manager.hardware.paper_print_text(text)

    def print(self):
        self.dlg_ask_for_file = QAskForFilesDialog("Выберите файл на печать", callback_yes=self.print_handler_file, only_one_file=True)
        self.dlg_ask_for_file.show()

    def print_handler_file(self, file):
        env.net_manager.hardware.paper_print_from_file(file)
        