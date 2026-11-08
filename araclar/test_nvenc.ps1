# Ayni round'u once x264 (islemci), sonra NVENC (ekran karti) ile kaydedip sureleri olcer.
$csdm = 'C:\Users\koseo\AppData\Local\Programs\cs-demo-manager\csdm.cmd'
$dl = 'C:\Users\koseo\Downloads'
$demo = "$dl\1-59cf10f2-9122-41c4-89bc-2b28c64e0637-1-1.dem"
$env:Path += ';C:\Program Files\PostgreSQL\17\bin'
$ortak = @('video', $demo, '--mode', 'player', '--steamids', '76561198963443734', '--event', 'kills', '--rounds', '20,22',
    '--start-seconds-before', '5', '--end-seconds-after', '3', '--no-concatenate-sequences', '--recording-system', 'CS',
    '--close-game-after-recording')
$sonuc = @()

foreach ($t in @(
    @{ Ad = 'nvenc'; Ek = @('--ffmpeg-video-codec', 'h264_nvenc', '--ffmpeg-output-parameters=-preset p5 -rc vbr -cq 21 -b:v 0') }
)) {
    Write-Host "=== $($t.Ad) ==="
    $basla = Get-Date
    $ilkDonusum = $null
    & $csdm @ortak @($t.Ek) 2>&1 | ForEach-Object {
        if (-not $ilkDonusum -and "$_" -like 'Converting*') { $ilkDonusum = Get-Date }
        Write-Host $_
    }
    $bitis = Get-Date
    $dosyalar = Get-ChildItem $dl -Filter 'sequence-*.mp4' | Where-Object LastWriteTime -gt $basla
    New-Item -ItemType Directory -Force "$dl\nvenc-test\$($t.Ad)" | Out-Null
    $dosyalar | Move-Item -Destination "$dl\nvenc-test\$($t.Ad)" -Force
    $sonuc += [pscustomobject]@{
        Kodlayici = $t.Ad
        ToplamSn = [int]($bitis - $basla).TotalSeconds
        DonusumSn = if ($ilkDonusum) { [int]($bitis - $ilkDonusum).TotalSeconds } else { -1 }
        Parca = @($dosyalar).Count
        MB = [math]::Round((($dosyalar | Measure-Object Length -Sum).Sum / 1MB), 1)
    }
    Start-Sleep 5
}
$sonuc | Format-Table -AutoSize
$sonuc | ConvertTo-Json | Set-Content "$dl\nvenc-test\sonuc-nvenc.json"
