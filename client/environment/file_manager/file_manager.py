from environment.file_manager.File import File
from environment.file_manager.ZipDataFile import ZipDataFile

import zipfile

from singleton import singleton

from defines import *

import utils
import os

@singleton
class FileManager:
    def __init__(self, env):
        self.env = env
    
    def get_files_list(self, path):
        files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path) for f in filenames]
        dirs = self.scan_for_subdirs(path)

        files_list = []

        for f in files:
            f_c = File(path=f, f_type=FILE)
            files_list.append(f_c)

        for f in dirs:
            files_list.append(f)

        return files_list
    
    def files_list_to_dict_list(self, files_list):
        obj = []
        for f in files_list:
            obj.append(f.to_dict())
        return obj

    def get_list_size(self, files_list):
        size = 0
        for f in files_list:
            if f.f_type == FILE:
                size += f.size
        
        return size

    def make_data_zip(self, files_list, relative=None, additional_data_to_send=None):
        dirs = [f for f in files_list if f.f_type == FOLDER]
        files = [f for f in files_list if f.f_type == FILE]

        data_file = ZipDataFile(files=files, dirs=dirs, relative_path=relative)
        data_file.create_entry()
        data_file.create_metadata()
        data_file.create_dirs_list()
        data_file.create_files_list()
        data_file.create_additional_data(additional_data_to_send)

        file_name = utils.get_unique_id()
        data_filename = os.path.join(self.env.config_manager["path"]["temp_path"], (file_name))+".txt"
        zip_filename = os.path.join(self.env.config_manager["path"]["temp_path"], (file_name))+".zip"

        with open(data_filename, "w", encoding="utf-8") as f:
            f.write(data_file.string())

        self.zip_files_by_linkers(data_file.FILE_LINKERS, zip_filename, data_filename)

        self.delete_file(data_filename)

        return zip_filename
    
    def scan_for_subdirs(self, dirname):
        subfolders = self._scan_for_subdirs(dirname)

        ret = []
        for f in subfolders:
            f = File(path=f, f_type=FOLDER)
            ret.append(f)

        return ret

    def _scan_for_subdirs(self, dirname):
        subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
        for dirname in list(subfolders):
            subfolders.extend(self._scan_for_subdirs(dirname))
        
        return subfolders

        
    
    def zip(self, src_path, dest_path):
        if src_path[-1] == "\\":
            src_path = src_path[:-1]
        with zipfile.ZipFile(dest_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            _zipdir(src_path, zipf)

    def zip_files_by_linkers(self, linkers, dest_path, data_filename):
        try:
            with zipfile.ZipFile(dest_path, "w") as archive:
                for f in linkers.keys():
                    real_file_path = linkers[f]
                    arch_filename = f
                    archive.write(real_file_path, arch_filename)
                archive.write(data_filename, "PROTOWORKS_DATA.txt")
        except Exception as e:
            print("WRITING ERROR!")
            print(e)
            raise e

    def unzip(self, zip, destination):
        with zipfile.ZipFile(zip, 'r') as zip_ref:
            zip_ref.extractall(destination)

    def delete_file(self, file):
        if type(file) == type(str()):
            os.remove(file)
        elif type(file) == File():
            os.remove(file.path)