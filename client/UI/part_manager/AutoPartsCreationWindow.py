from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea, QMenu, QFileDialog, QApplication, QFrame
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


from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()

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
        self.layout.addWidget(self.label)

        self.folder_select = QPathInput("Директория исходных файлов")
        self.extensions = QChooseManyCheckBoxes("Форматы исходных файлов", FILE_FORMATS.values())

        

        self.layout.addWidget(self.folder_select)
        self.layout.addWidget(self.extensions)

        self.setLayout(self.layout)

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
        self.setFixedSize(QSize(600, 600))

        self.description = QLabel("В данном разделе можно автоматически создавать Детали-ProtoWorks для их дальнейшей печати, конвертации в другие форматы и тд. ProtoWorks работает только с деталями, которые зарегистрованны здесь.")
        self.description.setWordWrap(True)
        self.layout.addWidget(self.description)

        self.create_new_parts_wnd = CreateNewParts(self.project)
        self.layout.addWidget(self.create_new_parts_wnd)

        self.setLayout(self.layout)