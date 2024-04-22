from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox, QProgressBar
from PySide6.QtCore import QTimer
from PySide6.QtGui import QShortcut, QKeySequence

from PySide6.QtCore import Signal, QObject, QTimer

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

from UI.task_manager.TaskListEntry import TaskListEntry

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

from environment.task_manager.statuses import *

import os, time, shutil

from UI.part_manager.donut_joke import *

from environment.convert_manager.convert_ways import CONVERT_WAYS

from UI.part_manager.UpdateSignal import UpdateSignal

import pythoncom
import win32com
import threading

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
    def __init__(self, project, files, settings, update_only=False, parts=[]):
        super().__init__()

        self.update_only = update_only
        self.parts = parts

        self.shortcut_open = QShortcut(QKeySequence('Ctrl+R'), self)
        self.shortcut_open.activated.connect(self.show_donut)

        self.project = project
        self.files = files
        self.settings = settings

        self.setWindowTitle(f"[Процесс] Автоматическое создание деталей")
        if self.update_only:
            self.setWindowTitle(f"[Процесс] Автоматическое обновление деталей")

        self.setWindowIcon(templates_manager.icons["proto"])
        self.setFixedSize(QSize(1280, 720))

        self.hLayout = QHBoxLayout()
        self.layout = QVBoxLayout()

        threads_count = int(env.config_manager["heavy_processing"]["task_threads"])

        self.label = QLabel("Обработчик деталей")

        self.left_frame = QFrame()
        self.left_frame_layout = QVBoxLayout()
        self.left_frame.setLayout(self.left_frame_layout)
        self.left_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.left_frame.setLineWidth(1)

        self.label_overall = QLabel("Общий процесс")
        self.progress_bar_overall = QProgressBar(self)
        self.progress_bar_overall.setValue(0)

        self.left_frame_layout.addWidget(self.label_overall)
        self.left_frame_layout.addWidget(self.progress_bar_overall)


        self.label_copy = QLabel("Копирование деталей")
        self.progress_bar_copy = QProgressBar(self)
        self.progress_bar_copy.setValue(0)

        self.left_frame_layout.addWidget(self.label_copy)
        self.left_frame_layout.addWidget(self.progress_bar_copy)

        # label_name = "Конвертирование деталей"
        # if not self.settings["auto_convert_all_formats"]:
        #     label_name = "[Отключено] Конвертирование деталей"

        # self.label_convert = QLabel(label_name)
        # self.progress_bar_convert = QProgressBar(self)
        # self.progress_bar_convert.setValue(0)
        # if not self.settings["auto_convert_all_formats"]:
        #     self.progress_bar_convert.setValue(100)

        #self.left_frame_layout.addWidget(self.label_convert)
        #self.left_frame_layout.addWidget(self.progress_bar_convert)

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

        self.hLayout.addWidget(self.left_frame, 40)


        self.right_frame = QFrame()
        self.right_frame_layout = QVBoxLayout()
        self.right_frame.setLayout(self.right_frame_layout)
        self.right_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.right_frame.setLineWidth(1)


        self.terminal_label = QLabel("Терминал")
        self.terminal_out = QTerminalScreenOutput()
        self.right_frame_layout.addWidget(self.terminal_label)
        self.right_frame_layout.addWidget(self.terminal_out)

        self.hLayout.addWidget(self.right_frame, 60)

        self.exit_btn = QInitButton("Закрыть(без остановки процесса)", callback=lambda: self.hide())

        self.layout.addWidget(self.label)
        self.layout.addLayout(self.hLayout)
        self.layout.addWidget(self.exit_btn)
        self.setLayout(self.layout)

        self.workers = []
        self.workers_entries = []

        self.hidden = HiddenDonut()

        self.signals = UpdateSignal()
        self.signals.update.connect(self.update_workers_show)

        pro = Progress()
        name = self.project["name"]
        task_name = f"[{name}] Создание новых деталей"
        if self.update_only:
            task_name = f"[{name}] Обновление деталей"
        self.process = env.task_manager.create_process(self.new_parts_control_worker, task_name, progress=pro)

        #self.process.run_silent_task(lambda: auto_check_overall_progress(exit=exit_dc))

        #self.process.signals.process_status_changed.connect(self.update_workers_show)
        #self.update_workers_show()

    def print_terminal(self, string, rgb_color="rgb(74,246,38)", color=None):
        if color != None:
            self.terminal_out.signals.append.emit({"string": string, "color": color})
        else:
            self.terminal_out.signals.append.emit({"string": string, "rgb_color": rgb_color})

    def callback_server_after_process_end(self, ids):
        if self.update_only:
            return
        while self.process.progress.get_percentage() != 100:
            time.sleep(1)

        if self.process.status == FAILED:
            return

        pro = Progress()
        fn = lambda: env.part_manager.send_parts(self.project, ids, progress=pro)
        task = self.process.append_task(fn, "Синхронизация деталей", pro)
        self.workers.append(task)
        self.signals.update.emit()

        while task.status != ENDED:
            time.sleep(1)
        self.process.set_status(ENDED)

    def new_parts_control_worker(self, process):
        local_path = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"])

        parts_send = []
        for f in self.files:
            part = {
                "name": f["path"].split("\\")[-1],
                "origin_path": os.path.join(self.project["server_path"], utils.remove_path(local_path, f["path"]))
            }
            parts_send.append(part)

        if not self.update_only:
            ret = env.net_manager.parts.register_parts(self.project["id"], parts_send)
            start_idx = ret["start_idx"]

            ids = []
            for i in range(len(parts_send)):
                ids.append(start_idx + i)

        files_size_convert = 0
        if self.settings["auto_convert_all_formats"]:
            for i in range(len(self.files)):
                f = self.files[i]
                ext = f["path"].split(".")[-1]
                if ext in CONVERT_WAYS:
                    convert_list = CONVERT_WAYS[ext]
                else:
                    continue
                f["size"] = os.path.getsize(f["path"])
                files_size_convert += (f["size"]*len(convert_list))
        
        if self.update_only:
            for i in range(len(self.parts)):
                self.parts[i]["size"] = os.path.getsize(self.parts[i]["local_path"])

        files_size_copy = env.file_manager.get_list_size(self.files)
        files_size = files_size_convert + files_size_copy
        process.progress.full = files_size
        
        task_copy_pro = Progress()
        task_copy_pro.full = files_size_copy

        task_copy = process.append_task(lambda: 1+1, "Копирование", task_copy_pro, _disable_task_end_on_func_end=True)
        
        self.workers.append(task_copy)

        self.copied_pathes = []

        task_copy.progress.signals.progress_changed.connect(self.copy_update_progress)
        process.progress.signals.progress_changed.connect(self.update_overall_progress)

        if not self.update_only:
            for i in range(len(self.files)):
                ext = self.files[i]["path"].split(".")[-1]
                file = self.files[i]["path"].split(".")[0]
                new_name = file.split("\\")[-1] + f"_PW{str(start_idx+i)}." + ext
                self.files[i]["id"] = start_idx+i
                path_from = self.files[i]["path"]
                try:
                    path = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"])
                    path = os.path.join(path, "ДЕТАЛИ-PW")

                    dir_name = get_dir_name_by_ext(ext)
                    if dir_name == None:
                        dir_name = ext

                    path = os.path.join(path, dir_name)

                    if not os.path.exists(path):
                        os.mkdir(path)

                    path = os.path.join(path, new_name)
                    if os.path.isfile(path):
                        os.remove(path)
                    shutil.copy(self.files[i]["path"], path)
                    env.file_manager.sync_update_time(self.files[i]["path"], path)
                    file_new = self.files[i].copy()
                    file_new["path"] = path
                    self.copied_pathes.append(file_new)
                    self.print_terminal(f"Копирование файла \n{path_from} -> {path}")
                except Exception as e:
                    print(e)
                    task_copy.set_status(FAILED)
                    path = self.files[i]["path"]
                    self.print_terminal(f"Не удалось создать копию файла: {path_from} -> {path}", color="red")
                    #utils.message(f"Не удалось создать копию файла: {path} -> {new_name}")
                    process.set_status(FAILED)
                    return
                
                task_copy_pro.add(self.files[i]["size"])
                process.progress.add(self.files[i]["size"])

            ids = []
            for i in range(len(parts_send)):
                ids.append(start_idx+i)

            env.task_manager.run_silent_task(lambda: self.callback_server_after_process_end(ids))
            
            if task_copy.status != FAILED:
                task_copy.set_status(ENDED)
        
        else:
            for i in range(len(self.parts)):
                part = self.parts[i]
                ext = self.parts[i]["local_path"].split(".")[-1]
                file = self.parts[i]["local_path"].split(".")[0]
                self.files[i]["id"] = self.parts[i]["id"]
                id = part["id"]
                new_name = file.split("\\")[-1] + f"_PW{str(id)}." + ext
                path_from = self.parts[i]["local_path"]
                try:
                    path = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"])
                    path = os.path.join(path, "ДЕТАЛИ-PW")

                    dir_name = get_dir_name_by_ext(ext)
                    if dir_name == None:
                        dir_name = ext

                    path = os.path.join(path, dir_name)

                    if not os.path.exists(path):
                        os.mkdir(path)

                    path = os.path.join(path, new_name)
                    if os.path.isfile(path):
                        os.remove(path)
                    shutil.copy(self.parts[i]["local_path"], path)
                    env.file_manager.sync_update_time(self.parts[i]["local_path"], path)
                    file_new = self.parts[i].copy()
                    file_new["path"] = path
                    self.copied_pathes.append(file_new)
                    self.print_terminal(f"Копирование файла \n{path_from} -> {path}")
                except Exception as e:
                    print(e)
                    task_copy.set_status(FAILED)
                    path = self.parts[i]["local_path"]
                    self.print_terminal(f"Не удалось создать копию файла: {path_from} -> {path}", color="red")
                    #utils.message(f"Не удалось создать копию файла: {path} -> {new_name}")
                    process.set_status(FAILED)
                    return
                task_copy_pro.add(self.parts[i]["size"])
                process.progress.add(self.parts[i]["size"])
            
            if task_copy.status != FAILED:
                task_copy.set_status(ENDED)
        

        if not self.settings["auto_convert_all_formats"]:
            process.set_status(ENDED)
            return

        tasks_convert = []
        tasks_count = int(env.config_manager["heavy_processing"]["task_threads"])

        files_kompas = []
        files_other = []
        for i in range(len(self.files)):
            f = self.files[i]
            if self.update_only:
                self.files[i]["id"] = self.parts[i]["id"]
            ext = f["path"].split(".")[-1]
            if ext not in CONVERT_WAYS:
                continue
            if ext in ["m3d", "frw", "a3d", "cdw"]:
                files_kompas.append(f)
            else:
                files_other.append(f)

        files_count_for_task = len(files_other)//(tasks_count)

        if files_count_for_task < 1 and len(files_other) > 0:
            task_convert_pro = Progress()
            task_convert = process.append_task(lambda: self.convert_worker(files_other, task_convert_pro, 
            process=process), "Конвертирование", task_convert_pro)
            self.workers.append(task_convert)
            task_convert_old = task_convert_pro

        j = 0
        if len(files_other) > 0:
            for i in range(tasks_count-1):
                task_convert_pro = Progress()

                fn = lambda files_s=files_other[j:(j+files_count_for_task)], task_convert_pro_s=task_convert_pro, process_s=process: self.convert_worker(files_s, task_convert_pro_s, process_s)
                # fuck lambda.

                task_convert = process.append_task(fn, f"[Поток {str(i+1)}] Конвертирование", task_convert_pro)
                j += files_count_for_task
                self.workers.append(task_convert)

        last_files = files_other[j:]

        if len(last_files) > 0:
            task_convert_pro = Progress()
            fn = lambda files_s=last_files, task_convert_pro_s=task_convert_pro, process_s=process: self.convert_worker(files_s, task_convert_pro_s, process_s)
            task_convert = process.append_task(fn, f"[Поток {str(tasks_count)}] Конвертирование", task_convert_pro)
            self.workers.append(task_convert)

        if len(files_kompas) > 0:
            task_convert_pro = Progress()

            fn = lambda files_s=files_kompas, task_convert_pro_s=task_convert_pro, process_s=process: self.convert_worker_kompas(files_s, task_convert_pro_s, process_s)

            task_convert = process.append_task(fn, f"[Поток {len(self.workers)}] Конвертирование КОМПАС-3D", task_convert_pro)
            self.workers.append(task_convert)

        self.signals.update.emit()

    def convert_worker_kompas(self, files, progress, process):
        size = 0
        for f in files:
            ext = f["path"].split(".")[-1]
            convert_list = CONVERT_WAYS[ext]
            size += (f["size"]*len(convert_list))

        progress.full = size
        for f in files:
            ext = f["path"].split(".")[-1]
            convert_list = CONVERT_WAYS[ext]
            failed = False
            path = f["path"]
            for to_ext in convert_list:
                if ext == "a3d":
                    if not self.settings["enable_a3d_convert"]:
                        progress.add(f["size"])
                        process.progress.add(f["size"])
                        continue
                try:
                    path_new = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"])
                    path_new = os.path.join(path_new, "ДЕТАЛИ-PW")
                    path_new = os.path.join(path_new, get_dir_name_by_ext(to_ext))
                    path_new = os.path.join(path_new, path.split("\\")[-1])
                    id = str(f["id"])
                    path_new = path_new.split(".")[0] + f"_PW{id}"
                    path_new = path_new + "." + to_ext
                    if os.path.isfile(path_new):
                        os.remove(path_new)
                    env.convert_manager.convert(path, path_new)
                except Exception as e:
                    failed = True
                    self.print_terminal(f"Не удалось сконвертировать: {path} -> {path_new}\n Ошибка: {str(e)}", color="red")

                progress.add(f["size"])
                process.progress.add(f["size"])
            

            if failed:
                self.print_terminal(f"Попытка конвертации окончилась с ошибкой: {path}", color="yellow")
            else:
                self.print_terminal(f"Успешно конвертирование: \n{path}")

    def convert_worker(self, files, progress, process):
        size = 0
        for f in files:
            ext = f["path"].split(".")[-1]
            convert_list = CONVERT_WAYS[ext]
            size += (f["size"]*len(convert_list))

        progress.full = size
        for f in files:
            ext = f["path"].split(".")[-1]
            convert_list = CONVERT_WAYS[ext]
            failed = False
            path = f["path"]
            for to_ext in convert_list:
                try:
                    path_new = os.path.join(env.config_manager["path"]["projects_path"], self.project["name"])
                    path_new = os.path.join(path_new, "ДЕТАЛИ-PW")
                    path_new = os.path.join(path_new, get_dir_name_by_ext(to_ext))
                    path_new = os.path.join(path_new, path.split("\\")[-1])
                    id = str(f["id"])
                    path_new = path_new.split(".")[0] + f"_PW{id}"
                    path_new = path_new + "." + to_ext
                    if os.path.isfile(path_new):
                        os.remove(path_new)
                    env.convert_manager.convert(path, path_new)
                except Exception as e:
                    breakpoint()
                    failed = True
                    self.print_terminal(f"Не удалось сконвертировать: {path} -> {path_new}\n Ошибка: {str(e)}", color="red")

                progress.add(f["size"])
                process.progress.add(f["size"])
            

            if failed:
                self.print_terminal(f"Попытка конвертации окончилась ошибкой: {path}", color="yellow")
            else:
                self.print_terminal(f"Успешно конвертирование: \n{path}")

    def update_workers_show(self):
        for w in self.workers_entries:
            if w.parent() != None:
                w.setParent(None)

        self.workers_entries = []

        for i in range(len(self.workers)):
            worker = self.workers[i]
            t = TaskListEntry(worker, parent=self)
            self.scrollWidgetLayout.insertWidget(i, t)
            self.scrollWidgetLayout.setAlignment(t, Qt.AlignmentFlag.AlignTop)

            self.workers_entries.append(t)
        
        self.update_overall_progress(None, manual=True)

    def show_donut(self):
        self.hidden.show()
        env.task_manager.run_silent_task(self.hidden.donut_render)

    def copy_update_progress(self, pg):
        self.progress_bar_copy.setValue(pg)
    def update_overall_progress(self, pg, manual=False):
        if manual:
            self.progress_bar_overall.setValue(self.process.progress.get_percentage())
        else:
            self.progress_bar_overall.setValue(pg)

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