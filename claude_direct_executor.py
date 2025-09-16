#!/usr/bin/env python3
"""
Claude Direct MCP Executor
This script directly executes Claude Code with MCP tools instead of generating prompts.
Uses the mcp__codex functionality to run booking automation directly.
"""

import os
import sys
import json
import time
import argparse
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

class ClaudeDirectExecutor:
    def __init__(self):
        self.base_dir = Path("/home/dmin1/Golf Tee Times Bot")
        self.log_dir = self.base_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)

        # Enhanced logging setup
        self.debug_mode = os.environ.get('DEBUG', 'true').lower() == 'true'
        self.start_time = datetime.now()
        self.log_environment()

        # Booking configuration
        self.credentials = {
            "membership": "224816",
            "password": "160599Golf",
            "login_url": "https://kingvalley.clublink.ca/login"
        }

        # Course priorities (exactly 6)
        self.primary_courses = [
            "King Valley",
            "King's Riding",
            "Wyndance",
            "Station Creek South",
            "Diamondback",
            "Station Creek North"
        ]

        self.backup_courses = [
            "Emerald Hills T1",
            "Emerald Hills T10",
            "Emerald Hills T19",
            "Caledon Woods"
        ]

    def log(self, message, level="INFO"):
        """Enhanced logging with levels and detailed timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        elapsed = (datetime.now() - self.start_time).total_seconds()
        log_message = f"[{timestamp}] [{level}] [+{elapsed:.3f}s] {message}"
        print(log_message)

        # Write to log files
        log_files = [
            self.log_dir / f"claude_direct_{datetime.now().strftime('%Y%m%d')}.log",
            self.log_dir / f"direct_{self.start_time.strftime('%Y%m%d_%H%M%S')}.log"
        ]

        for log_file in log_files:
            with open(log_file, "a") as f:
                f.write(log_message + "\n")

    def log_environment(self):
        """Log detailed environment information for debugging"""
        self.log("="*60, "DEBUG")
        self.log("CLAUDE DIRECT EXECUTOR STARTING", "DEBUG")
        self.log(f"Script: {sys.argv[0]}", "DEBUG")
        self.log(f"Arguments: {' '.join(sys.argv[1:])}", "DEBUG")
        self.log(f"Working Directory: {os.getcwd()}", "DEBUG")
        self.log(f"Start Time: {self.start_time.isoformat()}", "DEBUG")
        self.log("="*60, "DEBUG")

    def execute_via_claude_cli(self, prompt, session_name="booking"):
        """
        Execute a prompt directly via Claude CLI with MCP tools
        """
        self.log(f"Executing via Claude CLI - Session: {session_name}")

        try:
            # Create a temporary file for the prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name

            # Construct Claude command
            claude_cmd = [
                "claude",
                "--print",
                "--model", "sonnet",
                "--dangerously-skip-permissions",
                "--session-id", f"golf-{session_name}-{int(time.time())}",
                prompt
            ]

            self.log(f"Running command: {' '.join(claude_cmd[:4])} [prompt]")

            # Execute Claude command
            result = subprocess.run(
                claude_cmd,
                capture_output=True,
                text=True,
                cwd=str(self.base_dir),
                timeout=300  # 5 minute timeout
            )

            # Clean up temp file
            os.unlink(prompt_file)

            self.log(f"Claude CLI exit code: {result.returncode}")
            if result.stdout:
                self.log(f"Claude CLI output: {result.stdout[:500]}...")
            if result.stderr:
                self.log(f"Claude CLI errors: {result.stderr}", "ERROR")

            return result.returncode == 0, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            self.log("Claude CLI execution timed out", "ERROR")
            return False, "", "Execution timed out"
        except Exception as e:
            self.log(f"Error executing Claude CLI: {e}", "ERROR")
            return False, "", str(e)

    def create_booking_prompt(self, action="book", booking_date=None, num_players=1):
        """
        Create a comprehensive booking prompt for direct MCP execution
        """
        if not booking_date:
            booking_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")

        self.log(f"Creating booking prompt for action: {action}")

        if action == "prestage":
            prompt = f"""
You are an expert golf booking automation agent. Execute the following pre-staging workflow using MCP Playwright tools.

**TASK: Pre-stage booking form for tomorrow's 6:30 AM execution**

**WORKFLOW:**

