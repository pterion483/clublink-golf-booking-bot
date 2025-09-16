#!/bin/bash
#
# Claude Code MCP Wrapper for Golf Booking System
# This wrapper invokes Claude Code directly with MCP tools instead of generating prompts
#

# Set up environment
export PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/home/dmin1/.local/bin:/home/dmin1/.nvm/versions/node/v20.19.4/bin
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

# Create log directory
mkdir -p "$LOG_DIR"

# Function to log messages
log_message() {
    local message="$1"
    local log_file="$2"
    echo "[$TIMESTAMP] $message" | tee -a "$log_file"
}

# Determine log files
case "$ACTION" in
    prestage)
        LOG_FILE="$LOG_DIR/claude_code_prestage_$DATE.log"
        EXEC_LOG="$LOG_DIR/cron_code_prestage_$DATE.log"
        ;;
    book)
        LOG_FILE="$LOG_DIR/claude_code_booking_$DATE.log"
        EXEC_LOG="$LOG_DIR/cron_code_booking_$DATE.log"
        ;;
    gap)
        LOG_FILE="$LOG_DIR/claude_code_gap_$DATE.log"
        EXEC_LOG="$LOG_DIR/cron_code_gap_$DATE.log"
        ;;
    gap-night)
        LOG_FILE="$LOG_DIR/claude_code_gap_night_$DATE.log"
        EXEC_LOG="$LOG_DIR/cron_code_gap_night_$DATE.log"
        ;;
    *)
        echo "Usage: $0 {prestage|book|gap|gap-night}"
        exit 1
        ;;
esac

# Log execution start
{
    echo "================================================================"
    echo "CLAUDE CODE MCP EXECUTION STARTED"
    echo "================================================================"
    echo "Timestamp: $TIMESTAMP"
    echo "Action: $ACTION"
    echo "User: $(whoami)"
    echo "Working Dir: $(pwd)"
    echo "Environment:"
    echo "  PATH=$PATH"
    echo "  HOME=$HOME"
    echo "  NODE_PATH=$NODE_PATH"
    echo "Claude Version:"
    which claude && claude --version
    echo "Script Directory: $SCRIPT_DIR"
    echo "Log Directory: $LOG_DIR"
    echo "================================================================"
} >> "$EXEC_LOG" 2>&1

# Change to script directory
cd "$SCRIPT_DIR" || {
    echo "ERROR: Failed to change to $SCRIPT_DIR" >> "$EXEC_LOG"
    exit 1
}

# Create dynamic prompts based on action
create_prestage_prompt() {
    local booking_date=$(date -d "+5 days" '+%Y-%m-%d')
    cat << EOF
Execute golf booking pre-staging using MCP Playwright tools:

1. Navigate to https://kingvalley.clublink.ca/login
2. Login: 224816 / 160599Golf
3. Go to "Tee Times Plus"
4. Set date: $booking_date, players: 1
5. Select courses: King Valley, King's Riding, Wyndance, Station Creek South, Diamondback, Station Creek North
6. DO NOT click Search - leave form ready
7. Take screenshot of ready state

Critical: Form must be ready for 6:30 AM execution.
EOF
}

create_booking_prompt() {
    local booking_date=$(date -d "+5 days" '+%Y-%m-%d')
    cat << EOF
Execute time-critical golf booking using MCP Playwright tools:

1. Verify form is ready (take snapshot)
2. At exactly 6:30:00 AM, click Search button
3. IMMEDIATELY handle Cloudflare at (464, 572) within 1 second
4. Select earliest morning time (before 11:00 AM)
5. Complete booking confirmation
6. Take success screenshot

CRITICAL: Must execute at 6:30:00 AM sharp with immediate Cloudflare handling!
EOF
}

create_gap_prompt() {
    local dates=""
    for i in {1..5}; do
        local date=$(date -d "+$i days" '+%Y-%m-%d')
        dates="$dates $date"
    done

    cat << EOF
Execute gap finder using MCP Playwright tools:

1. Check current bookings at: https://linklineonline.ca/web/my-account/itinerary
2. Identify dates without morning bookings:$dates
3. For first gap found:
   - Search primary courses: King Valley, King's Riding, Wyndance, Station Creek South, Diamondback, Station Creek North
   - If none available, try backup: Emerald Hills T1, Emerald Hills T10, Emerald Hills T19, Caledon Woods
   - Handle Cloudflare immediately after each search
4. Book earliest morning time if available
5. Take success screenshot

Focus only on morning times before 11:00 AM.
EOF
}

create_gap_night_prompt() {
    local dates=""
    for i in {2..5}; do
        local date=$(date -d "+$i days" '+%Y-%m-%d')
        dates="$dates $date"
    done

    cat << EOF
Execute overnight gap finder using MCP Playwright tools:

1. Check current bookings at: https://linklineonline.ca/web/my-account/itinerary
2. Identify dates without morning bookings (skip tomorrow):$dates
3. For first gap found:
   - Search primary courses: King Valley, King's Riding, Wyndance, Station Creek South, Diamondback, Station Creek North
   - If none available, try backup: Emerald Hills T1, Emerald Hills T10, Emerald Hills T19, Caledon Woods
   - Handle Cloudflare immediately after each search
4. Book earliest morning time if available
5. Take success screenshot

Focus only on morning times before 11:00 AM.
EOF
}

# Execute via Claude Code with MCP tools
execute_claude_code() {
    local prompt="$1"
    local session_name="$2"

    echo "Executing Claude Code with MCP tools..." >> "$EXEC_LOG"
    echo "Session: $session_name" >> "$EXEC_LOG"
    echo "Prompt length: ${#prompt} characters" >> "$EXEC_LOG"

    # Create unique session ID
    local session_id="golf-${session_name}-$(date +%s)"

    # Execute Claude Code with MCP tools
    echo "$prompt" | claude \
        --print \
        --model sonnet \
        --dangerously-skip-permissions \
        --session-id "$session_id" \
        >> "$LOG_FILE" 2>&1

    return $?
}

# Execute the appropriate action
case "$ACTION" in
    prestage)
        echo "Creating pre-staging prompt..." >> "$EXEC_LOG"
        PROMPT=$(create_prestage_prompt)
        execute_claude_code "$PROMPT" "prestage"
        RESULT=$?
        ;;
    book)
        echo "Creating booking prompt..." >> "$EXEC_LOG"
        PROMPT=$(create_booking_prompt)
        execute_claude_code "$PROMPT" "booking"
        RESULT=$?
        ;;
    gap)
        echo "Creating gap finder prompt..." >> "$EXEC_LOG"
        PROMPT=$(create_gap_prompt)
        execute_claude_code "$PROMPT" "gap-daytime"
        RESULT=$?
        ;;
    gap-night)
        echo "Creating overnight gap finder prompt..." >> "$EXEC_LOG"
        PROMPT=$(create_gap_night_prompt)
        execute_claude_code "$PROMPT" "gap-overnight"
        RESULT=$?
        ;;
esac

# Log execution result
{
    echo "================================================================"
    echo "CLAUDE CODE MCP EXECUTION COMPLETED"
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

# Log to syslog
logger -t "golf-booking-claude-code" "Action: $ACTION, Result: $RESULT, Log: $LOG_FILE"

exit $RESULT