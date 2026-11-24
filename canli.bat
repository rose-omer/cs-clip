@echo off
rem Oynarken kaydeder: canli.bat (izle) | canli.bat kur | canli.bat kes <demo>
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (echo Once kur.bat calistir. & pause & exit /b 1)
if "%~1"=="" (.venv\Scripts\python canli.py izle) else (.venv\Scripts\python canli.py %*)
pause
