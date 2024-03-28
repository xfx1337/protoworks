from defines import *

# FILE_FORMATS = {
#     STL: "stl",
#     KOMPAS_PART: "m3d",
#     KOMPAS_ASSEMBLY: "a3d",
#     KOMPAS_FRAGMENT: "frw",
#     KOMPAS_BLUEPRINT: "cdw",
#     GCODE: "gcode",
#     SOLID_PART: "sldprt",
#     SOLID_ASSEMBLY: "sldasm",
#     SOLID_FRAGMENT: "NOT_IMPLEMENTED",
#     SOLID_BLUEPRINT: "NOT_IMPLEMENTED",
#     DXF: "dxf",
#     DWG: "dwg",
#     PDF: "pdf"
# }

CONVERT_WAYS = {
    "stl": [],
    "m3d": ["stl"],
    "a3d": ["m3d", "stl"],
    "frw": ["dxf", "dwg", "pdf"],
    "cdw": ["dxf", "dwg", "pdf"],
    "dxf": ["dwg, pdf"],
    "dwg": ["dxf", "pdf"]
}