# Golf Booking System - Claude Code MCP Architecture

## Overview
This system uses **Claude Code with Playwright MCP tools** to execute golf bookings directly. Python scripts only generate prompts; Claude Code does all the actual web automation.

## Core Architecture

```
┌──────────┐     ┌───────────────┐     ┌──────────────┐     ┌──────────────┐
│   CRON   │────▶│claude_executor│────▶│Python Scripts│────▶│ Claude Code  │
│          │     │     .sh       │     │ (generate    │     │ (MCP tools)  │
└──────────┘     └───────────────┘     │  prompts)    │     └──────────────┘
                                        └──────────────┘              │
                                                                       ▼
                                                              ┌──────────────┐
                                                              │  Web Browser │
                                                              │ (Playwright) │
                                                              └──────────────┘
```

## Execution Flow

1. **Cron Job Triggers** (every 15 min / 1 hour / 6:30 AM)
   - Runs `claude_executor.sh` with action parameter

2. **Claude Executor Script**
   - Runs Python script to generate prompt file
   - Launches Claude Code via CLI to read and execute prompt

3. **Python Scripts** (Generate prompts only!)
   - `claude_mcp_booking.py` → Creates booking instructions
   - `morning_gap_finder_claude.py` → Creates gap finder instructions
   - `overnight_gap_finder_claude.py` → Creates overnight gap instructions
   - Output: `current_claude_prompt.txt` or `current_gap_finder_prompt.txt`

4. **Claude Code Execution**
   - Reads prompt file with booking instructions
   - Uses Playwright MCP tools (`mcp__playwright__browser_*`)
   - Executes the booking autonomously
   - Handles Cloudflare challenges
   - Completes bookings

## Key Files

### Execution Layer
- `claude_executor.sh` - Main launcher script called by cron
- `claude_direct_crontab` - Crontab configuration

### Prompt Generation Layer
- `claude_mcp_booking.py` - Generates 6:30 AM booking prompts
- `morning_gap_finder_claude.py` - Generates daytime gap finder prompts
- `overnight_gap_finder_claude.py` - Generates overnight gap finder prompts

### Output Files
- `current_claude_prompt.txt` - Active booking prompt for Claude
- `current_gap_finder_prompt.txt` - Active gap finder prompt

### Configuration
- `CLAUDE.md` - Critical project instructions
- `booking_instructions.md` - Detailed booking flow

## Cron Schedule

```bash
# Main booking at 6:30 AM
30 6 * * * /home/dmin1/Golf\ Tee\ Times\ Bot/claude_executor.sh book

# Daytime gap finder (every 15 min, 6 AM - 9 PM)
*/15 6-21 * * * /home/dmin1/Golf\ Tee\ Times\ Bot/claude_executor.sh gap

# Overnight gap finder (every hour, 10 PM - 5 AM)
0 22,23 * * * /home/dmin1/Golf\ Tee\ Times\ Bot/claude_executor.sh gap-night
0 0-5 * * * /home/dmin1/Golf\ Tee\ Times\ Bot/claude_executor.sh gap-night
```

## Testing

```bash
# Test Claude Code execution
cd "/home/dmin1/Golf Tee Times Bot"
./claude_executor.sh test

# Test gap finder
./claude_executor.sh gap

# Test booking (use carefully!)
./claude_executor.sh book
```

## Important Notes

1. **Claude Code does the work** - Python scripts ONLY generate prompts
2. **MCP tools required** - Playwright MCP server must be running
3. **Permissions** - Uses `--dangerously-skip-permissions` for automation
4. **Logging** - All executions logged to `logs/` directory
5. **WSL Considerations** - Cron service must be running (`sudo service cron start`)

## Troubleshooting

### Cron not working in WSL
```bash
# Check if cron is running
ps aux | grep cron

# Start cron service
sudo service cron start

# Check crontab
crontab -l
```

### Claude Code not executing
- Verify Claude CLI is installed: `which claude`
- Check MCP servers are configured: `claude --help`
- Review logs in `/home/dmin1/Golf Tee Times Bot/logs/`

### Bookings failing
- Check Cloudflare handling speed (must be < 1 second)
- Verify login credentials in prompts
- Check course selection (max 6 courses)

## Architecture Benefits

1. **True AI Execution** - Claude Code adapts to UI changes
2. **Separation of Concerns** - Python generates instructions, Claude executes
3. **Maintainability** - Easy to update prompts without changing execution
4. **Logging** - Complete audit trail of all actions
5. **Flexibility** - Claude can handle unexpected scenarios

## Future Improvements

- Direct MCP API calls without CLI
- Real-time status monitoring
- Multiple booking strategies
- Automatic failure recovery