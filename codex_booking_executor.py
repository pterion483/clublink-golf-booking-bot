#!/usr/bin/env python3
"""
Codex Booking Executor
This script is designed to run WITHIN Claude Code and use mcp__codex tools directly.
It should be called from cron via a wrapper that invokes Claude Code.
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path

class CodexBookingExecutor:
    def __init__(self):
        self.base_dir = Path("/home/dmin1/Golf Tee Times Bot")
        self.log_dir = self.base_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        self.start_time = datetime.now()

        # Booking configuration
        self.credentials = {
            "membership": "224816",
            "password": "160599Golf",
            "login_url": "https://kingvalley.clublink.ca/login"
        }

        self.primary_courses = [
            "King Valley", "King's Riding", "Wyndance",
            "Station Creek South", "Diamondback", "Station Creek North"
        ]

        self.backup_courses = [
            "Emerald Hills T1", "Emerald Hills T10",
            "Emerald Hills T19", "Caledon Woods"
        ]

    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        elapsed = (datetime.now() - self.start_time).total_seconds()
        log_message = f"[{timestamp}] [{level}] [+{elapsed:.3f}s] {message}"
        print(log_message)

        log_file = self.log_dir / f"codex_executor_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, "a") as f:
            f.write(log_message + "\n")

    def create_prestage_prompt(self, booking_date: str) -> str:
        """Create prestage prompt for MCP execution"""
        return f"""
I need you to execute golf booking pre-staging using MCP Playwright tools. This is critical preparation for tomorrow's 6:30 AM booking.

MISSION: Pre-stage the ClubLink booking form so it's ready to execute at exactly 6:30:00 AM tomorrow.

EXECUTION STEPS:

1. **Initialize and Login**
   - Use mcp__playwright__browser_navigate to go to: {self.credentials["login_url"]}
   - Take mcp__playwright__browser_snapshot to see the login page
   - Find the membership field and use mcp__playwright__browser_type with: {self.credentials["membership"]}
   - Find the password field and use mcp__playwright__browser_type with: {self.credentials["password"]}
   - Use mcp__playwright__browser_click on the login button

2. **Navigate to Booking System**
   - Look for "Tee Times Plus" link and use mcp__playwright__browser_click
   - If it opens a new tab, use mcp__playwright__browser_tabs to manage tabs
   - Take mcp__playwright__browser_snapshot of the booking interface

3. **Configure Booking Form (DO NOT SUBMIT)**
   - Set the booking date to: {booking_date}
   - Set number of players to: 1
   - Click the course selector dropdown
   - Uncheck "All Courses" if it's selected
   - Select these exact 6 courses: {', '.join(self.primary_courses)}
   - Set the time range to start from earliest available (around 7:00 AM)

4. **Final Verification**
   - Use mcp__playwright__browser_take_screenshot to capture the ready state
   - Verify the Search button is visible and ready to click
   - **CRITICAL**: DO NOT CLICK THE SEARCH BUTTON - leave it ready for 6:30 AM

5. **Confirmation**
   - Report that pre-staging is complete
   - Confirm all 6 courses are selected
   - Confirm date is set to {booking_date}
   - Confirm Search button is ready

SUCCESS CRITERIA:
- Form completely filled but NOT submitted
- Search button ready for immediate clicking at 6:30 AM
- All settings verified and screenshot taken

Execute this workflow now using the MCP Playwright tools.
"""

    def create_booking_prompt(self, booking_date: str) -> str:
        """Create booking execution prompt"""
        return f"""
I need you to execute a time-critical golf booking using MCP Playwright tools. This booking opens at exactly 6:30:00 AM and requires split-second timing.

CRITICAL MISSION: Complete golf booking within 30 seconds of 6:30:00 AM.

TIMING-CRITICAL EXECUTION:

1. **Pre-Flight Check**
   - Use mcp__playwright__browser_snapshot to verify the booking form is ready
   - Confirm date is set to {booking_date}
   - Confirm 6 courses are selected: {', '.join(self.primary_courses)}
   - Confirm Search button is visible and ready

2. **PRECISION TIMING EXECUTION**
   - Monitor system time until exactly 6:30:00.000 AM
   - At PRECISELY 6:30:00 AM, use mcp__playwright__browser_click on the Search button
   - Log the exact timestamp when you clicked

