# Golf Booking Instructions for AI Agents

This file contains detailed instructions for AI agents (Claude Code) to execute golf bookings automatically.

## Critical Information

### Login Credentials
- **URL**: https://kingvalley.clublink.ca/login
- **Membership Number**: 224816
- **Password**: 160599Golf

### Booking Flow
1. Login at kingvalley.clublink.ca
2. Click "Tee Times Plus" (opens new tab)
3. Set date, players, time
4. Click Search
5. **IMMEDIATELY** handle Cloudflare (within milliseconds)
6. Select available tee time
7. Confirm booking

## Cloudflare Challenge Handling

**CRITICAL**: The Cloudflare challenge appears immediately after clicking Search button.

- **Coordinates**: (464, 572)
- **Timing**: Must click within 200ms or booking will fail
- **Method**: Use cloudflare_handler.py module in this directory
- **Backup**: Direct coordinate click if module unavailable

## Course Selection

**Priority Courses** (select exactly 6):
1. King Valley
2. King's Riding
3. Wyndance
4. Station Creek South
5. Diamondback
6. Station Creek North

**Backup Courses** (if primary unavailable):
- Emerald Hills T1
- Emerald Hills T10
- Emerald Hills T19
- Caledon Woods

## Timing Requirements

### Main Booking (6:30 AM)
- Target time: **06:30:00.000** (exact)
- Pre-staging: 6:25 AM (form setup)
- Search click: Precisely at 6:30:00
- Cloudflare handling: Within 200ms

### Gap Finding (Throughout Day)
- Check days 1-5 ahead
- Look for times before 11:00 AM
- Book earliest available morning slot

## Technical Implementation

### Browser Setup
- Use Playwright MCP tools
- Take snapshots to understand page state
- Handle dynamic content appropriately

### Error Handling
- Retry Cloudflare challenge if first attempt fails
- Capture screenshots for confirmation
- Log all actions with timestamps

### Success Criteria
- Booking confirmed within 15 seconds of 6:30 AM
- Screenshot of confirmation saved
- Earliest available time secured

## Element References

### Login Page
- Membership field: `name="membership"`
- Password field: `name="password"`
- Login button: `input[type="submit"]`

### Booking Page
- Date field: Search for date input
- Players field: Search for players/golfers input
- Course checkboxes: Look for course names in labels
- Search button: `input[value="Search"]` or similar
- Time slots: Links or buttons containing "Book" or booking URLs

### Cloudflare Challenge
- Checkbox: `input[type="checkbox"]` within Cloudflare frame
- Verification text: Text containing "Verify you are human"
- Fallback coordinates: (464, 572)

## Important Notes

1. **Speed is critical** - Golf bookings are highly competitive
2. **Cloudflare timing** - The 200ms window is non-negotiable
3. **Course selection** - Must select exactly 6 courses or booking fails
4. **Screenshot evidence** - Always capture confirmation for verification
5. **Adaptive behavior** - Use snapshots to understand current page state

## Files and Scripts

- `cloudflare_handler.py` - Dedicated Cloudflare challenge handler
- `ultrafast_bot.py` - Main booking bot (6:30 AM execution)
- `claude_mcp_booking.py` - MCP orchestrator
- `monitor_bot.py` - System status monitoring
- Gap finders - Automated gap detection and booking