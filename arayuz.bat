@echo off
rem cs-klip arayuzu: tarayicida demo istatistikleri ve klipler.
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (echo Once kur.bat calistir. & pause & exit /b 1)
.venv\Scripts\python arayuz.py %*
if errorlevel 1 pause
