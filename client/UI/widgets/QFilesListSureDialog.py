import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QStyleOption, QStyle
from PySide6 import QtGui

from UI.widgets.QEasyScroll import QEasyScroll
from UI.widgets.QInitButton import QInitButton
from UI.widgets.QListEntry import QListEntry

import UI.stylesheets

import utils

from environment.templates_manager.templates_manager import TemplatesManager
templates_manager = TemplatesManager()

class QFilesListSureDialog(QDialog):
    def __init__(self, files_yes, files_no, tittle, text, files_yes_label, files_no_label, path_dont_show=None, sure=None):
        super().__init__()

        self.sure = sure

        self.setMinimumSize(QSize(700, 500))

        self.path_dont_show = path_dont_show
        self.files_yes = files_yes
        self.files_no = files_no

        self.setWindowTitle(tittle)
        self.setWindowIcon(templates_manager.icons["proto"])

        self.layout = QVBoxLayout()

        self.message = QLabel(text)
        self.layout.addWidget(self.message)

        self.upper_layout = QHBoxLayout()
        self.files_yes_label = QLabel(files_yes_label)
        self.files_no_label = QLabel(files_no_label)
        
        self.upper_layout.addWidget(self.files_yes_label)
        self.upper_layout.addWidget(self.files_no_label)

        self.layout.addLayout(self.upper_layout)

        self.hLayout = QHBoxLayout()

        self.files_yes_scroll = QEasyScroll()
        self.files_no_scroll = QEasyScroll()

        self.hLayout.addWidget(self.files_yes_scroll, 50)
        self.hLayout.addWidget(self.files_no_scroll, 50)

        self.layout.addLayout(self.hLayout)

        self.lower_layout = QHBoxLayout()

        self.l_arrow = QInitButton("", callback=self.left)
        self.r_arrow = QInitButton("", callback=self.right)

        self.l_arrow.setIcon(templates_manager.icons["left_arrow"])
        self.r_arrow.setIcon(templates_manager.icons["right_arrow"])

        self.lower_layout.addWidget(self.l_arrow)
        self.lower_layout.addWidget(self.r_arrow)

        self.layout.addLayout(self.lower_layout)

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.cancel)

        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

        self.files_yes_entries = []
        self.files_no_entries = []

        self.selected = []
        self.selected_column = None

        self.load_data()
    
    def load_data(self):
        for e in self.files_yes_entries:
            if e.parent != None:
                e.setParent(None)
        for e in self.files_no_entries:
            if e.parent != None:
                e.setParent(None)

        self.files_yes_entries = []
        self.files_no_entries = []

        for i in range(len(self.files_yes)):
            path = self.files_yes[i]["filename"]
            path_show = path
            if self.path_dont_show != None:
                if self.path_dont_show in path:
                    path_show = path[len(self.path_dont_show):]
                    if path_show[0] == "\\":
                        path_show = path_show[1:]

            e = QListEntry(path_show, mouse_left_callback=lambda val=i: self.select("yes", val))
            e.setToolTip("Путь:" + path + "\nПоследнее изменение: " + utils.time_by_unix(self.files_yes[i]["modification_time"]))
            self.files_yes_entries.append(e)
            self.files_yes_scroll.scrollWidgetLayout.insertWidget(i, e)
            self.files_yes_scroll.scrollWidgetLayout.setAlignment(e, Qt.AlignmentFlag.AlignTop)

        for i in range(len(self.files_no)):
            path = self.files_no[i]["filename"]
            path_show = path
            if self.path_dont_show != None:
                if self.path_dont_show in path:
                    path_show = path[len(self.path_dont_show):]
                    if path_show[0] == "\\":
                        path_show = path_show[1:]
            e = QListEntry(path_show, mouse_left_callback=lambda val=i: self.select("no", val))
            e.setToolTip("Путь:" + path + "\nПоследнее изменение: " + utils.time_by_unix(self.files_no[i]["modification_time"]))
            self.files_no_entries.append(e)
            self.files_no_scroll.scrollWidgetLayout.insertWidget(i, e)
            self.files_no_scroll.scrollWidgetLayout.setAlignment(e, Qt.AlignmentFlag.AlignTop)

        for i in range(len(self.selected)):
            self.EntrySetStyleSheet(self.selected_column, self.selected[i], UI.stylesheets.SELECTED_BORDER_STYLESHEET)

    def select(self, column, i):
        modifiers = QApplication.keyboardModifiers()
        self.EntrySetStyleSheet(column, i, UI.stylesheets.SELECTED_BORDER_STYLESHEET)
        if len(self.selected) == 1:
            if self.selected[0] == i:
                self.unselect("yes")
                self.unselect("no")
                self.selected_column = None
                self.selected = []
                return

        if self.selected_column == None or self.selected_column != column:
            self.selected_column = column
            self.unselect("yes")
            self.unselect("no")
            self.selected = [i]
            self.EntrySetStyleSheet(column, i, UI.stylesheets.SELECTED_BORDER_STYLESHEET)
            return
        else:
            if modifiers == Qt.KeyboardModifier.ControlModifier:
                self.selected.append(i)
            elif modifiers == Qt.KeyboardModifier.ShiftModifier:
                first_sel = self.selected[0]
                second_sel = i
                self.unselect(column)
                if first_sel > second_sel:
                    for j in range(first_sel, second_sel-1, -1):
                        self.EntrySetStyleSheet(column, j, UI.stylesheets.SELECTED_BORDER_STYLESHEET)
                        self.selected.append(j)
                else:
                    for j in range(first_sel, second_sel+1):
                        self.EntrySetStyleSheet(column, j, UI.stylesheets.SELECTED_BORDER_STYLESHEET)
                        self.selected.append(j)
                

            else:
                self.unselect(column)
                self.EntrySetStyleSheet(column, i, UI.stylesheets.SELECTED_BORDER_STYLESHEET)
                self.selected = [i]

    def unselect(self, column):
        if column == "yes":
            to_unselect = self.files_yes_entries
        else:
            to_unselect = self.files_no_entries
        for j in range(len(to_unselect)):
            self.EntrySetStyleSheet(column, j, UI.stylesheets.DEFAULT_BORDER_STYLESHEET)
        self.selected = []

    def EntrySetStyleSheet(self, column, i, stylesheet):
        if column == "yes":
            self.files_yes_entries[i].setStyleSheet(stylesheet)
        if column == "no":
            self.files_no_entries[i].setStyleSheet(stylesheet)
    
    def left(self):
        if len(self.selected) == 0 or self.selected_column == "yes":
            return

        last_left_id = len(self.files_yes)-1
        temp_selected = []
        for i in range(len(self.selected)):
            self.files_yes.append(self.files_no[self.selected[i]])
            temp_selected.append(last_left_id+1+i)
        
        self.selected = sorted(self.selected, reverse=True)
        for i in range(len(self.selected)):
            del self.files_no[self.selected[i]]
        
        self.unselect(self.selected_column)
        self.selected_column = "yes"
        self.selected = temp_selected

        self.load_data()

    def right(self):
        if len(self.selected) == 0 or self.selected_column == "no":
            return

        last_right_id = len(self.files_no)-1
        temp_selected = []
        for i in range(len(self.selected)):
            self.files_no.append(self.files_yes[self.selected[i]])
            temp_selected.append(last_right_id+1+i)

        self.selected = sorted(self.selected, reverse=True)
        for i in range(len(self.selected)):
            del self.files_yes[self.selected[i]]

        self.unselect(self.selected_column)
        self.selected_column = "no"
        self.selected = temp_selected

        self.load_data()
    
    def closeEvent(self, event):
        if self.sure != None:
            if self.sure[0] == None:
                self.sure[0] = False
        event.accept()

    def accept(self):
        if self.sure != None:
            self.sure[0] = True # fuck that's pointer system
        self.close()
    
    def cancel(self):
        if self.sure != None:
            self.sure[0] = False
        self.close()