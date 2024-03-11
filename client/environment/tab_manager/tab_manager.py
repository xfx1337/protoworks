import utils

class TabManager():
    def __init__(self, env):
        self.env = env
        self.opened_tabs = {}
        self.refresh_callback = None
        
    def open_tab(self, tab):
        tab.set_id(utils.get_unique_id())
        tab.set_exit_callback(lambda: self.close_tab(tab.id))
        
        self.opened_tabs[tab.id] = tab
        return tab.id

    def close_tab(self, id):
        self.opened_tabs[id].setParent(None)
        del self.opened_tabs[id]
        if self.refresh_callback != None:
            self.refresh_callback()

    def close_all(self):
        keys = list(self.opened_tabs.keys())
        for i in keys:
            self.close_tab(i)
            
    def get_tabs_count(self):
        return len(list(self.opened_tabs.keys()))

    def get_opened_tabs_by_type(self, tab_type):
        ret = []
        for tab in self.opened_tabs.keys():
            if type(self.opened_tabs[tab]) == tab_type:
                ret.append(tab)
        
        return ret
    
    def get_tab_by_id(self, id):
        return self.opened_tabs[id]

    def set_refresh_callback(self, func):
        self.refresh_callback = func