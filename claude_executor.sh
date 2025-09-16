#!/bin/bash
# Claude Code Executor for Golf Bookings
# This script is called by cron to launch Claude Code to execute bookings

set -e

# Add Claude to PATH (installed via nvm)
export PATH="/home/dmin1/.nvm/versions/node/v20.19.4/bin:$PATH"

# Configuration
SCRIPT_DIR="/home/dmin1/Golf Tee Times Bot"
LOG_DIR="$SCRIPT_DIR/logs"
DATE=$(date +%Y%m%d)
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S.%3N')

# Action type passed as first argument
ACTION=$1

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log_message() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_DIR/claude_executor_${DATE}.log"
}

# Function to execute Claude Code with a prompt file
execute_claude() {
    local prompt_file=$1
    local action_name=$2

    if [ ! -f "$prompt_file" ]; then
        log_message "ERROR: Prompt file not found: $prompt_file"
        return 1
    fi

    log_message "Starting Claude Code execution for: $action_name"
    log_message "Reading prompt from: $prompt_file"

    # Execute Claude Code with the prompt
    # Using --dangerously-skip-permissions to allow automated execution
    # Using --print for non-interactive output
    # Directly pass the prompt content to Claude

    # Read the prompt file and pipe it directly to Claude
    # This ensures Claude gets the actual booking instructions, not a meta-instruction to read a file
    cat "$prompt_file" | claude --print --dangerously-skip-permissions --mcp-config '{"mcpServers": {"playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}}}' 2>&1 | tee -a "$LOG_DIR/claude_output_${DATE}.log"

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log_message "SUCCESS: Claude Code execution completed for $action_name"
    else
        log_message "ERROR: Claude Code execution failed for $action_name with exit code $exit_code"
    fi

    return $exit_code
}

# Main execution logic
case "$ACTION" in
    book)
        log_message "=== BOOKING EXECUTION STARTED ==="
        # First generate the prompt
        cd "$SCRIPT_DIR"
        python3 claude_mcp_booking.py
        # Then execute it with Claude Code
        execute_claude "$SCRIPT_DIR/current_claude_prompt.txt" "6:30 AM Booking"
        ;;

    gap)
        log_message "=== GAP FINDER (DAYTIME) EXECUTION STARTED ==="
        # First generate the prompt
        cd "$SCRIPT_DIR"
        python3 morning_gap_finder_claude.py
        # Then execute it with Claude Code
        execute_claude "$SCRIPT_DIR/current_gap_finder_prompt.txt" "Daytime Gap Finder"
        ;;

    gap-night)
        log_message "=== GAP FINDER (OVERNIGHT) EXECUTION STARTED ==="
        # First generate the prompt
        cd "$SCRIPT_DIR"
        python3 overnight_gap_finder_claude.py
        # Then execute it with Claude Code
        execute_claude "$SCRIPT_DIR/current_gap_finder_prompt.txt" "Overnight Gap Finder"
        ;;

    test)
        log_message "=== TEST EXECUTION ==="
        # Direct test execution
        claude --print --dangerously-skip-permissions <<EOF
Test message from cron job. Current time: $TIMESTAMP. If you can see this, the Claude Code execution from cron is working.
EOF
        ;;

    *)
        log_message "ERROR: Unknown action: $ACTION"
        echo "Usage: $0 {book|gap|gap-night|test}"
        exit 1
        ;;
esac

log_message "=== EXECUTION COMPLETED ==="
exit 0