class Tab():
    def __init__(self):
        self.id = None
        self.exit_callback = None

    def exit(self):
        if self.exit_callback != None:
            self.exit_callback()
    
    def set_exit_callback(self, func):
        self.exit_callback = func
    
    def set_id(self, id):
        self.id = id