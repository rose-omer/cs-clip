@echo off
rem cs-klip tam otomatik: yeni demolari izler, CS2 ve FACEIT kapaliyken sirayla kaydeder.
rem FACEIT indirme icin: otomatik.bat --faceit-dk 10  (ayarlar.json -> faceit_api_anahtari gerekir)
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (echo Once kur.bat calistir. & pause & exit /b 1)
.venv\Scripts\python otomatik.py izle %*
pause