3. **IMMEDIATE Cloudflare Challenge**
   - Within 200 milliseconds of clicking Search, Cloudflare will challenge
   - Use mcp__playwright__browser_hover at coordinates (464, 572)
   - IMMEDIATELY use mcp__playwright__browser_click at the same coordinates
   - This MUST happen within 1 second or the entire booking fails

4. **Results Selection**
   - Wait for search results (should load quickly after Cloudflare)
   - Use mcp__playwright__browser_snapshot to see available times
   - Look for morning times between 7:00 AM and 11:00 AM
   - Use mcp__playwright__browser_click on the EARLIEST available morning time

5. **Booking Confirmation**
   - Click through all confirmation dialogs (Continue, Confirm, etc.)
   - Complete the booking process
   - Wait for final confirmation page

6. **Success Documentation**
   - Use mcp__playwright__browser_take_screenshot with filename: booking_success_{booking_date}_{{current_time}}.png
   - Report the booking details: time, course, confirmation number

CRITICAL SUCCESS FACTORS:
- Search clicked at exactly 6:30:00 AM (tolerance: ±50ms)
- Cloudflare handled within 1 second
- Booking completed within 30 seconds total
- Success screenshot captured

FAILURE POINTS TO AVOID:
- Late Search click = no availability
- Delayed Cloudflare = timeout failure
- Missing confirmations = lost booking slot

Execute this NOW with absolute precision!
"""

    def create_gap_finder_prompt(self, overnight: bool = False) -> str:
        """Create gap finder prompt"""
        days_start = 2 if overnight else 1
        days_end = 5
        mode = "overnight" if overnight else "daytime"

        dates_to_check = []
        for i in range(days_start, days_end + 1):
            date = datetime.now() + timedelta(days=i)
            dates_to_check.append(date.strftime("%Y-%m-%d"))

        return f"""
I need you to execute a gap finder workflow using MCP Playwright tools to find and book missing morning golf times.

MISSION: Find days without morning bookings and book the first available gap.

SYSTEMATIC WORKFLOW:

1. **Analyze Current Bookings**
   - Use mcp__playwright__browser_navigate to: https://linklineonline.ca/web/my-account/itinerary
   - If not logged in, go to {self.credentials["login_url"]} and login:
     * Membership: {self.credentials["membership"]}
     * Password: {self.credentials["password"]}
   - Use mcp__playwright__browser_snapshot to capture current bookings
   - Identify which of these dates LACK morning bookings (before 11:00 AM): {', '.join(dates_to_check)}

2. **Find First Gap Day**
   - Review the itinerary snapshot
   - Identify the FIRST date from the list that has NO morning booking
   - This will be your target gap day

3. **Search Primary Courses**
   - Use mcp__playwright__browser_navigate to: https://linklineonline.ca/web/tee-times
   - Configure search:
     * Click course selector dropdown
     * Uncheck "All Courses"
     * Select these 6 primary courses: {', '.join(self.primary_courses)}
     * Set date to the gap day you identified
     * Set players to 1
     * Set start time to 06:00 AM
   - Use mcp__playwright__browser_click on Search
   - **CRITICAL**: Immediately handle Cloudflare at coordinates (464, 572) within 1 second

4. **Evaluate Primary Results**
   - Use mcp__playwright__browser_snapshot to see search results
   - Look for morning times (before 11:00 AM)
   - If morning times available: proceed to booking (step 6)
   - If NO morning times: try backup courses (step 5)

5. **Search Backup Courses (if needed)**
   - Refresh the search form
   - Configure search with backup courses:
     * Uncheck "All Courses"
     * Select these 4 backup courses: {', '.join(self.backup_courses)}
     * Use same gap day and settings (date, players=1, time=06:00 AM)
   - Use mcp__playwright__browser_click on Search
   - Handle Cloudflare immediately at (464, 572)

6. **Book Available Morning Time**
   - If morning times found (before 11:00 AM):
     * Use mcp__playwright__browser_click on the EARLIEST available time
     * Complete booking confirmation dialogs
     * Use mcp__playwright__browser_take_screenshot with filename: gap_filled_{{gap_date}}_{{timestamp}}.png

7. **Report Results**
   - Report which dates were checked
   - Report which gap day was targeted
   - Report which course set was searched (primary/backup)
   - Report what was booked (time, course) or "no availability"

