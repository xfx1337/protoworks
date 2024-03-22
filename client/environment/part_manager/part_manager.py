import requests

from singleton import singleton

import exceptions

from environment.part_manager.Part import Part

@singleton
class PartManager:
    def __init__(self, env):
        self.env = env
    
    