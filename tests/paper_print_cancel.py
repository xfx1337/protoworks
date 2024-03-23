import tempfile
import win32api
import sys
import win32print

printer_name = win32print.GetDefaultPrinter()
printer = win32print.OpenPrinter(printer_name)

win32print.EndDocPrinter(printer)