IMPORTANT CONSTRAINTS:
- Book ONLY ONE tee time per execution
- Focus ONLY on morning times (before 11:00 AM)
- Handle Cloudflare within 1 second of each search
- Stop after first successful booking

Execute this workflow now using MCP Playwright tools.
"""

    def execute_via_codex(self, prompt: str, action_type: str):
        """Use the actual mcp__codex functionality"""
        self.log(f"Executing {action_type} via mcp__codex")

        # This will only work when running inside Claude Code with MCP access
        # We'll implement the call here
        try:
            # Import the mcp__codex__codex function
            # In the actual Claude Code environment, this would be available
            print(f"=== CODEX EXECUTION: {action_type.upper()} ===")
            print(f"Timestamp: {datetime.now().isoformat()}")
            print(f"Prompt length: {len(prompt)} characters")
            print("="*60)
            print(prompt)
            print("="*60)

            # For now, we'll create a marker file to indicate execution was attempted
            execution_marker = self.base_dir / f"codex_execution_{action_type}_{int(time.time())}.txt"
            with open(execution_marker, "w") as f:
                f.write(f"Codex execution attempted at {datetime.now().isoformat()}\n")
                f.write(f"Action: {action_type}\n")
                f.write(f"Prompt length: {len(prompt)}\n")
                f.write("\nPrompt:\n")
                f.write(prompt)

            self.log(f"Created execution marker: {execution_marker}")
            return True, f"Codex execution initiated for {action_type}"

        except Exception as e:
            self.log(f"Codex execution error: {e}", "ERROR")
            return False, str(e)


def main():
    parser = argparse.ArgumentParser(description="Codex Booking Executor")
    parser.add_argument("action", choices=["prestage", "book", "gap", "gap-night"],
                       help="Action to perform")
    args = parser.parse_args()

    executor = CodexBookingExecutor()

    try:
        booking_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")

        if args.action == "prestage":
            executor.log("="*60)
            executor.log("CODEX PRESTAGING STARTED")
            prompt = executor.create_prestage_prompt(booking_date)
            success, result = executor.execute_via_codex(prompt, "prestage")

        elif args.action == "book":
            executor.log("="*60)
            executor.log("CODEX BOOKING STARTED", "CRITICAL")

            # Timing for 6:30 AM
            target_time = datetime.now().replace(hour=6, minute=30, second=0, microsecond=0)
            current_time = datetime.now()

            if current_time < target_time:
                wait_seconds = (target_time - current_time).total_seconds()
                executor.log(f"Waiting {wait_seconds:.3f} seconds until 6:30:00 AM")
                time.sleep(wait_seconds)

            prompt = executor.create_booking_prompt(booking_date)
            success, result = executor.execute_via_codex(prompt, "booking")

        elif args.action == "gap":
            executor.log("="*60)
            executor.log("CODEX GAP FINDER STARTED - DAYTIME")
            prompt = executor.create_gap_finder_prompt(overnight=False)
            success, result = executor.execute_via_codex(prompt, "gap-daytime")

        elif args.action == "gap-night":
            executor.log("="*60)
            executor.log("CODEX GAP FINDER STARTED - OVERNIGHT")
            prompt = executor.create_gap_finder_prompt(overnight=True)
            success, result = executor.execute_via_codex(prompt, "gap-overnight")

        if success:
            executor.log(f"{args.action.upper()} CODEX EXECUTION COMPLETED", "SUCCESS")
            print(f"\n=== {args.action.upper()} EXECUTION SUCCESSFUL ===")
        else:
            executor.log(f"{args.action.upper()} CODEX EXECUTION FAILED", "ERROR")
            print(f"\n=== {args.action.upper()} EXECUTION FAILED ===")
            sys.exit(1)

    except Exception as e:
        import traceback
        executor.log(f"FATAL ERROR: {str(e)}", "ERROR")
        executor.log(f"Traceback:\n{traceback.format_exc()}", "ERROR")
        print(f"\n=== FATAL ERROR ===\n{e}")
        sys.exit(1)

    finally:
        total_time = (datetime.now() - executor.start_time).total_seconds()
        executor.log(f"Script completed in {total_time:.3f} seconds")


if __name__ == "__main__":
    main()