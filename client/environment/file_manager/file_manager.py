from environment.file_manager.File import File
from environment.file_manager.ZipDataFile import ZipDataFile

import zipfile

from singleton import singleton

from defines import *

import utils
import os, shutil

from environment.file_manager.ZipDataFileDecoder import ZipDataFileDecoder
zip_data_file_decoder = ZipDataFileDecoder()

@singleton
class FileManager:
    def __init__(self, env):
        self.env = env
    
    def delete_empty_folders(self, root):
        deleted = set()
        for current_dir, subdirs, files in os.walk(root, topdown=False):
            still_has_subdirs = False
            for subdir in subdirs:
                if os.path.join(current_dir, subdir) not in deleted:
                    still_has_subdirs = True
                    break
        
            if not any(files) and not still_has_subdirs and ("PW" not in current_dir) and (current_dir.split("\\")[-1] not in DETAILS_DIRS):
                os.rmdir(current_dir)
                deleted.add(current_dir)

    def copy_files(self, files):
        for f in files.keys():
            shutil.copy(f, files[f])

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
        #data_file.create_dirs_list()
        data_file.create_files_list()
        if additional_data_to_send != None:
            data_file.create_additional_data(additional_data_to_send)

        file_name = utils.get_unique_id()
        data_filename = os.path.join(self.env.config_manager["path"]["temp_path"], (file_name))+".txt"
        zip_filename = os.path.join(self.env.config_manager["path"]["temp_path"], (file_name))+".zip"

        with open(data_filename, "w", encoding="utf-8") as f:
            f.write(data_file.string())

        self.zip_files_by_linkers(data_file.FILE_LINKERS, zip_filename, data_filename)

        self.delete_file(data_filename)

        return zip_filename
    
    def unzip_data_archive(self, path, extract_to):
        data = ""
        with zipfile.ZipFile(path, 'r') as archive:
            with archive.open('PROTOWORKS_DATA.txt') as data_file:
                data = str(data_file.read().decode('UTF-8'))
                data = zip_data_file_decoder.decode(data)
            
            # if "dirs" in data:
            #     for d in data["dirs"]:
            #         os.mkdir(os.path.join(extract_to, d))
            
            if "files" in data:
                dirs = {}
                for f in data["files"]:
                    dirs_f = self.get_dirs_for_file(f["path"])
                    for d in dirs_f:
                        if d not in dirs:
                            dirs[d] = 1
                for d in dirs.keys():
                    try: os.mkdir(os.path.join(extract_to, d))
                    except: pass

                for f in data["files"]:
                    archive.extract(f["arch_filename"], self.env.config_manager["path"]["temp_path"])
                    try:
                        os.rename(os.path.join(self.env.config_manager["path"]["temp_path"], f["arch_filename"]), os.path.join(extract_to, f["path"]))
                    except:
                        self.delete_file(os.path.join(extract_to, f["path"]))
                        os.rename(os.path.join(self.env.config_manager["path"]["temp_path"], f["arch_filename"]), os.path.join(extract_to, f["path"]))

        return data

    def get_dirs_for_file(self, file, relative=None):
        dirs = {}
        if relative != None:
            dirs_f = utils.relative(file, relative).split("\\")[:-1]
        else:
            dirs_f = file.split("\\")[:-1]
        for i in range(len(dirs_f)):
            p = "\\".join(dirs_f[:i+1])
            if p not in dirs:
                if relative != None:
                    dirs[os.path.join(relative, p)] = 1
                else:
                    dirs[p] = 1
        
        return list(dirs.keys())

    def set_modification_time(self, path, time):
        os.utime(path, (time, time))

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

    def mkdir(self, path):
        try: os.mkdir(path)
        except: pass    
    
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
        
    def delete_files(self, files):
        for f in files:
            self.delete_file(f)