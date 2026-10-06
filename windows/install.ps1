# 이 폴더(digest.py, view.py, daily_check.ps1이 들어있는 폴더)에서 실행하세요.
# 우클릭 > PowerShell로 실행, 또는:
#   powershell -ExecutionPolicy Bypass -File install.ps1

$dir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1) 로그온 시 + 30분마다(하루 종일 반복) daily_check.ps1 실행하는 예약 작업 등록
#    -> 로그인 순간, 그리고 절전 후 깨어난 뒤 30분 이내에 6시 이후면 자동 실행됨
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$dir\daily_check.ps1`""
$logonTrigger = New-ScheduledTaskTrigger -AtLogOn
$repeatTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration ([TimeSpan]::MaxValue)

Register-ScheduledTask -TaskName "NewsDigest" -Action $action `
    -Trigger @($logonTrigger, $repeatTrigger) `
    -Description "AI/IT 뉴스 다이제스트: 오전 6시 이후 로그인/주기 체크" -Force | Out-Null

# 2) PowerShell 프로필에 '뉴스' 명령어 등록 (mac의 alias 뉴스='...' 와 동일 역할)
if (-not (Test-Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force | Out-Null
}
$aliasLine = "function 뉴스 { python `"$dir\view.py`" }"
if (-not (Select-String -Path $PROFILE -Pattern "function 뉴스" -Quiet -ErrorAction SilentlyContinue)) {
    Add-Content -Path $PROFILE -Value "`n$aliasLine"
}

Write-Host "설치 완료. PowerShell을 새로 열고 '뉴스'라고 입력해 보세요."
Write-Host "(python이 PATH에 없다면 python.org에서 설치 시 'Add python.exe to PATH' 체크 필요)"
