from environment.file_manager.File import File
from environment.file_manager.ZipDataFile import ZipDataFile

import zipfile

from singleton import singleton

from defines import *

import utils
import os, shutil

from environment.file_manager.ZipDataFileDecoder import ZipDataFileDecoder
zip_data_file_decoder = ZipDataFileDecoder()

from ezdxf import recover

@singleton
class ConvertManager:
    def __init__(self, env):
        self.env = env
    
    def convert(self, fr, to):
        if fr.split(".")[-1] in ["m3d", "frw"]:
            self.env.kompas3d.request(lambda: self.env.kompas3d.files.convert(fr, to), ask_response=True)
        
        if fr.split(".")[-1] in ["dxf", "dwg"]:
            self.convert_dxf_dwg(fr, to)
    
        self.env.file_manager.sync_update_time(fr, to)
    
    def convert_dxf_dwg(self, fr, to):
        doc, _ = recover.readfile(fr)
        doc.dxfversion = self.env.config_manager["formats"]["preffered_vector_graphics_ver"]
        doc.saveas(to)