1. **Navigate and Login**
   - Use mcp__playwright__browser_navigate to go to: {self.credentials["login_url"]}
   - Take a snapshot with mcp__playwright__browser_snapshot
   - Enter membership number: {self.credentials["membership"]}
   - Enter password: {self.credentials["password"]}
   - Click login button

2. **Navigate to Booking**
   - Click "Tee Times Plus" link (opens new tab)
   - Use mcp__playwright__browser_tabs to manage tabs if needed

3. **Pre-fill Booking Form (DO NOT SUBMIT)**
   - Set date to: {booking_date}
   - Set number of players: {num_players}
   - Click course selector and uncheck "All Courses"
   - Select these 6 courses: {', '.join(self.primary_courses)}
   - Set time range starting from 7:00 AM
   - Take a screenshot to confirm form is ready

4. **Final State**
   - Ensure the form is completely filled but NOT submitted
   - The Search button should be ready to click at exactly 6:30:00 AM
   - Take a final screenshot showing the ready state

**CRITICAL REQUIREMENTS:**
- Do NOT click the Search button
- Leave the browser in the pre-staged state
- Form must be completely filled and ready
- Take screenshots at each major step for verification

Begin execution now using the MCP Playwright tools.
"""

        elif action == "book":
            prompt = f"""
You are an expert golf booking automation agent. Execute this CRITICAL TIME-SENSITIVE booking using MCP Playwright tools.

**URGENT: This must execute at EXACTLY 6:30:00 AM with microsecond precision!**

**WORKFLOW:**

1. **Verify Ready State**
   - Take snapshot with mcp__playwright__browser_snapshot
   - Ensure booking form is pre-filled and ready
   - Confirm Search button is visible and clickable

2. **CRITICAL TIMING - Execute at 6:30:00.000 AM**
   - Wait until exactly 6:30:00.000 AM system time
   - Click the Search button IMMEDIATELY at target time
   - Use mcp__playwright__browser_click on the Search button

3. **IMMEDIATE Cloudflare Handling**
   - Within 200ms of clicking Search, Cloudflare challenge will appear
   - Use mcp__playwright__browser_hover at coordinates (464, 572)
   - Immediately follow with mcp__playwright__browser_click at same coordinates
   - This MUST happen within 1 second or booking fails

4. **Select and Book**
   - Wait for search results to load
   - Take snapshot to see available times
   - Click on the EARLIEST morning time (before 11:00 AM)
   - Click Continue/Confirm buttons to complete booking

5. **Capture Success**
   - Take final screenshot with mcp__playwright__browser_take_screenshot
   - Save as "booking_success_{booking_date}_{timestamp}.png"

**CRITICAL TIMING REQUIREMENTS:**
- Search click at exactly 6:30:00 AM
- Cloudflare click within 1 second
- Complete booking within 30 seconds total

Begin execution NOW! Speed is essential!
"""

        elif action == "gap_finder":
            dates_to_check = []
            for i in range(1, 6):  # Check days 1-5 ahead
                date = datetime.now() + timedelta(days=i)
                dates_to_check.append(date.strftime("%Y-%m-%d"))

            prompt = f"""
You are an intelligent gap finder for golf bookings. Execute this workflow using MCP Playwright tools.

**TASK: Find and book morning gaps in existing bookings**

**WORKFLOW:**

1. **Check Current Bookings**
   - Navigate to https://linklineonline.ca/web/my-account/itinerary
   - Login if needed: {self.credentials["membership"]} / {self.credentials["password"]}
   - Take snapshot and identify all existing bookings
   - Create a list of dates that LACK morning bookings (before 11:00 AM)

2. **Find Gap Days**
   - Check these dates: {', '.join(dates_to_check)}
   - Identify which dates have NO morning booking

3. **Search for Morning Times (Primary Courses)**
   - For the FIRST gap day found:
   - Navigate to https://linklineonline.ca/web/tee-times
   - Configure search:
     * Uncheck "All Courses"
     * Select: {', '.join(self.primary_courses)}
     * Set date to gap day
     * Set players: 1
     * Set time: 06:00 AM
   - Click Search
   - **CRITICAL**: Handle Cloudflare immediately at (464, 572)

4. **Check Results and Try Backup if Needed**
   - If NO morning times with primary courses:
     * Clear search and try backup courses: {', '.join(self.backup_courses)}
     * Use same date and settings
     * Click Search and handle Cloudflare

