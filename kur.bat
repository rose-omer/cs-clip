@echo off
rem cs-klip kurulumu: sanal ortam, paketler, ayar dosyasi, testler.
cd /d "%~dp0"

where py >nul 2>nul || (echo [HATA] Python bulunamadi. python.org'dan Python 3.11+ kur, "py launcher" secili olsun. & pause & exit /b 1)

if not exist .venv (
    echo Sanal ortam olusturuluyor...
    py -3 -m venv .venv || (echo [HATA] venv olusturulamadi. & pause & exit /b 1)
)

echo Paketler kuruluyor...
.venv\Scripts\python -m pip install -q --disable-pip-version-check -r requirements.txt || (echo [HATA] Paket kurulumu basarisiz. & pause & exit /b 1)

if not exist ayarlar.json (
    copy /y ayarlar.ornek.json ayarlar.json >nul
    echo ayarlar.json olusturuldu. OBS sifresini icine yaz.
)

echo Testler calisiyor...
.venv\Scripts\python -m pytest -q || (echo [HATA] Testler gecmedi. Ciktiyi Claude'a gonder. & pause & exit /b 1)

echo.
echo Kurulum tamam.
pause
