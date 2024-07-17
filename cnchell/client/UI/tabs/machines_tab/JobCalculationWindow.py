from PySide6.QtCore import QSize, Qt
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication

import os, shutil
import subprocess
import utils

from environment.environment import Environment
env = Environment()

from environment.task_manager.Progress import Progress

import UI.stylesheets as stylesheets
from UI.widgets.QClickableLabel import QClickableLabel
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QDoubleLabel import QDoubleLabel
from UI.widgets.QAreUSureDialog import QAreUSureDialog

from UI.tabs.machines_tab.EditSlaveWnd import EditSlaveWnd

from UI.widgets.QYesOrNoDialog import QYesOrNoDialog
from UI.widgets.QFilesListSureDialog import QFilesListSureDialog
from UI.widgets.QAskForNumberDialog import QAskForNumberDialog
from UI.widgets.QAskForFilesDialog import QAskForFilesDialog
from UI.widgets.QAskForDirectoryDialog import QAskForDirectoryDialog

from UI.widgets.QProgramWidget import QProgramWidget

import defines

from PySide6.QtCore import Signal, QObject

class JobCalculationFiles:
    def __init__(self):
        self.selected_file = None
        self.calculated_file = None

class JobCalculationWindow(QFrame):
    def __init__(self, job, change_callback=None, queue=None):
        super().__init__()
        self.job = job
        self.queue = queue
        self.change_callback = change_callback

        self.setWindowIcon(env.templates_manager.icons["cnchell"])
        #self.setMinimumSize(QSize(800, 600))
        id = self.job["id"]
        self.setWindowTitle(f"Расчёт работы ID: {id}")

        self.files = JobCalculationFiles()

        self.layout = QVBoxLayout()
        #self.layout.setSpacing(0)
        #self.layout.setContentsMargins(0,0,0,0)

        self.label = QLabel("Существуют файлы(gcode, pwma, pm3, ..), которые уже рассчитаны под конкретный станок, они не могут быть перерассчитаны под другой станок. Так же существуют файлы, которые под станок не рассчитаны(stl), их уже можно рассчитать под станок. Ниже нужно выбрать файл, по которому будет проводится расчёт для станка. Если же уже есть рассчитанный в ручную файл - выберите его как рассчитанный")
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label)

        self.h_layout = QHBoxLayout()

        self.left_layout = QVBoxLayout()
        self.job_info = JobInfoFrame(self.job)
        self.file_select_frame = FileSelectFrame(self.job, self.files)
        self.left_layout.addWidget(self.job_info)
        self.left_layout.addWidget(self.file_select_frame)
        self.h_layout.addLayout(self.left_layout, 50)

        self.right_layout = QVBoxLayout()
        self.calculation_frame = CalculationFrame(self.job, self.files, self)
        self.right_layout.addWidget(self.calculation_frame)

        self.h_layout.addLayout(self.right_layout, 50)

        self.layout.addLayout(self.h_layout)

        self.save_btn = QInitButton("Сохранить расчёт", callback=self.save)
        self.layout.addWidget(self.save_btn)
        self.setLayout(self.layout)

    def save(self):
        files = []
        if self.files.selected_file != None and os.path.isfile(self.files.selected_file):
            self.job["unique_info"]["job_send_filename"] = utils.get_unique_id()
            self.job["unique_info"]["job_filename"] = self.files.selected_file.split("\\")[-1]
            files.append({self.job["unique_info"]["job_send_filename"]: self.files.selected_file})
        if self.files.calculated_file != None and os.path.isfile(self.files.calculated_file):
            self.job["unique_info"]["job_send_pre_calculated_filename"] = utils.get_unique_id()
            self.job["unique_info"]["job_pre_calculated_filename"] = self.files.calculated_file.split("\\")[-1]
            self.job["unique_info"]["job_pre_calculated"] = True
            self.job["unique_info"]["job_pre_calculated_machine"] = self.queue.machine["id"]

            self.job["work_time"] = env.machine_utils.calculate_job_time_by_file(self.files.calculated_file)

            files.append({self.job["unique_info"]["job_send_pre_calculated_filename"]: self.files.calculated_file})
        if self.job["status"] == "Ошибка. Отсутствует файл расчёта для станка.":
            self.job["status"] = "В ожидании"
        
        env.net_manager.work_queue.overwrite_job_files(self.job["id"], self.job, files)
        if self.change_callback != None:
            self.change_callback(self.job)
        utils.message("Отправлено", tittle="Оповещение")

