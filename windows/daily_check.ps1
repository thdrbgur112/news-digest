# 6시 이후 깨어난 첫 순간(또는 30분 주기)에 실행되지만, 하루 한 번만 digest 실행
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $dir

$hour = (Get-Date).Hour
$today = (Get-Date).ToString("yyyy-MM-dd")
$stateFile = Join-Path $dir ".last_run"

if ($hour -lt 6) { exit }
if ((Test-Path $stateFile) -and ((Get-Content $stateFile -Raw).Trim() -eq $today)) { exit }

python digest.py
Set-Content -Path $stateFile -Value $today -NoNewline
