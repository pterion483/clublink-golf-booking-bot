#!/usr/bin/env python3
"""
Morning Gap Finder - Claude Code Version
This script creates prompts for Claude Code to find and book morning tee times.
Run every 30 minutes via cron to continuously check for openings.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import List

# Configuration
DAYS_AHEAD = 5
MORNING_END = "11:00"
LOG_DIR = "/home/dmin1/Golf Tee Times Bot/logs"

def setup_logging():
    """Setup logging configuration."""
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"gap_finder_{datetime.now().strftime('%Y%m%d')}.log")

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def generate_claude_prompt():
    """Generate the prompt for Claude Code to execute."""

    # Calculate date range
    today = datetime.now()
    dates_to_check = []
    for i in range(1, DAYS_AHEAD + 1):
        date = today + timedelta(days=i)
        dates_to_check.append(date.strftime("%Y-%m-%d"))

    prompt = f"""
Please execute the following golf booking gap finder task using Playwright MCP tools:

## Step 1: Check Current Bookings
1. Navigate to https://linklineonline.ca/web/my-account/itinerary
2. If not logged in:
   - Go to https://kingvalley.clublink.ca/login
   - Login with Membership: 224816, Password: 160599Golf
   - Navigate back to itinerary
3. Take a snapshot and identify all bookings
4. Make a list of dates that have morning bookings (before 11:00 AM)

## Step 2: Find Gap Days
Check these dates: {', '.join(dates_to_check)}
Identify which dates do NOT have a morning booking (before 11:00 AM).

## Step 3: Search for Morning Times - Primary Courses
For the FIRST gap day found (if any):
1. Navigate to https://linklineonline.ca/web/tee-times
2. Configure search with PRIMARY courses:
   - Click course selector
   - Uncheck "All Courses" first
   - Select: King Valley, Kings Riding, Wyndance, Station Creek-South, DiamondBack, Station Creek-North
   - Set Players to 1
   - Set the date to the gap day
   - Set time to 06:00 AM (to search from earliest)
3. Click Search
4. **CRITICAL**: Handle Cloudflare IMMEDIATELY (within 1 second!) - hover and click at dialog or (464, 572)

## Step 4: Check Primary Course Results
If NO morning times available with primary courses, proceed to Step 5.
If morning times ARE available, skip to Step 6 to book.

## Step 5: Search Backup Courses (if primary unavailable)
If no times found with primary courses:
1. Clear the search and start fresh
2. Configure search with BACKUP courses:
   - Click course selector
   - Uncheck "All Courses" first
   - Select: Emerald Hills T1, Emerald Hills T10, Emerald Hills T19, Caledon Woods
   - Set Players to 1
   - Set the same gap day date
   - Set time to 06:00 AM
3. Click Search
4. **CRITICAL**: Handle Cloudflare IMMEDIATELY (within 1 second!)

## Step 6: Book Morning Time
If morning times (before 11:00 AM) are available from either primary or backup courses:
1. Click on the EARLIEST morning time
2. Click Continue in the confirmation dialog
3. Click Confirm on the final page
4. Take a screenshot of the confirmation

## Step 7: Report Results
Report what was done:
- Which dates were checked
- Which dates already had morning bookings
- What gap was found
- Which courses were searched (primary and/or backup)
- What was booked (if anything)

## Important Notes:
- Only book ONE tee time per run (to avoid overbooking)
- Focus on times before 11:00 AM only
- If no morning times available, report that and move on
- Handle Cloudflare within 1 second or it will fail!
"""

    return prompt

def save_prompt_for_claude(prompt):
    """Save the prompt to a file that Claude Code can read."""
    prompt_file = "/home/dmin1/Golf Tee Times Bot/current_gap_finder_prompt.txt"
    with open(prompt_file, 'w') as f:
        f.write(prompt)
    return prompt_file

def main():
    """Main execution function."""
    logger = setup_logging()

    logger.info("=" * 60)
    logger.info("Morning Gap Finder Starting...")

    # Generate and save the prompt
    prompt = generate_claude_prompt()
    prompt_file = save_prompt_for_claude(prompt)

    logger.info(f"Prompt saved to: {prompt_file}")
    logger.info("Claude Code should now execute this prompt to find and book morning gaps")

    # Print the prompt for manual execution if needed
    print("\n" + "=" * 60)
    print("PROMPT FOR CLAUDE CODE:")
    print("=" * 60)
    print(prompt)
    print("=" * 60 + "\n")

    logger.info("Gap finder prompt generation complete.")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()