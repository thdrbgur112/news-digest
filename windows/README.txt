[친구 노트북 설치 순서]

1. Python 3 설치 (python.org/downloads) — 설치 화면에서
   "Add python.exe to PATH" 체크박스 꼭 체크.

2. 이 폴더(news-digest 등 원하는 이름으로 통째로) 아무 곳에나 복사.

3. 폴더 안에서 PowerShell 열고 아래 실행:
       powershell -ExecutionPolicy Bypass -File install.ps1

   -> 로그온/30분마다(오전 6시 이후, 하루 1회) 자동으로 뉴스 수집 + 알림 뜨는
      예약 작업이 등록되고, PowerShell에서 '뉴스'라고 치면 정리된 목록이
      뜨도록 설정됩니다.

4. PowerShell 새로 열고 '뉴스' 입력해서 확인.
   (그날 처음 실행 전이면 "아직 오늘자 다이제스트가 없습니다" 나올 수 있음
    -> python digest.py 한 번 직접 실행해서 즉시 생성 가능)

[제거하려면]
   Unregister-ScheduledTask -TaskName "NewsDigest" -Confirm:$false
