# Morning Gap Finder Documentation

## Overview

The Morning Gap Finder is an intelligent system that automatically books morning tee times on days where you don't have any. It runs every 30 minutes throughout the day, catching cancellations as they happen.

## How It Works

### 1. Gap Detection
- Checks your itinerary for the next 5 days
- Identifies days without morning bookings (before 11:00 AM)
- Creates a priority list of days needing morning times

### 2. Continuous Monitoring
- Runs every 30 minutes from 7 AM to 9 PM
- Searches for newly available morning slots
- Books immediately when found

### 3. Smart Booking
- Only books ONE tee time per run (prevents overbooking)
- Focuses on times before 11:00 AM
- Uses your 6 preferred courses
- Handles Cloudflare challenges automatically

## Files

### `morning_gap_finder_claude.py`
Main script that:
- Generates prompts for Claude Code
- Identifies gap days
- Creates booking instructions
- Logs all activity

### `run_gap_finder.sh`
Manual trigger script for:
- Testing the system
- Running on-demand checks
- Viewing current gaps

### Cron Entry
```bash
*/30 7-21 * * * cd "$GOLF_BOT_HOME" && python3 morning_gap_finder_claude.py >> logs/gap_finder.log 2>&1
```

## Configuration

Edit `morning_gap_finder_claude.py` to customize:

```python
DAYS_AHEAD = 5  # Maximum booking window
MORNING_END = "11:00"  # Define "morning"
PREFERRED_COURSES = [
    "King Valley",
    "Kings Riding",
    "Wyndance",
    "Station Creek-South",
    "DiamondBack",
    "Station Creek-North"
]
```

## Usage

### Manual Run
```bash
# Generate and view the gap finder prompt
./run_gap_finder.sh

# Check logs
tail -f logs/gap_finder_$(date +%Y%m%d).log
```

### Automatic Mode
```bash
# Install cron job for automatic checking
crontab claude_crontab

# Verify it's running
crontab -l | grep gap_finder
```

## Example Workflow

### Current Bookings:
```
Sep 16: 3:57 PM (afternoon only)
Sep 17: No bookings
Sep 18: 8:40 AM (has morning ✓)
Sep 19: 9:30 AM (has morning ✓)
Sep 20: No bookings
```

### Gap Finder Actions:
1. **7:00 AM**: Checks Sep 16 - finds 8:30 AM at King Valley → BOOKS IT
2. **7:30 AM**: Checks Sep 17 - no times available yet
3. **8:00 AM**: Checks Sep 17 - finds 9:00 AM at Wyndance → BOOKS IT
4. **8:30 AM**: Checks Sep 20 - finds 7:40 AM at Station Creek → BOOKS IT
5. **9:00 AM**: All gaps filled, continues monitoring for better times

## Logic Flow

```
Every 30 minutes:
├── Check itinerary
├── Find days without morning bookings
├── For first gap day:
│   ├── Search for times 7:00-11:00 AM
│   ├── If available:
│   │   ├── Book earliest time
│   │   └── Exit (one booking per run)
│   └── If not available:
│       └── Continue to next gap day
└── Log results and wait 30 minutes
```

## Monitoring

### Check Status
```bash
# View current gaps
python3 morning_gap_finder_claude.py

# See last booking attempts
grep "BOOKED" logs/gap_finder_*.log

# Watch live activity
tail -f logs/gap_finder_$(date +%Y%m%d).log
```

### Success Indicators
- "Found morning booking" - Successfully booked
- "No morning times available" - Checked but nothing open
- "All gaps filled" - Schedule is complete

## Troubleshooting

### No bookings being made
- Check if you're logged in correctly
- Verify Cloudflare is being handled within 1 second
- Ensure courses are properly selected

### Too many bookings
- System books ONE per run by design
- Check cron frequency (default: every 30 minutes)
- Review logs for duplicate runs

### Connection failures
- Usually means Cloudflare timing issue
- Must click within 1 second of Search
- Check CLAUDE.md for timing requirements

## Best Practices

1. **Run during peak cancellation times**
   - Early morning (7-9 AM) - people canceling same-day
   - Evening (6-9 PM) - people planning ahead
   - Lunch time (12-1 PM) - business hour cancellations

2. **Monitor special dates**
   - Weekends fill up fast - monitor aggressively
   - Holidays need earlier booking
   - Bad weather days have more cancellations

3. **Optimize for your schedule**
   - Adjust MORNING_END if you prefer earlier times
   - Modify course list based on location preferences
   - Change frequency based on urgency

## Integration with Main System

The Gap Finder works alongside the main booking system:
- **6:30 AM**: Main system books 5 days ahead
- **Throughout day**: Gap Finder fills in missing morning times
- **Result**: Complete schedule with preferred morning slots

## Logs

All activity is logged to:
```
/home/dmin1/Golf Tee Times Bot/logs/gap_finder_YYYYMMDD.log
```

Example log entries:
```
[08:00:00] Starting gap check...
[08:00:02] Current morning bookings: Sep 18 (8:40), Sep 19 (9:30)
[08:00:03] Gap found: Sep 16 - no morning booking
[08:00:08] Searching for times on Sep 16...
[08:00:15] FOUND: 8:30 AM at King Valley - Booking now!
[08:00:25] ✓ Successfully booked
```

## Future Enhancements

Potential improvements:
- Preference for specific times (e.g., always after 8 AM)
- Course-specific time preferences
- Weather-based adjustments
- Group size flexibility (1-2 players)
- Integration with calendar systems
- Email/SMS notifications