@echo off
cd cnchell\client\additional\fake_octo_server
set /p "port=Enter port: "
set /p "id=Enter machine id: "
set /p "username=Enter username: "
set /p "password=Enter password: "
python main.py %port% %id% "C:\Users\DumbOS\Documents\work\git\protoworks\cnchell\client\config.ini" %username% %password%
pause