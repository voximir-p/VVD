@echo off
echo [1] Use Voximir's Video Downloader
echo [2] Update packages (Use when you encounter an error)

choice /c 12 /m "Enter your choice:"

cls

if errorlevel 2 goto update
if errorlevel 1 goto start

:start
.\.venv\Scripts\python.exe main.py
exit

:update
.\.venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
exit
