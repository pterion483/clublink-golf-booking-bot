#!/bin/bash
# Monitor cron execution for golf booking system

LOG_DIR="/home/dmin1/Golf Tee Times Bot/logs"
CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")
TODAY=$(date +%Y%m%d)

echo "========================================"
echo "CRON MONITORING REPORT"
echo "Current Time: $CURRENT_TIME"
echo "========================================"

# Check if cron service is running
echo -e "\n[CRON SERVICE STATUS]"
if ps aux | grep -q "[c]ron"; then
    echo "✓ Cron service is running"
    ps aux | grep "[c]ron"
else
    echo "✗ Cron service is NOT running!"
    echo "Run: sudo service cron start"
fi

# Check recent cron executions
echo -e "\n[RECENT CRON EXECUTIONS - Last 15 minutes]"
FIFTEEN_MIN_AGO=$(date -d "15 minutes ago" "+%Y-%m-%d %H:%M")
echo "Looking for executions since: $FIFTEEN_MIN_AGO"

# Check Claude executor logs
if [ -f "$LOG_DIR/claude_executor_${TODAY}.log" ]; then
    echo -e "\nClaude Executor Activity:"
    tail -20 "$LOG_DIR/claude_executor_${TODAY}.log"
else
    echo "No Claude executor logs found today"
fi

# Check cron Claude gap logs
if [ -f "$LOG_DIR/cron_claude_gap_${TODAY}.log" ]; then
    echo -e "\nCron Gap Finder Activity:"
    tail -10 "$LOG_DIR/cron_claude_gap_${TODAY}.log"
else
    echo "No cron gap finder logs found today"
fi

# Check manual gap execution
if ls "$LOG_DIR"/manual_gap_*.log 2>/dev/null | head -1 > /dev/null; then
    echo -e "\nManual Gap Finder Activity:"
    ls -lt "$LOG_DIR"/manual_gap_*.log | head -3
fi

# Next scheduled runs
echo -e "\n[NEXT SCHEDULED RUNS]"
CURRENT_MIN=$(date +%M)
NEXT_15=$((((CURRENT_MIN / 15) + 1) * 15))
if [ $NEXT_15 -ge 60 ]; then
    NEXT_15=0
    NEXT_HOUR=$(($(date +%H) + 1))
else
    NEXT_HOUR=$(date +%H)
fi
printf "Next gap finder run: %02d:%02d (every 15 min during 6 AM - 9 PM)\n" $NEXT_HOUR $NEXT_15

# Check if prompt files exist
echo -e "\n[PROMPT FILES]"
if [ -f "/home/dmin1/Golf Tee Times Bot/current_gap_finder_prompt.txt" ]; then
    echo "✓ Gap finder prompt exists ($(stat -c %y "/home/dmin1/Golf Tee Times Bot/current_gap_finder_prompt.txt" | cut -d. -f1))"
else
    echo "✗ Gap finder prompt missing"
fi

if [ -f "/home/dmin1/Golf Tee Times Bot/current_claude_prompt.txt" ]; then
    echo "✓ Booking prompt exists ($(stat -c %y "/home/dmin1/Golf Tee Times Bot/current_claude_prompt.txt" | cut -d. -f1))"
else
    echo "- Booking prompt not found (generated at 6:30 AM)"
fi

echo -e "\n========================================"