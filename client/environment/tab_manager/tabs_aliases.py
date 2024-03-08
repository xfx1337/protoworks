from UI.tabs.projects_tab.projects_tab import ProjectsWidget
from UI.tabs.settings_tab.settings_tab import SettingsWidget

TABS_ALIASES = {"projects": ProjectsWidget, "settings": SettingsWidget}

def get_tab_by_alias(alias):
    return TABS_ALIASES[alias]()