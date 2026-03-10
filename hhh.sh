#!/bin/bash
# HHH Bot Management Script

PID_FILE="bot.pid"
LOG_FILE="bot.log"

case "$1" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "Bot is already running (PID: $(cat $PID_FILE))"
            exit 1
        fi
        echo "Starting HHH Bot..."
        nohup uv run python src/bot/main.py > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "Started successfully. PID: $(cat $PID_FILE)"
        ;;
    stop)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "Stopping HHH Bot (PID: $(cat $PID_FILE))..."
            kill -15 $(cat "$PID_FILE")
            rm "$PID_FILE"
            echo "Stopped."
        else
            echo "Bot is not running."
        fi
        ;;
    status)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "🟢 Bot is RUNNING (PID: $(cat $PID_FILE))"
            echo "--- Last 5 log entries ---"
            tail -n 5 "$LOG_FILE"
        else
            echo "🔴 Bot is STOPPED."
        fi
        ;;
    logs)
        tail -f "$LOG_FILE"
        ;;
    *)
        echo "Usage: ./hhh.sh {start|stop|status|logs}"
        exit 1
        ;;
esac
