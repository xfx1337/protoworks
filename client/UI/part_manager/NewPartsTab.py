from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox, QProgressBar
from PySide6.QtCore import QTimer
from PySide6.QtGui import QShortcut, QKeySequence

from PySide6.QtCore import Signal, QObject

import utils
from defines import *

import UI.stylesheets as stylesheets
from UI.widgets.QClickableLabel import QClickableLabel
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QListEntry import QListEntry
from UI.widgets.QDictShow import QDictShow
from UI.widgets.QPathInput import QPathInput
from UI.widgets.QChooseManyCheckBoxes import QChooseManyCheckBoxes
from UI.widgets.QFilesListSureDialog import QFilesListSureWidget
from UI.widgets.QEasyScroll import QEasyScroll

from UI.widgets.QTerminalScreenOutput import QTerminalScreenOutput


from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

from environment.task_manager.statuses import *

import time

from UI.part_manager.donut_joke import *


class HiddenDonut(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(QSize(600, 700))
        self.hidden_terminal = QTerminalScreenOutput()
        self.hidden_layout = QVBoxLayout()
        self.hidden_layout.addWidget(self.hidden_terminal)
        self.setLayout(self.hidden_layout)
        self.terminator = [False]

        self.setWindowTitle(f"[Процесс] Пасхалка в виде пончика")
        self.setWindowIcon(templates_manager.icons["proto"])

    def closeEvent(self, event):
        self.terminator[0] = True
        event.accept() # let the window close

    def donut_render(self):
        try: run(self.terminator, lambda send: self.hidden_terminal.signals.append.emit(send))
        except: pass

class NewPartsCreationProcessWindow(QWidget):
    def __init__(self, project, files, settings):
        super().__init__()

        self.shortcut_open = QShortcut(QKeySequence('Ctrl+R'), self)
        self.shortcut_open.activated.connect(self.show_donut)

        self.project = project
        self.files = files
        self.settings = settings

        self.setWindowTitle(f"[Процесс] Автоматическое создание деталей")
        self.setWindowIcon(templates_manager.icons["proto"])
        self.setFixedSize(QSize(700, 500))

        self.hLayout = QHBoxLayout()
        self.layout = QVBoxLayout()

        threads_count = int(env.config_manager["heavy_processing"]["task_threads"])

        self.label = QLabel("Обработчик деталей")

        self.left_frame = QFrame()
        self.left_frame_layout = QVBoxLayout()
        self.left_frame.setLayout(self.left_frame_layout)
        self.left_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.left_frame.setLineWidth(1)


        self.label_copy = QLabel("Копирование деталей")
        self.progress_bar_copy = QProgressBar(self)
        self.progress_bar_copy.setValue(0)

        self.left_frame_layout.addWidget(self.label_copy)
        self.left_frame_layout.addWidget(self.progress_bar_copy)

        label_name = "Конвертирование деталей"
        if not self.settings["auto_convert_all_formats"]:
            label_name = "[Отключено] Конвертирование деталей"

        self.label_convert = QLabel(label_name)
        self.progress_bar_convert = QProgressBar(self)
        self.progress_bar_convert.setValue(0)
        if not self.settings["auto_convert_all_formats"]:
            self.progress_bar_convert.setValue(100)

        self.left_frame_layout.addWidget(self.label_convert)
        self.left_frame_layout.addWidget(self.progress_bar_convert)

        label_name_threads = "Потоки"
        if not self.settings["auto_convert_all_formats"]:
            label_name_threads = "[Отключено] Потоки"

        self.threads_label = QLabel(label_name_threads)
        self.scrollable = QEasyScroll()
        self.scrollWidgetLayout = self.scrollable.scrollWidgetLayout
        self.scrollWidget = self.scrollable.scrollWidget
        self.workers_entries = []

        self.left_frame_layout.addWidget(self.threads_label)
        self.left_frame_layout.addWidget(self.scrollable)

        self.hLayout.addWidget(self.left_frame)


        self.right_frame = QFrame()
        self.right_frame_layout = QVBoxLayout()
        self.right_frame.setLayout(self.right_frame_layout)
        self.right_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.right_frame.setLineWidth(1)


        self.terminal_label = QLabel("Терминал")
        self.terminal_out = QTerminalScreenOutput()
        self.right_frame_layout.addWidget(self.terminal_label)
        self.right_frame_layout.addWidget(self.terminal_out)

        self.hLayout.addWidget(self.right_frame)

        self.layout.addWidget(self.label)
        self.layout.addLayout(self.hLayout)
        self.setLayout(self.layout)


        self.hidden = HiddenDonut()

        pro = Progress()
        self.process = env.task_manager.create_process(self.test, "Ебать колотить целый процесс", progress=pro)

    def test(self, process):
        pro = Progress()
        task = process.append_task(lambda: self.test2(pro), "градиент хпс", pro)
        process.progress.full = 1000
        while task.status == RUNNING:
            time.sleep(0.2)
            process.progress.add(1)

    def show_donut(self):
        self.hidden.show()
        env.task_manager.run_silent_task(self.hidden.donut_render)

    def test2(self, progress):
        r = 0
        g = 128
        b = 255
        r_d = 1
        g_d = -1
        b_d = 1
        strings = ["хуй", "пизда", "сковорода"]
        progress.full = 1000
        for i in range(1000):
            time.sleep(0.05)
            if r > 248:
                r_d = -1
            if r < 6:
                r_d = 1
            if b > 248:
                b_d = -1
            if b < 6:
                b_d = 1
            if g > 248:
                g_d = -1
            if g < 6:
                g_d = 1
            r += r_d*5
            g += g_d*5
            b += b_d*5
            color_rgb = f"rgb({str(r)}, {str(g)}, {str(b)})"
            string = strings[i % 3]
            progress.add(1)
            self.terminal_out.signals.append.emit({"string": string, "rgb_color": color_rgb})


class SettingsFrame(QFrame):
    def __init__(self):
        super().__init__()

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Доп настройки автоматического создания деталей")
        self.label.setFixedSize(self.label.sizeHint())
        self.layout.addWidget(self.label)

        self.auto_convert_btn = QCheckBox("Автоматически конвертировать файл детали во все форматы")
        
        self.layout.addWidget(self.auto_convert_btn)
    
    def get_settings(self):
        settings = {
            "auto_convert_all_formats": self.auto_convert_btn.isChecked()
        }
        return settings

class NewPartsTab(QFrame):
    def __init__(self, project):
        super().__init__()
        self.project = project

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()

        self.label = QLabel("Автоматическое создание новых деталей")
        self.label.setFixedSize(self.label.sizeHint())


        self.files = []

        self.folder_select = QPathInput("Директория исходных файлов", selected_callback = self.update_path)
        self.subfolders_enable_cb = QCheckBox("Проверять подпапки на наличие файлов")
        self.subfolders_enable_cb.setChecked(True)
        self.subfolders_enable_cb.toggled.connect(self.update_path)



        self.folder_select.setStyleSheet(stylesheets.DISABLE_BORDER)
        self.folder_choosing_frame = QFrame()
        self.folder_choosing_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.folder_choosing_frame.setLineWidth(1)
        self.folder_choosing_layout = QVBoxLayout()
        self.folder_choosing_frame.setLayout(self.folder_choosing_layout)
        self.folder_choosing_layout.addWidget(self.folder_select)
        self.folder_choosing_layout.addWidget(self.subfolders_enable_cb)


        
        extensions = []
        for ext in FILE_FORMATS.keys():
            extensions.append(FILE_FORMATS[ext])

        self.extensions = QChooseManyCheckBoxes("Форматы исходных файлов", extensions, checking_callback=self.update_data_files)

        self.files_show = QFilesListSureWidget([], [], "Выберите исходные файлы", "Исходные файлы", "Проигнорировать")


        self.settings_frame = SettingsFrame()
        self.run_btn = QInitButton("Выполнить", callback=self.run_creation)

        self.layout.addWidget(self.label, 10)
        self.layout.addWidget(self.folder_choosing_frame, 10)
        self.layout.addWidget(self.extensions, 20)
        self.layout.addWidget(self.files_show, 50)
        self.layout.addWidget(self.settings_frame, 20)
        self.layout.addWidget(self.run_btn)


        self.setLayout(self.layout)

    def run_creation(self):
        self.creation_wnd = NewPartsCreationProcessWindow(self.project, self.files_show.files_yes, self.settings_frame.get_settings())
        self.creation_wnd.show()
        self.parent().close()

    def update_path(self):
        if self.folder_select.path == None:
            return
        if self.subfolders_enable_cb.isChecked():
            self.files = env.file_manager.get_files_list(self.folder_select.path, files_only=True)
        else:
            self.files = env.file_manager.get_files_list(self.folder_select.path, files_only=True, subdirs=False)

        self.files = env.file_manager.files_list_to_dict_list(self.files)

        for f in self.files:
            f["visible"] = True

        self.update_data_files()

    def update_data_files(self):
        extensions = self.extensions.get_selected()
        for f in self.files:
            f["visible"] = True
            ext = f["path"].split(".")[-1]
            if len(extensions) != 0: 
                if ext not in extensions:
                    f["visible"] = False

        self.update_data()

    def update_data(self):
        main_path = self.folder_select.path
        self.files_show.path_dont_show = main_path

        visible_files = []
        for f in self.files:
            if f["visible"]:
                visible_files.append(f)
        self.files_show.files_yes = visible_files
        self.files_show.files_no = []
        self.files_show.load_data()
        self.files_show.update()