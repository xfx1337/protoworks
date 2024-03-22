import tempfile
import win32api
import sys
import win32print

filename = tempfile.mktemp (".txt")
open (filename, "w").write ("ProtoWorks")
win32api.ShellExecute (
  0,
  "printto",
  filename,
  '"%s"' % win32print.GetDefaultPrinter (),
  ".",
  0
)