class JobInfoFrame(QFrame):
    def __init__(self, job):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)
        self.job = job

        self.layout = QVBoxLayout()

        unique_info = job["unique_info"]
        status = job["status"]
        work_time = job["work_time"]
        work_start = job["work_start"]

        job_id = job["id"] 


        job_name = "Нет"
        if "job_name" in unique_info:
            job_name = unique_info["job_name"]
        
        job_filename = "Нет"
        if "job_filename" in unique_info:
            job_filename = unique_info["job_filename"]
        
        job_part_id = "Нет"
        if "job_part_id" in unique_info:
            job_part_id = unique_info["job_part_id"]
        
        job_part_name = "Нет"
        if "job_part_name" in unique_info:
            job_part_name = unique_info["job_part_name"]

        job_project_name = "Нет"
        job_project_id = "Нет"
        if "job_project_id" in unique_info:
            job_project_id = unique_info["job_project_id"]
            job_project_name = env.net_manager.projects.get_project_info(job_project_id)["name"]

        job_pre_calculated = "Нет"
        if "job_pre_calculated" in unique_info and unique_info["job_pre_calculated"]:
            job_pre_calculated = "Да"
        
        job_pre_calculated_machine_name = "Нет"
        if "job_pre_calculated_machine" in unique_info:
            job_pre_calculated_machine = unique_info["job_pre_calculated_machine"]
            if job_pre_calculated_machine != -1:
                try:
                    job_pre_calculated_machine_name = env.net_manager.machines.get_machine(job_pre_calculated_machine)["name"]
                except:
                    job_pre_calculated_machine_name = "Недоступно."


        job_count_done = unique_info["job_count_done"]
        job_count_need = unique_info["job_count_need"]

        self.id_label = QLabel(f"ID: {job_id}")
        self.name_label = QLabel(f"Название: {job_name}")
        self.filename_label = QLabel(f"Название файла: {job_filename}")
        self.part_id_label = QLabel(f"ID детали: {job_part_id}")
        self.part_name_label = QLabel(f"Название детали: {job_part_name}")
        self.count_need_label = QLabel(f"Требуемое количество: {job_count_need}")
        self.count_done_label = QLabel(f"Количество выполненных: {job_count_done}")
        self.project_name_label = QLabel(f"Название проекта: {job_project_name}")
        self.job_pre_calculated_label = QLabel(f"Рассчитана под станок: {job_pre_calculated}")
        self.job_pre_calculated_machine_label = QLabel(f"Рассчитана под станок(название): {job_pre_calculated_machine_name}")
        self.work_time_label = QLabel(f"Время работы, рассчитанное под станок: {utils.seconds_to_str(work_time*(job_count_need-job_count_done))}")
        
        if work_start >= 0:
            self.work_start_label = QLabel(f"Время начала работы: {utils.time_by_unix(work_start)}")
        else:
            self.work_start_label = QLabel(f"Время начала работы: Не начата.")

        self.status_label = QLabel(f"Состояние: {status}")

        self.layout.addWidget(self.id_label)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.filename_label)
        self.layout.addWidget(self.part_id_label)
        self.layout.addWidget(self.part_name_label)
        self.layout.addWidget(self.count_need_label)
        self.layout.addWidget(self.count_done_label)
        self.layout.addWidget(self.project_name_label)
        self.layout.addWidget(self.job_pre_calculated_label)
        self.layout.addWidget(self.job_pre_calculated_machine_label)
        self.layout.addWidget(self.work_time_label)
        self.layout.addWidget(self.work_start_label)
        self.layout.addWidget(self.status_label)

        self.setLayout(self.layout)

