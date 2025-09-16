#!/bin/bash
#
# Cron Wrapper for Golf Booking System
# This wrapper adds extensive logging to track cron execution
#

# Set up environment
export PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/home/dmin1/.local/bin
export HOME=/home/dmin1
export USER=dmin1
export CRON=true
export DEBUG=true

# Variables
SCRIPT_DIR="/home/dmin1/Golf Tee Times Bot"
LOG_DIR="$SCRIPT_DIR/logs"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S.%3N')
DATE=$(date +%Y%m%d)
ACTION="$1"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log_message() {
    local message="$1"
    local log_file="$2"
    echo "[$TIMESTAMP] $message" | tee -a "$log_file"
}

# Determine log file based on action
case "$ACTION" in
    prestage)
        LOG_FILE="$LOG_DIR/claude_prestage_$DATE.log"
        EXEC_LOG="$LOG_DIR/cron_prestage_exec_$DATE.log"
        ;;
    book)
        LOG_FILE="$LOG_DIR/claude_booking_$DATE.log"
        EXEC_LOG="$LOG_DIR/cron_booking_exec_$DATE.log"
        ;;
    gap)
        LOG_FILE="$LOG_DIR/gap_finder_$DATE.log"
        EXEC_LOG="$LOG_DIR/cron_gap_exec_$DATE.log"
        ;;
    gap-night)
        LOG_FILE="$LOG_DIR/gap_finder_overnight_$DATE.log"
        EXEC_LOG="$LOG_DIR/cron_gap_night_exec_$DATE.log"
        ;;
    *)
        echo "Usage: $0 {prestage|book|gap|gap-night}"
        exit 1
        ;;
esac

# Log execution start
{
    echo "================================================================"
    echo "CRON EXECUTION STARTED"
    echo "================================================================"
    echo "Timestamp: $TIMESTAMP"
    echo "Action: $ACTION"
    echo "User: $(whoami)"
    echo "Working Dir: $(pwd)"
    echo "Environment:"
    echo "  PATH=$PATH"
    echo "  HOME=$HOME"
    echo "  USER=$USER"
    echo "  SHELL=$SHELL"
    echo "  CRON=$CRON"
    echo "  DEBUG=$DEBUG"
    echo "Python Version:"
    /usr/bin/python3 --version
    echo "Python Location:"
    which python3
    echo "Script Directory: $SCRIPT_DIR"
    echo "Log Directory: $LOG_DIR"
    echo "Log File: $LOG_FILE"
    echo "================================================================"
} >> "$EXEC_LOG" 2>&1

# Change to script directory
cd "$SCRIPT_DIR" || {
    echo "ERROR: Failed to change to $SCRIPT_DIR" >> "$EXEC_LOG"
    exit 1
}

# Execute the appropriate script
case "$ACTION" in
    prestage)
        echo "Executing: python3 claude_mcp_booking.py prestage" >> "$EXEC_LOG"
        /usr/bin/python3 claude_mcp_booking.py prestage >> "$LOG_FILE" 2>&1
        RESULT=$?
        ;;
    book)
        echo "Executing: python3 claude_mcp_booking.py book" >> "$EXEC_LOG"
        /usr/bin/python3 claude_mcp_booking.py book >> "$LOG_FILE" 2>&1
        RESULT=$?
        ;;
    gap)
        echo "Executing: python3 morning_gap_finder_claude.py" >> "$EXEC_LOG"
        /usr/bin/python3 morning_gap_finder_claude.py >> "$LOG_FILE" 2>&1
        RESULT=$?
        ;;
    gap-night)
        echo "Executing: python3 overnight_gap_finder_claude.py" >> "$EXEC_LOG"
        /usr/bin/python3 overnight_gap_finder_claude.py >> "$LOG_FILE" 2>&1
        RESULT=$?
        ;;
esac

# Log execution result
{
    echo "================================================================"
    echo "CRON EXECUTION COMPLETED"
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S.%3N')"
    echo "Exit Code: $RESULT"
    if [ $RESULT -eq 0 ]; then
        echo "Status: SUCCESS"
    else
        echo "Status: FAILED"
        echo "Check log file: $LOG_FILE"
    fi
    echo "================================================================"
    echo ""
} >> "$EXEC_LOG" 2>&1

# Also log to syslog for system-wide tracking
logger -t "golf-booking-cron" "Action: $ACTION, Result: $RESULT, Log: $LOG_FILE"

exit $RESULT