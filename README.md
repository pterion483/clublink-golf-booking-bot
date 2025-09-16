# 🤖 Claude Code Golf Booking System

## The AI Revolution in Golf Booking

This repository implements an **AI-driven golf booking system** using Claude Code as the intelligent booking agent. Unlike traditional scripted automation, this system uses visual understanding and adaptive reasoning to book tee times at ClubLink golf courses.

## 🚀 Quick Start

```bash
# Setup the system
./setup_claude_cron.sh

# Test booking flow
python3 claude_mcp_booking.py test

# Manual booking
python3 claude_mcp_booking.py book

# Manual gap finder tests
python3 morning_gap_finder_claude.py    # Daytime gap finder
python3 overnight_gap_finder_claude.py  # Overnight gap finder
./run_gap_finder.sh                     # Legacy gap finder script

# Check gap finder status
tail -f logs/gap_finder_$(date +%Y%m%d).log
```

## 📚 Key Documentation

### Essential Reading
1. **[AI_REVOLUTION_README.md](AI_REVOLUTION_README.md)** - Complete system overview and architecture
2. **[booking_instructions.md](booking_instructions.md)** - Detailed AI agent instructions with all element references
3. **[CLAUDE.md](CLAUDE.md)** - Critical project-specific instructions (Cloudflare timing!)

### Implementation Guides
- **[claude_direct_executor.md](claude_direct_executor.md)** - Direct Claude Code execution guide
- **[claude_crontab](claude_crontab)** - Cron scheduling configuration

## 🏗️ Architecture

```
Claude Code (AI Agent)
    ↓
Playwright MCP Tools
    ↓
ClubLink Website
```

**Key Innovation**: Claude Code IS the booking agent - not a script runner, but an intelligent decision maker that:
- Sees pages through browser snapshots
- Adapts to UI changes automatically
- Handles errors intelligently
- Makes real-time decisions

## 🆕 Dual Gap Finder System

**Automatically fills your schedule with morning tee times using intelligent scheduling!**

The system includes a sophisticated **dual gap finder system** that operates on different schedules to optimize booking opportunities:

### 🌅 Daytime Gap Finder
- **Schedule**: Every 15 minutes from 6 AM to 9 PM
- **Days Checked**: Days 1-5 (tomorrow through 5 days ahead)
- **Purpose**: Aggressive checking for next-day bookings and immediate cancellations
- **Script**: `morning_gap_finder_claude.py`

### 🌙 Overnight Gap Finder
- **Schedule**: Every hour from 10 PM to 5 AM (22:00, 23:00, 00:00-05:00)
- **Days Checked**: Days 2-5 (skips tomorrow, checks 2-5 days ahead)
- **Purpose**: Gentle overnight monitoring with more advance notice
- **Script**: `overnight_gap_finder_claude.py`

### 🎯 How It Works
Both gap finders:
1. Check your current bookings at https://linklineonline.ca/web/my-account/itinerary
2. Identify days without morning tee times (before 11:00 AM)
3. Search for available morning slots on primary courses (King Valley, Kings Riding, Wyndance, Station Creek-South, DiamondBack, Station Creek-North)
4. Fall back to backup courses if needed (Emerald Hills T1/T10/T19, Caledon Woods)
5. Automatically book the earliest available morning time
6. **Important**: Neither system books same-day tee times automatically

### 📋 Cron Schedule
From `claude_crontab_enhanced`:
```bash
# Daytime Gap Finder - every 15 minutes (6 AM - 9 PM)
*/15 6-21 * * * /home/dmin1/Golf\ Tee\ Times\ Bot/cron_wrapper.sh gap

# Overnight Gap Finder - every hour (10 PM - 5 AM)
0 22,23 * * * /home/dmin1/Golf\ Tee\ Times\ Bot/cron_wrapper.sh gap-night
0 0-5 * * * /home/dmin1/Golf\ Tee\ Times\ Bot/cron_wrapper.sh gap-night
```

## ⚡ Critical Success Factors

### 1. Cloudflare Challenge (MOST CRITICAL)
- **MUST click within 1 SECOND** after Search button
- Connection failed = too slow at Cloudflare
- Use real mouse movement (browser_hover → browser_click)
- Never use JavaScript clicks

### 2. Course Selection
- Maximum 6 courses allowed
- Required: King Valley, King's Riding, Wyndance, Station Creek-South, DiamondBack, Station Creek-North

### 3. Timing
- Pre-stage at 6:25 AM (login and setup)
- Execute booking at exactly 6:30:00 AM
- Complete within 15 seconds

## 📁 Project Structure

