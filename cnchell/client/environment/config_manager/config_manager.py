from configparser import *

from singleton import singleton
import os

@singleton
class Config(ConfigParser):
    def __init__(self, config_file, env=None):
        self.env = env
        super().__init__()
        self.config_file = config_file
        self.read(config_file, encoding="utf8")
    
    def write_host(self, host):
        if "server" not in self:
            self["server"] = {}
        self["server"]["host"] = host
        self.override()
        
    def override(self):
        with open(self.config_file, 'w', encoding="utf-8") as f:
            self.write(f)

    def get_abs_path(self):
        return os.path.join(os.getcwd(), self.config_file)