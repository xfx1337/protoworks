import os
import json
import configparser

cura_path = "C:\\Program Files\\Ultimaker Cura 5.2.1\\"
cura_engine_path = os.path.join(cura_path, "CuraEngine.exe")

machine_settings_file = "C:\\Program Files\\Ultimaker Cura 5.2.1\\share\\cura\\resources\\definitions\\flsun_qq.def.json"
extruder_settings_file = "flsun_qq_s_extruder_0.def.json"
quality_settings_file = "extra_fast.inst.cfg"

input_file = "test_cube.stl"
output_file = "2706.gcode"

config = configparser.ConfigParser()
config.read(quality_settings_file)

additional_settings = []

for s in config["values"].keys():
    additional_settings.append([s, config["values"][s]])

with open(extruder_settings_file) as f:
    extruder = json.load(f)

for value in extruder["overrides"].keys():
    additional_settings.append([value, extruder["overrides"][value]["default_value"]])


cmd = f'"{cura_engine_path}"' + " slice -v -p -j " + f'"{machine_settings_file}"' + " -l " + input_file + " -o " + output_file + " -s "
for s in additional_settings:
    cmd += f"{s[0]}={s[1]} "

print(cmd)