5. **Book if Available**
   - If morning times found (before 11:00 AM):
     * Click EARLIEST available time
     * Complete booking confirmation
     * Take success screenshot

6. **Report Results**
   - Report what was checked, found, and booked
   - Only book ONE time per execution

**IMPORTANT:**
- Handle Cloudflare within 1 second of each search
- Only morning times before 11:00 AM
- Book only one tee time to avoid overbooking

Execute this workflow now using MCP Playwright tools.
"""

        else:
            raise ValueError(f"Unknown action: {action}")

        return prompt

    def execute_prestaging(self):
        """Execute pre-staging directly via MCP"""
        self.log("="*60)
        self.log("DIRECT PRE-STAGING EXECUTION STARTED")

        booking_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        prompt = self.create_booking_prompt(action="prestage", booking_date=booking_date)

        success, output, error = self.execute_via_claude_cli(prompt, "prestage")

        if success:
            self.log("Pre-staging completed successfully", "SUCCESS")
        else:
            self.log("Pre-staging failed", "ERROR")
            self.log(f"Error: {error}", "ERROR")

        self.log("="*60)
        return success

    def execute_booking(self):
        """Execute booking directly via MCP"""
        self.log("="*60)
        self.log("DIRECT BOOKING EXECUTION STARTED", "CRITICAL")

        # Wait for exact timing if needed
        target_time = datetime.now().replace(hour=6, minute=30, second=0, microsecond=0)
        current_time = datetime.now()

        if current_time < target_time:
            wait_seconds = (target_time - current_time).total_seconds()
            self.log(f"Waiting {wait_seconds:.3f} seconds until 6:30:00 AM")
            time.sleep(wait_seconds)

        booking_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        prompt = self.create_booking_prompt(action="book", booking_date=booking_date)

        success, output, error = self.execute_via_claude_cli(prompt, "booking")

        if success:
            self.log("BOOKING COMPLETED SUCCESSFULLY!", "SUCCESS")
        else:
            self.log("BOOKING FAILED!", "ERROR")
            self.log(f"Error: {error}", "ERROR")

        self.log("="*60)
        return success

    def execute_gap_finder(self, overnight=False):
        """Execute gap finder directly via MCP"""
        mode = "overnight" if overnight else "daytime"
        self.log("="*60)
        self.log(f"DIRECT GAP FINDER EXECUTION STARTED - {mode.upper()}")

        prompt = self.create_booking_prompt(action="gap_finder")

        success, output, error = self.execute_via_claude_cli(prompt, f"gap-{mode}")

        if success:
            self.log(f"Gap finder ({mode}) completed successfully", "SUCCESS")
        else:
            self.log(f"Gap finder ({mode}) failed", "ERROR")
            self.log(f"Error: {error}", "ERROR")

        self.log("="*60)
        return success


def main():
    parser = argparse.ArgumentParser(description="Claude Direct MCP Executor")
    parser.add_argument("action", choices=["prestage", "book", "gap", "gap-night"],
                       help="Action to perform")
    parser.add_argument("--date", help="Booking date (YYYY-MM-DD)")
    parser.add_argument("--players", type=int, default=1, help="Number of players")

    args = parser.parse_args()

    executor = ClaudeDirectExecutor()

    try:
        if args.action == "prestage":
            success = executor.execute_prestaging()
        elif args.action == "book":
            success = executor.execute_booking()
        elif args.action == "gap":
            success = executor.execute_gap_finder(overnight=False)
        elif args.action == "gap-night":
            success = executor.execute_gap_finder(overnight=True)

        if success:
            print("\n=== EXECUTION SUCCESSFUL ===")
            executor.log("Direct execution completed successfully", "SUCCESS")
        else:
            print("\n=== EXECUTION FAILED ===")
            executor.log("Direct execution failed", "ERROR")
            sys.exit(1)

    except Exception as e:
        import traceback
        executor.log(f"FATAL ERROR: {str(e)}", "ERROR")
        executor.log(f"Traceback:\n{traceback.format_exc()}", "ERROR")
        print(f"\n=== FATAL ERROR ===\n{e}")
        sys.exit(1)

    finally:
        executor.log(f"Script completed in {(datetime.now() - executor.start_time).total_seconds():.3f} seconds")


if __name__ == "__main__":
    main()