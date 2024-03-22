import subprocess

def command_print(event = None):
    command = "{} {}".format('D:\\ProtoWorks\\server\\sw_requirements\\PDFtoPrinter.exe','D:\\ProtoWorksData\\Projects\\123\\МАТЕРИАЛЫ-PW\\latin.pdf')
    subprocess.call(command,shell=True)

command_print()