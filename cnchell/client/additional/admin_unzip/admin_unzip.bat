echo off
cd /D "%~dp0"
set arg1=%1
python admin_unzip.py %1
pause