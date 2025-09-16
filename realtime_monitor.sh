#!/bin/bash
# Real-time Golf Booking System Monitor

LOG_DIR="/home/dmin1/Golf Tee Times Bot/logs"
TODAY=$(date +%Y%m%d)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

clear
echo "================================================"
echo "   GOLF BOOKING SYSTEM - REAL-TIME MONITOR"
echo "================================================"
echo ""

while true; do
    CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")

    # Position cursor at top
    tput cup 4 0

    echo -e "${GREEN}[SYSTEM STATUS]${NC}"
    echo -e "Current Time: ${YELLOW}$CURRENT_TIME${NC}"
    echo ""

    # Check cron service
    if ps aux | grep -q "[c]ron"; then
        echo -e "Cron Service: ${GREEN}✓ RUNNING${NC}"
    else
        echo -e "Cron Service: ${RED}✗ NOT RUNNING${NC}"
    fi

    # Check Claude processes
    CLAUDE_PROCS=$(ps aux | grep -c "[c]laude_executor")
    if [ $CLAUDE_PROCS -gt 0 ]; then
        echo -e "Claude Executor: ${GREEN}✓ ACTIVE ($CLAUDE_PROCS processes)${NC}"
    else
        echo -e "Claude Executor: ${YELLOW}⊙ IDLE${NC}"
    fi

    echo ""
    echo -e "${GREEN}[NEXT SCHEDULED RUNS]${NC}"
    CURRENT_MIN=$(date +%M)
    CURRENT_HOUR=$(date +%H)

    # Calculate next 15-minute interval
    NEXT_15=$((((CURRENT_MIN / 15) + 1) * 15))
    if [ $NEXT_15 -ge 60 ]; then
        NEXT_15=0
        NEXT_HOUR=$((CURRENT_HOUR + 1))
    else
        NEXT_HOUR=$CURRENT_HOUR
    fi

    printf "Gap Finder:    %02d:%02d:00 (in %d min)\n" $NEXT_HOUR $NEXT_15 $((NEXT_15 - CURRENT_MIN))

    # Next hourly test
    NEXT_TEST=$((CURRENT_HOUR + 1))
    printf "System Test:   %02d:00:00 (in %d min)\n" $NEXT_TEST $((60 - CURRENT_MIN))

    echo ""
    echo -e "${GREEN}[RECENT ACTIVITY - Last 5 min]${NC}"

    # Check recent logs
    if [ -f "$LOG_DIR/claude_executor_${TODAY}.log" ]; then
        FIVE_MIN_AGO=$(date -d "5 minutes ago" "+%H:%M")
        RECENT=$(grep "\[$FIVE_MIN_AGO" "$LOG_DIR/claude_executor_${TODAY}.log" 2>/dev/null | tail -3)
        if [ -n "$RECENT" ]; then
            echo "$RECENT" | head -3
        else
            echo "No activity in last 5 minutes"
        fi
    fi

    echo ""
    echo -e "${GREEN}[LAST EXECUTION]${NC}"
    if [ -f "$LOG_DIR/claude_executor_${TODAY}.log" ]; then
        tail -1 "$LOG_DIR/claude_executor_${TODAY}.log"
    fi

    echo ""
    echo -e "${GREEN}[LOGIN STATUS]${NC}"
    # Check if recent logs show login issues
    if [ -f "$LOG_DIR/cron_claude_gap_${TODAY}.log" ]; then
        if tail -50 "$LOG_DIR/cron_claude_gap_${TODAY}.log" | grep -q "Login Issue\|authentication"; then
            echo -e "${YELLOW}⚠ Login issues detected - Now using adaptive credentials${NC}"
            echo "  Email: Sid.saini1@gmail.com OR Membership: 224816"
        else
            echo -e "${GREEN}✓ Authentication working${NC}"
        fi
    fi

    echo ""
    echo "Press Ctrl+C to exit monitoring"

    sleep 5
done