#!/bin/bash
# 6시 이후 깨어난 첫 순간(또는 30분 주기)에 실행되지만, 하루 한 번만 digest 실행
cd "$(dirname "$0")" || exit 1

/usr/bin/python3 welcome_new_subscribers.py

HOUR=$(date +%H)
TODAY=$(date +%Y-%m-%d)
STATE=.last_run

if [ "$HOUR" -lt 6 ]; then
  exit 0
fi
if [ -f "$STATE" ] && [ "$(cat "$STATE")" = "$TODAY" ]; then
  exit 0
fi

/usr/bin/python3 digest.py
echo "$TODAY" > "$STATE"
