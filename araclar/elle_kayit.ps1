# CSDM'siz kayit / tani: CS2'yi dogrudan -condebug ile acip demoyu oynatir, konsol komutlarini yazdirir.
# CSDM'de takilan bir parcanin CS2 tarafinda nerede durdugunu gormek (game\csgo\console.log) ya da
# parcayi elle kaydetmek icin.
#   powershell -ExecutionPolicy Bypass -File araclar\elle_kayit.ps1 -Demo <demo.dem> -Baslangic 61512 -Bitis 61832
# CS2 ya da FACEIT aciksa hicbir sey kapatmaz, uyarip cikar.
# Not: CS2'de belirli bir tick'te komut calistirmanin yolu yok (CSDM eklentisi ya da HLAE mirv_cmd gerekir),
# netcon de calismiyor; bu yuzden komutlar konsola elle yazilir.
param(
    [Parameter(Mandatory = $true)][string]$Demo,
    [Parameter(Mandatory = $true)][int]$Baslangic,
    [Parameter(Mandatory = $true)][int]$Bitis,
    [int]$OncekiPaket = 0  # 1: CS2'yi hedefin bir onceki FullPacket'inden baslat
)
$ErrorActionPreference = "Stop"
$acik = Get-Process cs2, faceitclient, faceitservice -ErrorAction SilentlyContinue
if ($acik) {
    Write-Host "Acik: $(($acik | ForEach-Object Name | Sort-Object -Unique) -join ', '). Once bunlari kendin kapat."
    exit 1
}
if (-not (Test-Path $Demo)) { Write-Host "Demo yok: $Demo"; exit 1 }
$Demo = (Resolve-Path $Demo).Path

$steam = (Get-ItemProperty "HKCU:\Software\Valve\Steam").SteamPath -replace "/", "\"
$oyun = Join-Path $steam "steamapps\common\Counter-Strike Global Offensive\game"
$exe = Join-Path $oyun "bin\win64\cs2.exe"
if (-not (Test-Path $exe)) { Write-Host "cs2.exe yok: $exe"; exit 1 }
$log = Join-Path $oyun "csgo\console.log"
if (Test-Path $log) { Remove-Item $log }

# CSDM ile ayni atlama: kurulum tick'i baslangic - 64, ondan bir once.
$hedef = $Baslangic - 65
if ($OncekiPaket) { $hedef = [Math]::Max(1, [int]([Math]::Floor(($hedef - 1) / 3840) * 3840 + 1) - 33) }
$sure = [Math]::Round(($Bitis - $Baslangic) / 64, 1)

Write-Host "CS2 aciliyor (-condebug). Demo yuklenince konsola (~) sirayla yaz:"
Write-Host "  demo_ui_mode 0; sv_cheats 1; cl_draw_only_deathnotices 1; tv_listen_voice_indices 0"
Write-Host "  demo_gototick $hedef"
Write-Host "  (oyuncuyu sec: spec_player <slot>)  host_framerate 60"
Write-Host "  demo_gototick $Baslangic; startmovie elle_$Baslangic"
Write-Host "  ~$sure sn sonra: endmovie; host_framerate 0"
Write-Host "Takilirsa CS2'yi kendin kapat; gunluk: $log"
Start-Process -FilePath $exe -ArgumentList @("-insecure", "-novid", "-condebug", "-sw", "-w", "1280", "-h", "720",
    "+playdemo", "`"$Demo`"") -WorkingDirectory (Split-Path $exe)
