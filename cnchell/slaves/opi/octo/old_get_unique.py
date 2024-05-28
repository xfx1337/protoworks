# def get_unique_machine_data(port):
#     def clear_string(s): # fuck it
#         return s.rstrip().replace("\n", "").replace("\r", "").replace("\\n", "").replace("\'b", "").replace("\\'", "").replace("\'", "").replace('"', "")

#     process = subprocess.Popen(f"udevadm info -q all -n {port} --attribute-walk", shell=True, stdout=subprocess.PIPE)
#     out = ""
#     for line in process.stdout:
#         out += str(line)
#     process.wait()

#     found = re.findall("ATTRS\{idProduct\}==(.*?)ATTRS", out)

#     groups = []

#     for i in range(len(found)):
#         groups.append({})
#         groups[i]["idProduct"] = clear_string(found[i])

#     found = re.findall("ATTRS\{idVendor\}==(.*?)ATTRS", out)
#     for i in range(len(found)):
#         groups[i]["idVendor"] = clear_string(found[i])

#     # found = re.findall("ATTRS\{devpath\}==(.*?)ATTRS", out)
#     # for i in range(len(found)):
#     #     groups[i]["devpath"] = clear_string(found[i])

#     return groups