```
/home/dmin1/Golf Tee Times Bot/
├── AI_REVOLUTION_README.md         # Complete system documentation
├── booking_instructions.md         # AI agent instructions with refs
├── CLAUDE.md                       # Critical project instructions
├── claude_mcp_booking.py           # Main booking orchestrator
├── claude_booking_agent.sh         # Shell wrapper for Claude
├── claude_crontab_enhanced         # Current cron schedule configuration
├── morning_gap_finder_claude.py    # Daytime gap finder (days 1-5, every 15min)
├── overnight_gap_finder_claude.py  # Overnight gap finder (days 2-5, hourly)
├── cron_wrapper.sh                 # Cron execution wrapper with logging
├── run_gap_finder.sh              # Manual gap finder trigger
├── setup_claude_cron.sh           # Setup script
├── cron/                          # Cron-related files
├── logs/                          # Execution logs (gap finder & booking)
├── screenshots/                   # Booking confirmations
└── old/                           # Legacy Python automation (deprecated)
```

## 🔧 Configuration

### Main Booking System
Edit `claude_mcp_booking.py` to customize:
- Golf courses (max 6)
- Number of players (default: 1)
- Booking days ahead (default: 5)
- Time preferences

### Gap Finder System
Both gap finders are configured in their respective Python files:
- **Primary Courses**: King Valley, Kings Riding, Wyndance, Station Creek-South, DiamondBack, Station Creek-North
- **Backup Courses**: Emerald Hills T1, Emerald Hills T10, Emerald Hills T19, Caledon Woods
- **Morning Time**: Before 11:00 AM
- **Players**: 1 (default)

## 🔍 Gap Finder Operation

### Manual Testing
```bash
# Test daytime gap finder
python3 morning_gap_finder_claude.py

# Test overnight gap finder
python3 overnight_gap_finder_claude.py

# Use the manual trigger script
./run_gap_finder.sh
```

### Log Monitoring
Gap finder logs are stored in `/home/dmin1/Golf Tee Times Bot/logs/`:
- `gap_finder_YYYYMMDD.log` - Daytime gap finder logs
- `gap_finder_overnight_YYYYMMDD.log` - Overnight gap finder logs
- `cron_gap_exec_YYYYMMDD.log` - Cron execution logs for daytime
- `cron_gap_night_exec_YYYYMMDD.log` - Cron execution logs for overnight

### System Status Check
```bash
# Check if cron jobs are running
crontab -l

# Monitor recent gap finder activity
tail -f "/home/dmin1/Golf Tee Times Bot/logs/gap_finder_$(date +%Y%m%d).log"

# Check system-wide cron logs
sudo journalctl -u cron -f
```

## 📊 Success Metrics

- ✅ Booking completed within 15 seconds of 6:30 AM
- ✅ Earliest available tee time secured
- ✅ No manual intervention required
- ✅ Adapts to UI changes automatically

## 🚨 Troubleshooting

### Main Booking System
| Issue | Solution |
|-------|----------|
| Connection failed | You're too slow with Cloudflare - must click within 1 second |
| No times available | Try different dates, especially weekends |
| Login fails | Check credentials in CLAUDE.md |
| Cron not running | Run `crontab -l` to verify, check system time |

### Gap Finder System
| Issue | Solution |
|-------|----------|
| Gap finder not running | Check `crontab -l` for gap finder entries |
| No gaps found | Normal - system only books when gaps exist |
| Gap finder booking failures | Check Cloudflare timing - same 1-second rule applies |
| Too many bookings | Gap finders only book ONE time per run to prevent overbooking |
| Overnight gaps not working | Verify overnight cron jobs: `0 22,23 * * *` and `0 0-5 * * *` |
| Daytime gaps missing tomorrow | By design - daytime checks 1-5, overnight checks 2-5 |
| Gap finder logs missing | Check `/home/dmin1/Golf Tee Times Bot/logs/` directory permissions |
| Same-day booking | Gap finders never book same-day - this is intentional |

### Common Gap Finder Issues
- **No morning times available**: This is normal - gap finders only book when morning slots exist
- **Skipping tomorrow**: Overnight gap finder intentionally skips tomorrow for advance notice
- **Multiple gap finders running**: Each has different purpose - daytime (aggressive) vs overnight (gentle monitoring)
- **Booking conflicts**: Only one tee time booked per gap finder run to prevent double-booking

## 📝 Notes

- **This is NOT automation** - it's intelligent, adaptive booking
- Claude Code makes decisions based on visual understanding
- The system self-recovers from errors
- All legacy Python scripts moved to `/old` folder (deprecated)

## 🔄 Migration from Legacy System

The old Python/Selenium approach has been completely replaced. All legacy files are archived in the `/old` directory for reference but are no longer used.

**Old Way**: Python → Selenium → Fixed automation → Frequent failures
**New Way**: Claude Code → Visual intelligence → Adaptive decisions → Reliable booking

---

For detailed implementation and technical documentation, see [AI_REVOLUTION_README.md](AI_REVOLUTION_README.md)