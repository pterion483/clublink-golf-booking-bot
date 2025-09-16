#!/bin/bash
#
# Comprehensive Log Monitor for Golf Booking System
# This script monitors all logs and provides detailed debugging information
#

LOG_DIR="/home/dmin1/Golf Tee Times Bot/logs"
TODAY=$(date +%Y%m%d)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Golf Booking System - Log Monitor"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

# Function to check if file exists and show last lines
check_log() {
    local log_file="$1"
    local description="$2"

    echo -e "${BLUE}Checking: $description${NC}"
    echo "File: $log_file"

    if [ -f "$log_file" ]; then
        echo -e "${GREEN}✓ Log exists${NC}"
        echo "Size: $(du -h "$log_file" | cut -f1)"
        echo "Last modified: $(stat -c %y "$log_file" | cut -d' ' -f1,2)"
        echo "Last 10 lines:"
        echo "---"
        tail -10 "$log_file" | sed 's/^/  /'
        echo "---"
    else
        echo -e "${YELLOW}⚠ Log not found (will be created when cron runs)${NC}"
    fi
    echo ""
}

# 1. Check pre-staging log
echo -e "${YELLOW}=== PRE-STAGING LOG (6:25 AM) ===${NC}"
check_log "$LOG_DIR/claude_prestage_$TODAY.log" "Pre-staging execution log"

# 2. Check booking log
echo -e "${YELLOW}=== BOOKING LOG (6:30 AM) ===${NC}"
check_log "$LOG_DIR/claude_booking_$TODAY.log" "Main booking execution log"

# 3. Check combined MCP log
echo -e "${YELLOW}=== COMBINED MCP LOG ===${NC}"
check_log "$LOG_DIR/claude_mcp_$TODAY.log" "Combined Claude MCP log"

# 4. Check gap finder log
echo -e "${YELLOW}=== GAP FINDER LOG ===${NC}"
check_log "$LOG_DIR/gap_finder_$TODAY.log" "Morning gap finder log"

# 5. Check for any error messages
echo -e "${YELLOW}=== ERROR CHECK ===${NC}"
echo "Searching for errors in all logs..."
if grep -i "error\|fail\|exception\|critical" "$LOG_DIR"/*_$TODAY.log 2>/dev/null; then
    echo -e "${RED}⚠ Errors found in logs!${NC}"
else
    echo -e "${GREEN}✓ No errors found${NC}"
fi
echo ""

# 6. Check cron execution
echo -e "${YELLOW}=== CRON EXECUTION CHECK ===${NC}"
echo "Last 5 cron executions for golf booking:"
grep -a "claude_mcp\|gap_finder" /var/log/syslog 2>/dev/null | tail -5
echo ""

# 7. Check if scripts were executed today
echo -e "${YELLOW}=== EXECUTION STATUS ===${NC}"
if [ -f "$LOG_DIR/claude_prestage_$TODAY.log" ]; then
    echo -e "${GREEN}✓ Pre-staging was executed today${NC}"
    grep "PRE-STAGING PHASE STARTED" "$LOG_DIR/claude_prestage_$TODAY.log" | tail -1
else
    echo -e "${YELLOW}⚠ Pre-staging not yet executed today${NC}"
fi

if [ -f "$LOG_DIR/claude_booking_$TODAY.log" ]; then
    echo -e "${GREEN}✓ Booking was executed today${NC}"
    grep "BOOKING PHASE STARTED" "$LOG_DIR/claude_booking_$TODAY.log" | tail -1
else
    echo -e "${YELLOW}⚠ Booking not yet executed today${NC}"
fi
echo ""

# 8. Show prompt files
echo -e "${YELLOW}=== PROMPT FILES ===${NC}"
if [ -f "/home/dmin1/Golf Tee Times Bot/current_claude_prompt.txt" ]; then
    echo "Current prompt file exists:"
    echo "Size: $(wc -l < "/home/dmin1/Golf Tee Times Bot/current_claude_prompt.txt") lines"
    echo "First 5 lines:"
    head -5 "/home/dmin1/Golf Tee Times Bot/current_claude_prompt.txt" | sed 's/^/  /'
else
    echo "No current prompt file"
fi
echo ""

# 9. Check screenshots
echo -e "${YELLOW}=== SCREENSHOTS ===${NC}"
if ls "/home/dmin1/Golf Tee Times Bot/screenshots"/*$TODAY* 2>/dev/null; then
    echo -e "${GREEN}✓ Screenshots found for today${NC}"
else
    echo "No screenshots for today yet"
fi
echo ""

# 10. Summary
echo -e "${BLUE}=========================================="
echo "SUMMARY"
echo "==========================================${NC}"
echo "Current time: $(date '+%H:%M:%S')"
echo "Next pre-staging: Tomorrow 6:25 AM"
echo "Next booking: Tomorrow 6:30 AM"
echo ""
echo "To watch logs live:"
echo "  tail -f \"$LOG_DIR/claude_booking_$TODAY.log\""
echo ""
echo "To see all today's logs:"
echo "  ls -la \"$LOG_DIR\"/*$TODAY*"
echo "=========================================="