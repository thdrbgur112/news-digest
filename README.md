# news-digest

매일 아침 AI/IT 뉴스(OpenAI·Anthropic 블로그, AI타임스, GeekNews, TechCrunch AI, Google 뉴스)를 RSS로 모아 한국어로 번역·요약하고 텔레그램으로 보내는 봇. 표준 라이브러리만 사용합니다.

## 구성
- `digest.py` — RSS 수집 → 번역 → `digests/YYYY-MM-DD.md` 저장 → 텔레그램 전송
- `telegram_send.py` / `telegram_setup.py` — 봇 전송, 최초 chat_id 설정. 봇에게 말을 건 사람은 자동 구독자로 등록
- `welcome_new_subscribers.py` — 신규 구독자 환영 메시지
- `wake_check.sh` — 오전 6시 이후 첫 실행 시 하루 한 번만 digest 실행 (launchd로 30분마다 호출)
- `view.py` — 터미널에서 오늘 뉴스 보기
- `windows/` — Windows용 (작업 스케줄러 + PowerShell `뉴스` 명령)

## 사용
```bash
python3 telegram_setup.py   # BotFather 토큰 입력 -> telegram_config.json 생성(커밋 금지)
python3 digest.py
```
`telegram_config.json` 형식: `{"bot_token": "...", "chat_ids": []}`
