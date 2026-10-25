@echo off
cd /d "%~dp0"
py -m pip install -r requirements.txt
if errorlevel 1 goto fail
py main.py --show
if errorlevel 1 goto fail
pause
exit /b 0
:fail
echo Run failed. See the error above.
pause
exit /b 1
