from UI.tabs.projects_tab.projects_tab import ProjectsWidget
from UI.tabs.settings_tab.settings_tab import SettingsWidget
from UI.tabs.machines_tab.machines_tab import MachinesWidget

TABS_ALIASES = {"projects": ProjectsWidget, "settings": SettingsWidget, "machines": MachinesWidget}

def get_tab_by_alias(alias):
    return TABS_ALIASES[alias]