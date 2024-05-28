from functools import reduce

def checksum(command):
    return reduce(lambda x, y: x ^ y, map(ord, command))

def convert(command, lineno):
    prefix = "N" + str(lineno) + " " + command
    command = prefix + "*" + str(checksum(prefix))
    return command