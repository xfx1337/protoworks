import os, sys
import json
import ctypes

file_read = sys.argv[1]

d = {}
with open(file_read, encoding="utf-8") as f:
    d = json.load(f)

zip_path = d["zip_path"]
import zipfile



def unzip_archive(path, linkers):
    data = ""
    with zipfile.ZipFile(path, 'r') as archive:
        for f in linkers:
            archive.extract(f["arch_filename"], d["temp_path"])
            print(f["path"])
            try:
                os.rename(os.path.join(d["temp_path"], f["arch_filename"]), f["path"])
            except:
                os.remove(f["path"])
                os.rename(os.path.join(d["temp_path"], f["arch_filename"]), f["path"])

print(f"extracting {zip_path}")
unzip_archive(zip_path, d["linkers"])
print("done")