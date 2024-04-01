PROTOWORKS_VERSION = "0.1"
PROTOWORKS_FILETYPES_VERSION = "0.1"

INVALID_REQUEST_ASNWER = ("Invalid request", 400)
AUTH_ERROR = ("Invalid auth", 302)

PROJECT_IN_WORK = 0
PROJECT_DONE = 1

CLIENT = 0
SERVER = 1
FILE = 0
FOLDER = 1

MATERIAL_TECH_TASK = 0
MATERIAL_MEDIA = 1

DETAILS_DIRS = [
    "stl - Печать",
    "m3d - КОМПАС-Деталь",
    "a3d - КОМПАС-Сборка",
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
NC = 13

FILE_FORMATS = {
    STL: "stl",
    KOMPAS_PART: "m3d",
    KOMPAS_ASSEMBLY: "a3d",
    KOMPAS_FRAGMENT: "frw",
    KOMPAS_BLUEPRINT: "cdw",
    GCODE: "gcode",
    SOLID_PART: "sldprt",
    SOLID_ASSEMBLY: "sldasm",
    SOLID_FRAGMENT: "NOT_IMPLEMENTED",
    SOLID_BLUEPRINT: "NOT_IMPLEMENTED",
    DXF: "dxf",
    DWG: "dwg",
    PDF: "pdf",
    NC: "nc"
}

PART_DONE = 0 # done
PART_PRODUCTION = 1 # printing/milling
PART_IN_WORK = 2 # cad
PART_IN_COORDINATION = 3 # waiting