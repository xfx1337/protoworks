PROTOWORKS_VERSION = "0.1"
PROTOWORKS_FILETYPES_VERSION = "0.1"

PROJECT_IN_WORK = 0
PROJECT_DONE = 1

ACTION_SYNC_ALL_NEW_FILES = 0
ACTION_OVERRIDE_SERVER_FILES = 1
ACTION_OVERRIDE_CLIENT_FILES = 2
ACTION_SEND_ONLY_NEW_FILES_FROM_SERVER = 3
ACTION_SEND_ONLY_NEW_FILES_FROM_CLIENT = 4
ACTION_SEND_ONLY_EDITED_FILES_FROM_SERVER = 5
ACTION_SEND_ONLY_EDITED_FILES_FROM_CLIENT = 6

ACTION_TRANSLATIONS = {
    ACTION_SYNC_ALL_NEW_FILES: "Синхронизация",
    ACTION_OVERRIDE_SERVER_FILES: "Перезапись серверной директории",
    ACTION_OVERRIDE_CLIENT_FILES: "Перезапись локальной директории",
    ACTION_SEND_ONLY_NEW_FILES_FROM_SERVER: "Получение новых файлов с сервера",
    ACTION_SEND_ONLY_NEW_FILES_FROM_CLIENT: "Отправление новых файлов на сервер",
    ACTION_SEND_ONLY_EDITED_FILES_FROM_SERVER: "Получение измененных файлов с сервера",
    ACTION_SEND_ONLY_EDITED_FILES_FROM_CLIENT: "Отправление измененных файлов на сервер"
    }

BIG_FILE_SIZE = 10*1024*1024 # bytes
CHUNK_SIZE = 5120

CUR_CLIENT = 0
SERVER = 1
FILE = 0
FOLDER = 1

STL = 0
KOMPAS_PART = 1
KOMPAS_ASSEMBLY = 2
KOMPAS_FRAGMENT = 3
KOMPAS_BLUEPRINT = 4
GCODE = 5
SOLID_PART = 6
SOLID_ASSEMBLY = 7
SOLID_FRAGMENT = 8
SOLID_BLUEPRINT = 9
DXF = 10
DWG = 11
PDF = 12

FILE_FORMATS = {
    STL: "stl",
    KOMPAS_PART: "m3d",
    KOMPAS_ASSEMBLY: "a3d",
    KOMPAS_FRAGMENT: "frw",
    KOMPAS_BLUEPRINT: "NOT_IMPLEMENTED",
    GCODE: "gcode",
    SOLID_PART: "sldprt",
    SOLID_ASSEMBLY: "sldasm",
    SOLID_FRAGMENT: "NOT_IMPLEMENTED",
    SOLID_BLUEPRINT: "NOT_IMPLEMENTED",
    DXF: "dxf",
    DWG: "dwg",
    PDF: "pdf"
}

DETAILS_DIRS = [
    "stl - Печать",
    "m3d - КОМПАС-Деталь",
    "a3d - КОМАПС-Сборка",
    "frw - КОМПАС-Фрагмент",
    "NOT_IMPLEMENTED - КОМПАС-Чертёж",
    "gcode - Принтер-Код",
    "nc - Фрезер-Код",
    "sldprt - SOLID-Деталь",
    "sldasm - SOLID-Сборка",
    "NOT_IMPLEMENTED - SOLID-Фрагмент",
    "NOT_IMPLEMENTED - SOLID-Чертёж",
    "dxf - Графика",
    "dwg - Графика",
    "pdf - Документация", 
]

DXF_VERSION = {
    "AC1015": "AutoCAD 2000",
    "AC1018": "AutoCAD 2004",
    "AC1021": "AutoCAD 2007",
    "AC1024": "AutoCAD 2010",
    "AC1027": "AutoCAD 2013",
    "AC1032": "AutoCAD 2018"

}

def format_by_file(file):
    if type(file) == type(str()):
        frt = file.split(".")[-1]
    elif type(file) == type(dict()):
        if "path" in file:
            frt = file["path"].split(".")[-1]
        elif "file" in file:
            frt = file["file"]["path"].split(".")[-1]
    else:
        frt = file.path.split(".")[-1]
    
    if frt in FILE_FORMATS.values():
        return list(FILE_FORMATS.keys())[list(FILE_FORMATS.values()).index(frt)]


MATERIAL_TECH_TASK = 0
MATERIAL_MEDIA = 1