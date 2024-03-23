from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame, QCheckBox
from PySide6.QtCore import QTimer


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


from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()

from environment.environment import Environment
env = Environment()


# обьяснение
# выбор директории работы
# выбор исходного формата/все
# отдельная вкладка на перезапись старых деталей
# отдельная вкладка на обновление деталей по выбранному формату
# включение автоматической конвертации деталей в другие форматы
# отдельная кнопка на запуск обработчика деталей сборки компас
# окно настройки параметров конвертации


class CreateNewParts(QFrame):
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


        self.layout.addWidget(self.label, 20)
        self.layout.addWidget(self.folder_choosing_frame, 10)
        self.layout.addWidget(self.extensions, 20)
        self.layout.addWidget(self.files_show, 50)

        self.setLayout(self.layout)
    
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


class OldDetailsOverWrite(QFrame):
    def __init__(self, project):
        super().__init__()
        self.project = project

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        self.layout = QVBoxLayout()

        self.label = QLabel("Перезапись созданных деталей")
        self.label.setFixedSize(self.label.sizeHint())
        self.layout.addWidget(self.label)

        self.description = QLabel("ВНИМАНИЕ: Данный раздел опасен так, как при его работе происходит удаление старых файлов выбранной детали")
        self.layout.addWidget(self.description)



class AutoPartsCreationWindow(QWidget):
    def __init__(self, project):
        super().__init__()
    
        self.project = project

        self.layout = QVBoxLayout()

        self.setWindowTitle(f"Автоматическое создание деталей")
        self.setWindowIcon(templates_manager.icons["proto"])
        self.setFixedSize(QSize(800, 800))

        self.description = QLabel("В данном разделе можно автоматически создавать Детали-ProtoWorks для их дальнейшей печати, конвертации в другие форматы и тд. ProtoWorks работает только с деталями, которые зарегистрованны здесь.")
        self.description.setWordWrap(True)
        self.layout.addWidget(self.description)

        self.create_new_parts_wnd = CreateNewParts(self.project)
        self.layout.addWidget(self.create_new_parts_wnd)

        self.setLayout(self.layout)