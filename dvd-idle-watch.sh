#!/usr/bin/env bash
# Launches DVD screensaver after 5 min idle, kills it on activity

IDLE_THRESHOLD=10000    # 10 seconds in ms
POLL_INTERVAL=10        # seconds between checks
SCREENSAVER="/home/deveshb/Desktop/dvd-screensaver/dvd_screensaver.py"

saver_pid=""
active=false

get_idle_ms() {
  qdbus6 org.kde.screensaver /ScreenSaver org.freedesktop.ScreenSaver.GetSessionIdleTime 2>/dev/null
}

open_screensaver() {
  python3 "$SCREENSAVER" &
  saver_pid=$!
  active=true
}

close_screensaver() {
  if [ -n "$saver_pid" ] && kill -0 "$saver_pid" 2>/dev/null; then
    kill "$saver_pid" 2>/dev/null
  fi
  saver_pid=""
  active=false
}

while true; do
  idle=$(get_idle_ms)

  if [ -z "$idle" ]; then
    sleep "$POLL_INTERVAL"
    continue
  fi

  if [ "$idle" -ge "$IDLE_THRESHOLD" ] && [ "$active" = false ]; then
    open_screensaver
  elif [ "$idle" -lt "$IDLE_THRESHOLD" ] && [ "$active" = true ]; then
    close_screensaver
  fi

  sleep "$POLL_INTERVAL"
done
