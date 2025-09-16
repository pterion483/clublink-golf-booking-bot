# ClubLink Golf Booking - Critical Project Instructions

## 🚨 CLOUDFLARE CHALLENGE - MOST CRITICAL
### THE #1 CAUSE OF FAILURE: Being Too Slow!
- **MUST CLICK WITHIN 1 SECOND** after Search button
- **Connection failed = YOU WERE TOO SLOW**
- Dialog refs: e1089 (#mat-dialog-0), e1131 (#mat-dialog-1), e1330 (#mat-dialog-2)
- Coordinates: (464, 572)

### ✅ CORRECT Approach:
1. Click Search button (refs: e129, e1102, e1144)
2. IMMEDIATELY hover to dialog ref
3. Click within 1 second using REAL mouse events
4. Use: `browser_hover` → `browser_click`

### ❌ WRONG Approaches (WILL FAIL):
- Waiting 2 seconds before clicking
- Using JavaScript evaluate for clicks
- Not using mouse hover first
- Taking snapshots before handling Cloudflare

## 📋 Login Credentials
- **URL**: https://kingvalley.clublink.ca/login
- **Membership Number**: 224816
- **Password**: 160599Golf
- **Username field ref**: e231
- **Password field ref**: e234
- **Submit button ref**: e238

## 🏌️ Course Selection (Maximum 6)
Required courses in priority order:
1. King Valley (ref: e338)
2. King's Riding (ref: e346) - Note: spelled "Kings Riding" in system
3. Wyndance (ref: e695)
4. Station Creek-South (ref: e642) - Note the hyphen
5. DiamondBack (ref: e279)
6. Station Creek-North (ref: e638)

**Process**:
- Click course field (ref: e78)
- FIRST uncheck "All Courses" (ref: e262)
- Then select exactly 6 courses
- Click Done (ref: e743)

## 👤 Player Configuration
- Default: 4 Players
- Required: 1 Player
- Click Players field (ref: e88)
- Click decrease 3 times (ref: e831)
- Click Done (ref: e838)

## 📅 Booking Preferences
- **Days ahead**: 5 days (for regular booking)
- **Time range**: 7:00 AM - 11:00 AM
- **Players**: 1
- **Holes**: 18

## ⚡ Complete Booking Flow
```
1. Login → e231, e234, e238
2. Navigate → e45 (Tee Times Plus) → Switch to tab 1
3. Courses → e78 → e262 (uncheck) → Select 6 → e743
4. Players → e88 → e831 (3x) → e838
5. Date → e66 → Select date → Close
6. Search → e129/e1102/e1144
7. Cloudflare → e1089/e1131/e1330 (WITHIN 1 SECOND!)
8. Select time → e1350 (or first available)
9. Continue → e1485
10. Confirm → e1565
```

## ⏰ Cron Schedule

### Main Booking (6:30 AM Daily)
- **6:25 AM**: Pre-stage (login and setup)
- **6:30:00 AM**: Execute booking (click Search)
- Must complete within 15 seconds

### Morning Gap Finder
- **Daytime (6 AM - 9 PM)**: Every 15 minutes
  - Checks days 1-5 ahead (includes tomorrow)
  - Script: `morning_gap_finder_claude.py`
- **Overnight (10 PM - 5 AM)**: Every hour
  - Checks days 2-5 ahead (skips tomorrow for 24+ hour notice)
  - Script: `overnight_gap_finder_claude.py`
- **Behavior**:
  - NEVER books same-day automatically
  - Only books morning times (before 11 AM)
  - Books max ONE time per run

## 🔧 AI-Driven System Files
- **booking_instructions.md**: Complete AI agent instructions with all refs
- **claude_mcp_booking.py**: Main orchestrator (6:30 AM booking)
- **morning_gap_finder_claude.py**: Daytime gap finder (days 1-5)
- **overnight_gap_finder_claude.py**: Overnight gap finder (days 2-5)
- **claude_crontab_enhanced**: Full cron configuration
- **cron_wrapper.sh**: Cron execution wrapper with logging

## ❗ Critical Success Factors
1. **Cloudflare speed**: Click within 1 second
2. **Course limit**: Exactly 6 courses maximum
3. **Mouse events**: Use browser_hover + browser_click
4. **Timing precision**: 6:30:00.000 AM execution

## 🔍 Error Recovery
- **Connection failed**: Close error (e1115) → Retry Search → Click faster!
- **No times available**: Try different date (weekends better)
- **Login fails**: Verify credentials above
- **Turnstile error 300030**: Cloudflare verification failed - too slow

## 📝 Console Error Messages
- "Turnstile Widget seem to have hung" = Too slow
- "Turnstile errorV: 300030" = Verification failed
- "Connection failed" = Didn't click Cloudflare in time

---
**Remember**: This is AI-driven intelligent booking, not scripted automation. Claude Code adapts to what it sees!