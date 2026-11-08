# Ancient onarim denemesi: bayat komutu temizlenmis demoyu CS2'de kaydetmeyi dener.
# Mac bittikten sonra calistir:  powershell -ExecutionPolicy Bypass -File araclar\ancient_test.ps1
# CS2 ya da FACEIT aciksa hicbir sey kapatmaz, sadece uyarip cikar.
param(
    [string]$Demo = "$env:USERPROFILE\Downloads\1-3dd3d912-c5a5-4560-8de4-8a19d114ecf2-1-1.dem",
    [int]$EnIyi = 3
)
$ErrorActionPreference = "Stop"
$kok = Split-Path $PSScriptRoot -Parent
$py = Join-Path $kok ".venv\Scripts\python.exe"

$acik = Get-Process cs2, faceitclient, faceitservice -ErrorAction SilentlyContinue
if ($acik) {
    Write-Host "Acik: $(($acik | ForEach-Object Name | Sort-Object -Unique) -join ', '). Once bunlari kendin kapat, sonra tekrar calistir."
    exit 1
}
if (-not (Test-Path $Demo)) { Write-Host "Demo yok: $Demo"; exit 1 }

$onarilmis = $Demo -replace '\.dem$', '.onarilmis.dem'
Write-Host "1) Onarim: $Demo"
& $py (Join-Path $kok "araclar\demo_onar.py") $Demo --cikti $onarilmis
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if (-not (Test-Path $onarilmis)) { Write-Host "Bayat komut yok; bu demo icin onarim gerekmiyor."; exit 0 }

Write-Host "2) Kayit (en iyi $EnIyi klip): $onarilmis"
$log = Join-Path $kok "ancient_test.log"
Push-Location $kok
try {
    & $py klip.py $onarilmis --en-iyi $EnIyi 2>&1 | Tee-Object -FilePath $log
    $kod = $LASTEXITCODE
} finally { Pop-Location }

$cikti = Get-Content $log -Raw
if ($cikti -match "Game error|Zaman a") {
    Write-Host "SONUC: onarilmis demo da kaydedilemedi. Gunluk: $log"
    exit 2
}
Write-Host "SONUC: kayit tamamlandi (cikis kodu $kod). Klipler klipler\ klasorunde, gunluk: $log"
