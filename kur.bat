@echo off
rem cs-klip kurulumu: tek tikla. Tekrar calistirmak guvenli; kurulu olan adimlar atlanir.
rem Python yoksa winget ile Python 3.12 kurar, gerisini kurulum.py yapar:
rem sanal ortam, paketler, ayarlar.json, FFmpeg, PostgreSQL, CS Demo Manager, CSDM ayarlari, PATH, testler.
rem Kullanim: kur.bat [--prova] [--oyuncu AD] [--test-yok]     (--prova: hicbir seyi degistirmez)
setlocal
chcp 65001 >nul
cd /d "%~dp0"

call :python_bul
if defined PY goto calistir

if /i "%~1"=="--prova" (
    echo [prova] Python 3.11+ bulunamadi: winget install Python.Python.3.12 calistirilacak.
    goto son
)
echo Python bulunamadi. winget ile Python 3.12 kuruluyor...
where winget >nul 2>nul || (echo [HATA] winget yok. Microsoft Store'dan "Uygulama Yukleyici" kur ya da python.org'dan Python 3.12 kur. & goto son)
winget install --id Python.Python.3.12 -e --silent --accept-package-agreements --accept-source-agreements
call :python_bul
if not defined PY (echo [HATA] Python kuruldu ama bulunamadi. Bu pencereyi kapatip kur.bat'i yeniden calistir. & goto son)

:calistir
%PY% kurulum.py %*
set "SONUC=%errorlevel%"
echo.
pause
exit /b %SONUC%

:son
echo.
pause
exit /b 1

rem --- Python 3.11+ ara: sanal ortam, py launcher, PATH, winget'in kurdugu yerler ---
:python_bul
set "PY="
set "SURUM=import sys; sys.exit(sys.version_info < (3, 11))"
if exist ".venv\Scripts\python.exe" (".venv\Scripts\python.exe" -c "%SURUM%" >nul 2>nul && set PY=".venv\Scripts\python.exe")
if defined PY exit /b 0
py -3.12 -c "%SURUM%" >nul 2>nul && set "PY=py -3.12"
if defined PY exit /b 0
py -3 -c "%SURUM%" >nul 2>nul && set "PY=py -3"
if defined PY exit /b 0
python -c "%SURUM%" >nul 2>nul && set "PY=python"
if defined PY exit /b 0
for %%P in ("%LOCALAPPDATA%\Programs\Python\Python312\python.exe" "%ProgramFiles%\Python312\python.exe") do (
    if not defined PY if exist %%P set PY=%%P
)
exit /b 0
