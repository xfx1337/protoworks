from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QScrollArea

from UI.widgets.QClickableLabel import QClickableLabel

from UI.task_manager.TaskListEntry import TaskListEntry

import UI.stylesheets

from environment.environment import Environment
env = Environment()

class TaskManagerWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.tasks_entries = []

        self.layout = QVBoxLayout()
        self.setWindowIcon(env.templates_manager.icons["proto"])
        self.setMinimumSize(QSize(800, 600))

        self.setWindowTitle(f"Диспетчер задач")

        self.label = QLabel("Диспетчер задач")
        self.layout.addWidget(self.label)
        self.layout.setAlignment(self.label, Qt.AlignmentFlag.AlignTop)

        self.scrollable = QScrollArea()
        self.scrollable.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollable.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollable.setWidgetResizable(True)

        self.scrollWidgetLayout = QVBoxLayout()
        self.scrollWidgetLayout.setSpacing(0)
        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollWidgetLayout)
        self.scrollable.setWidget(self.scrollWidget)
        #self.scrollable.setLayout(self.scroll_layout)
        
        self.scrollWidgetLayout.addStretch()

        self.layout.addWidget(self.scrollable)
        self.setLayout(self.layout)

        env.main_signals.task_status_changed.connect(self.update_data)

        self.update_data()
    
    def update_data(self):
        tasks = env.task_manager.get_tasks()
        
        for p in self.tasks_entries:
            if p.parent() != None:
                p.setParent(None)

        self.tasks_entries = []


        tasks_sorted = sorted(tasks, key=lambda key: (tasks[key].time_started, tasks[key].name))

        for i in range(len(tasks_sorted)):
            task = tasks[tasks_sorted[i]]
            p = TaskListEntry(task, parent=self)
            self.scrollWidgetLayout.insertWidget(i, p)
            self.scrollWidgetLayout.setAlignment(p, Qt.AlignmentFlag.AlignTop)

            self.tasks_entries.append(p)