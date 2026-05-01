@echo off
setlocal
cd /d %~dp0
python -m pip install -r requirements.txt
pyinstaller --noconfirm --windowed --onefile --name SpaBookingApp app.py
echo Build done. EXE is at dist\SpaBookingApp.exe
endlocal
