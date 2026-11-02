@echo off
rem Demo dosyasini bu dosyanin uzerine surukle-birak ya da: klip.bat <demo> [--prova] [--sadece-analiz]
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (echo Once kur.bat calistir. & pause & exit /b 1)
.venv\Scripts\python klip.py %*
pause