class FileSelectFrame(QFrame):
    def __init__(self, job, files):
        super().__init__()
        self.job = job
        self.files = files
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()

        unique_info = job["unique_info"]

        calculated_filename = "Нет"
        job_filename = "Нет"
        if "job_filename" in unique_info:
            job_filename = unique_info["job_filename"]
            self.files.selected_file = job_filename
        else:
            self.files.selected_file = None
        
        job_file_name = job_filename.split('\\')[-1]

        if "job_pre_calculated_filename" in unique_info:
            calculated_filename = unique_info["job_pre_calculated_filename"]
            self.files.calculated_file = calculated_filename
        else:
            self.files.calculated_file = None
        
        calculated_file_name = calculated_filename.split('\\')[-1]

        self.download_files_btn = QInitButton("Скачать файлы с сервера", callback=self.download_files)


        self.file_selected_label = QLabel(f"Файл, по которому проводится расчёт: {job_file_name}")
        
        self.file_selected_select_btn = QInitButton("Установить файл, по которому должен быть проведён расчёт", callback=self.change_file_selected)
        self.file_selected_select_orig_btn = QInitButton("Установить для этого оригинальный файл детали", callback=self.set_original)
        self.open_file_directory_btn = QInitButton("Открыть директорию файла", callback=self.open_file_directory)

        job_file_name = job_filename.split("\\")[-1]
        self.file_calculated_label = QLabel(f"Рассчитанный под станок файл: {calculated_file_name}")
        self.file_calculated_select_btn = QInitButton("Установить файл, который считать рассчитанным", callback=self.set_calculated)
        self.open_calc_directory_btn = QInitButton("Открыть директорию рассчитанного файла", callback=self.open_calc_directory)


        self.layout.addWidget(self.download_files_btn)
        self.layout.addWidget(self.file_selected_label)
        self.layout.addWidget(self.file_selected_select_btn)
        self.layout.addWidget(self.file_selected_select_orig_btn)
        self.layout.addWidget(self.open_file_directory_btn)
        self.layout.addWidget(self.file_calculated_label)
        self.layout.addWidget(self.file_calculated_select_btn)
        self.layout.addWidget(self.open_calc_directory_btn)

        self.setLayout(self.layout)
    
    def download_files(self):
        self.dlg = QAskForDirectoryDialog("Выберите папку для загрузки", callback_yes=self.got_download_path)
        self.dlg.exec()
        
    def got_download_path(self, download_path):
        pro = Progress()
        env.task_manager.append_task(lambda: self.download_thread(pro, download_path), "[Загрузка] Скачивание файлов", progress=pro)

    def download_thread(self, pro, download_path, dont_open_explorer=False):
        files = []
        files_rename = []
        s_path = os.path.join(env.net_manager.files.get_server_path("machines_path"), "WorkingDirectory")
        try:
            path = os.path.join(s_path, self.job["unique_info"]["job_send_pre_calculated_filename"])
            files_rename.append(self.job["unique_info"]["job_pre_calculated_filename"])
            files.append(path)
        except:
            pass
        try:
            path = os.path.join(s_path, self.job["unique_info"]["job_send_filename"])
            files_rename.append(self.job["unique_info"]["job_filename"])
            files.append(path)
        except:
            pass
    
        path = env.net_manager.files.get_zipped_files(path=s_path, files=files, progress=pro)
        env.file_manager.unzip_data_archive(os.path.join(path), download_path)

        files_got = []
        for i in range(len(files)):
            shutil.copy(os.path.join(download_path, files[i].split("\\")[-1]), os.path.join(download_path, files_rename[i]))
            files_got.append(os.path.join(download_path, files_rename[i]))
            os.remove(os.path.join(download_path, files[i].split("\\")[-1]))

        path = "\\".join(download_path.split("\\")[:-1])
        if not dont_open_explorer:
            subprocess.Popen(f'explorer "{path}"')
        return files_got
        

    def open_calc_directory(self):
        path = self.files.calculated_file
        path = "\\".join(path.split("\\")[:-1])
        subprocess.Popen(f'explorer "{path}"')

    def open_file_directory(self):
        path = self.files.selected_file
        path = "\\".join(path.split("\\")[:-1])
        subprocess.Popen(f'explorer "{path}"')


    def change_file_selected(self):
        self.dlg = QAskForFilesDialog("Выберите файл для расчёта", callback_yes=self.selected_file_changed, only_one_file=True)
        self.dlg.exec()
    def selected_file_changed(self, file):
        self.files.selected_file = file
        calc_file_name = file.split('\\')[-1]
        self.file_selected_label.setText(f"Файл, по которому проводится расчёт: {calc_file_name}")
    
    def set_original(self):
        if "job_part_id" not in self.job["unique_info"]:
            utils.message("Работа не по детали. Оригинал недоступен")
            return

        part_id = self.job["unique_info"]["job_part_id"]
        part_project_id = self.job["unique_info"]["job_project_id"]
        project = env.net_manager.projects.get_project_info(part_project_id)
        part = env.net_manager.parts.get_part_info(part_id, part_project_id)
        client_path = utils.remove_path(project["server_path"], part["path"])
        project_path = os.path.join(env.config_manager["path"]["projects_path"], project["name"])
        client_path = os.path.join(project_path, client_path)
        
        self.files.selected_file = client_path
        calc_file_name = client_path.split('\\')[-1]
        self.file_selected_label.setText(f"Файл, по которому проводится расчёт: {calc_file_name}")


    def set_calculated(self):
        self.dlg = QAskForFilesDialog("Выберите файл, который считать рассчитанным", callback_yes=self.calculated_file_changed, only_one_file=True)
        self.dlg.exec()
    def calculated_file_changed(self, file):
        self.files.calculated_file = file
        calc_file_name = file.split('\\')[-1]
        self.file_calculated_label.setText(f"Рассчитанный под станок файл: {calc_file_name}")

