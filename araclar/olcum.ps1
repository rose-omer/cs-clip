# CSDM kaydini saniye saniye izler: CS2 acik mi, kac kare yazildi, ffmpeg calisiyor mu.
# Kullanim: olcum.ps1 -Sistem CS|HLAE
param([string]$Sistem = 'CS')
$csdm = 'C:\Users\koseo\AppData\Local\Programs\cs-demo-manager\csdm.cmd'
$dl = 'C:\Users\koseo\Downloads'
$demo = "$dl\1-59cf10f2-9122-41c4-89bc-2b28c64e0637-1-1.dem"
$movie = 'C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\csdm\movie'
$cikti = "$dl\olcum-$Sistem"
New-Item -ItemType Directory -Force $cikti | Out-Null
$env:Path += ';C:\Program Files\PostgreSQL\17\bin'

$argumanlar = "video `"$demo`" --mode player --steamids 76561198963443734 --event kills --rounds 20,22 " +
    "--start-seconds-before 5 --end-seconds-after 3 --no-concatenate-sequences --recording-system $Sistem --close-game-after-recording"
$basla = Get-Date
$p = Start-Process cmd.exe -ArgumentList "/c `"$csdm`" $argumanlar > `"$cikti\csdm.txt`" 2>&1" -PassThru -WindowStyle Hidden

$satirlar = @()
$enCokKare = 0; $enCokMB = 0
while (-not $p.HasExited) {
    $t = [math]::Round(((Get-Date) - $basla).TotalSeconds, 1)
    $cs = [bool](Get-Process cs2 -ErrorAction SilentlyContinue)
    $ff = @(Get-Process ffmpeg -ErrorAction SilentlyContinue).Count
    $kare = 0; $mb = 0
    if (Test-Path $movie) {
        $dosyalar = Get-ChildItem $movie -Recurse -File -ErrorAction SilentlyContinue
        $kare = @($dosyalar | Where-Object Extension -eq '.tga').Count
        $mb = [int](($dosyalar | Measure-Object Length -Sum).Sum / 1MB)
    }
    if ($kare -gt $enCokKare) { $enCokKare = $kare }
    if ($mb -gt $enCokMB) { $enCokMB = $mb }
    $son = (Get-Content "$cikti\csdm.txt" -ErrorAction SilentlyContinue | Select-Object -Last 1)
    $satirlar += [pscustomobject]@{ Sn = $t; CS2 = $cs; FFmpeg = $ff; Kare = $kare; MB = $mb; Durum = $son }
    Start-Sleep -Milliseconds 1000
}
$toplam = [math]::Round(((Get-Date) - $basla).TotalSeconds, 1)
$satirlar | Export-Csv "$cikti\zaman.csv" -NoTypeInformation -Encoding UTF8

# Ozet: her asamanin ilk gorundugu an
function Ilk($kosul) { ($satirlar | Where-Object $kosul | Select-Object -First 1).Sn }
$ozet = [ordered]@{
    Sistem = $Sistem
    ToplamSn = $toplam
    CS2Acildi = Ilk { $_.CS2 }
    IlkKare = Ilk { $_.Kare -gt 0 }
    CS2Kapandi = ($satirlar | Where-Object CS2 | Select-Object -Last 1).Sn
    IlkDonusum = Ilk { $_.Durum -like 'Converting*' }
    EnCokKare = $enCokKare
    EnCokMB = $enCokMB
}
$ozet | ConvertTo-Json | Set-Content "$cikti\ozet.json"
Get-ChildItem $dl -Filter 'sequence-*.mp4' | Where-Object LastWriteTime -gt $basla | Move-Item -Destination $cikti -Force
$ozet
Get-Content "$cikti\csdm.txt"