class CalculationFrame(QFrame):
    def __init__(self, job, files, parent):
        self.parent = parent
        super().__init__()
        self.job = job
        self.files = files
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Ниже представлены варианты автоматического расчёта. Если есть потребность рассчитать внешним ПО просто нажмите кнопку 'Открыть директорию файла', файл который вы рассчитайте выберите в левом окне как рассчитанный")
        self.label.setWordWrap(True)

        self.layout.addWidget(self.label)

        self.orca_slicer_btn = QProgramWidget("OrcaSlicer(FDM)", "orca", "Рассчитать в OrcaSlicer", callback=self.open_orca, pixmap_sizes=[64,64])
        self.layout.addWidget(self.orca_slicer_btn)
        self.layout.setAlignment(Qt.AlignTop)

    def open_orca(self):
        orca_path = os.path.join(env.config_manager["path"]["orca_path"], "orca-slicer.exe")

        pro = Progress()
        files = self.parent.file_select_frame.download_thread(pro, env.config_manager["path"]["temp_path"], dont_open_explorer=True)

        if os.path.isfile(self.parent.file_select_frame.files.selected_file):
            files.append(self.parent.file_select_frame.files.selected_file)

        if "job_part_id" in self.job["unique_info"]:
            job_part_id = self.job["unique_info"]["job_part_id"]
            job_project_id = self.job["unique_info"]["job_project_id"]
            project = env.net_manager.projects.get_project_info(job_project_id)
            files_part = env.part_manager.get_available_part_files_by_id(project, job_part_id, path_only=True)
            for f in files_part:
                files.append(f)

        out = "Сейчас будет открыт OrcaSlicer, в котором вы сможете создать GCODE под выбранный в OrcaSlicer станок. Пожалуйста, ознакомьтесь с пунктом меню или инструкции 'Настройки->Конфигурация подключений станков на клиенте'. После слайсинга в OrcaSlicer вам нужно будет экспортировать файл на станок."

        try:
            idx = self.parent.queue.machine["id"]
            host_type_i = env.net_manager.slaves.get_slave(self.parent.queue.machine["slave_id"])["slave"]["type"]
            if host_type_i in [defines.FDM_DIRECT, defines.FDM_OCTO, defines.FDM_KLIPPER]:
                host_type = "Octo/Klipper"
            else:
                host_type = "Не поддерживается"
            out += f"\nID станка, в очереди которого находится деталь сейчас: {idx}\nХост станка: http://127.0.0.1:{defines.FAKE_OCTO_FIRST_PORT+idx}\nТип хоста: {host_type}"
        except:
            pass

        is_part = False
        job_part_id = -1
        if "job_part_id" in self.job["unique_info"]:
            job_part_id = self.job["unique_info"]["job_part_id"]
            is_part = True

        for f in files:
            if f.split(".")[-1] in defines.ORCA_SLICER_INPUT_FILES:
                if "_PW" not in f and is_part:
                    f_new = f.split(".")[0] + f"_PW{job_part_id}." + f.split(".")[-1]
                    
                    try: os.rename(f, f_new)
                    except: pass
                    f = f_new

                subprocess.Popen(f'"{orca_path}" "{f}"')
                utils.message(out, tittle="Оповещение")
                self.parent.hide()
                del self.parent
                return

