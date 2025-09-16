#!/usr/bin/env python3
"""
Direct MCP Executor - Uses mcp__codex for true automation
This script runs inside Claude Code and directly executes MCP Playwright commands
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

class DirectMCPExecutor:
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
        """Enhanced logging"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        elapsed = (datetime.now() - self.start_time).total_seconds()
        log_message = f"[{timestamp}] [{level}] [+{elapsed:.3f}s] {message}"
        print(log_message)

        log_file = self.log_dir / f"direct_mcp_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, "a") as f:
            f.write(log_message + "\n")

    def execute_direct_booking_via_subprocess(self, action: str):
        """Execute booking automation by calling Claude Code as subprocess with MCP tools"""
        self.log(f"Executing {action} via Claude Code subprocess")

        booking_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")

        if action == "prestage":
            prompt = f"""
Execute golf booking pre-staging using MCP Playwright tools. This prepares for tomorrow's 6:30 AM booking.

Use these steps:
1. mcp__playwright__browser_navigate to: {self.credentials["login_url"]}
2. mcp__playwright__browser_type membership: {self.credentials["membership"]}
3. mcp__playwright__browser_type password: {self.credentials["password"]}
4. mcp__playwright__browser_click login button
5. mcp__playwright__browser_click "Tee Times Plus"
6. Set date to {booking_date}, players to 1
7. Select courses: {', '.join(self.primary_courses)}
8. DO NOT click Search - leave ready for 6:30 AM
9. mcp__playwright__browser_take_screenshot of ready state

Report pre-staging complete when form is ready.
"""

        elif action == "book":
            prompt = f"""
Execute time-critical golf booking using MCP Playwright tools at exactly 6:30:00 AM.

Critical workflow:
1. mcp__playwright__browser_snapshot to verify form ready
2. At exactly 6:30:00 AM: mcp__playwright__browser_click Search button
3. IMMEDIATELY mcp__playwright__browser_hover at (464, 572) for Cloudflare
4. IMMEDIATELY mcp__playwright__browser_click at (464, 572) within 1 second
5. mcp__playwright__browser_click on earliest morning time (before 11:00 AM)
6. Complete booking confirmation
7. mcp__playwright__browser_take_screenshot of success

CRITICAL: Cloudflare must be handled within 1 second or booking fails!
"""

        elif action in ["gap", "gap-night"]:
            days_range = range(2, 6) if action == "gap-night" else range(1, 6)
            dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in days_range]

            prompt = f"""
Execute gap finder using MCP Playwright tools to find and book missing morning times.

Workflow:
1. mcp__playwright__browser_navigate to: https://linklineonline.ca/web/my-account/itinerary
2. Login if needed: {self.credentials["membership"]} / {self.credentials["password"]}
3. mcp__playwright__browser_snapshot to see current bookings
4. Identify dates without morning bookings: {', '.join(dates)}
5. For first gap found:
   - mcp__playwright__browser_navigate to: https://linklineonline.ca/web/tee-times
   - Select primary courses: {', '.join(self.primary_courses)}
   - mcp__playwright__browser_click Search
   - mcp__playwright__browser_hover and click (464, 572) for Cloudflare
   - If no morning times, try backup courses: {', '.join(self.backup_courses)}
6. mcp__playwright__browser_click on earliest morning time if available
7. Complete booking and mcp__playwright__browser_take_screenshot

Book only ONE time per execution. Focus on times before 11:00 AM.
"""

        # Write prompt to file for debugging
        prompt_file = self.base_dir / f"{action}_direct_prompt.txt"
        with open(prompt_file, "w") as f:
            f.write(prompt)

        try:
            # Execute Claude Code with the prompt
            cmd = [
                "claude",
                "--print",
                "--model", "sonnet",
                "--dangerously-skip-permissions",
                prompt
            ]

            self.log(f"Executing command: claude --print --model sonnet [prompt]")

            result = subprocess.run(
                cmd,
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            self.log(f"Claude execution completed with exit code: {result.returncode}")

            if result.stdout:
                self.log(f"Claude output: {result.stdout[:500]}...")

                # Save full output
                output_file = self.base_dir / f"{action}_execution_output.txt"
                with open(output_file, "w") as f:
                    f.write(f"Execution timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"Action: {action}\n")
                    f.write(f"Exit code: {result.returncode}\n")
                    f.write("="*60 + "\n")
                    f.write("STDOUT:\n")
                    f.write(result.stdout)
                    f.write("\n" + "="*60 + "\n")
                    f.write("STDERR:\n")
                    f.write(result.stderr)

            if result.stderr:
                self.log(f"Claude errors: {result.stderr}", "ERROR")

            return result.returncode == 0, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            self.log("Claude execution timed out", "ERROR")
            return False, "", "Execution timed out"
        except Exception as e:
            self.log(f"Error executing Claude: {e}", "ERROR")
            return False, "", str(e)

    def execute_prestaging(self) -> bool:
        """Execute pre-staging"""
        self.log("="*60)
        self.log("DIRECT MCP PRE-STAGING STARTED")

        success, output, error = self.execute_direct_booking_via_subprocess("prestage")

        if success:
            self.log("Pre-staging completed successfully", "SUCCESS")
        else:
            self.log("Pre-staging failed", "ERROR")
            self.log(f"Error: {error}", "ERROR")

        self.log("="*60)
        return success

    def execute_booking(self) -> bool:
        """Execute booking with precise timing"""
        self.log("="*60)
        self.log("DIRECT MCP BOOKING STARTED", "CRITICAL")

        # Wait for 6:30 AM if needed
        target_time = datetime.now().replace(hour=6, minute=30, second=0, microsecond=0)
        current_time = datetime.now()

        if current_time < target_time:
            wait_seconds = (target_time - current_time).total_seconds()
            self.log(f"Waiting {wait_seconds:.3f} seconds until 6:30:00 AM")
            time.sleep(wait_seconds)

        success, output, error = self.execute_direct_booking_via_subprocess("book")

        if success:
            self.log("BOOKING COMPLETED SUCCESSFULLY!", "SUCCESS")
        else:
            self.log("BOOKING FAILED!", "ERROR")
            self.log(f"Error: {error}", "ERROR")

        self.log("="*60)
        return success

    def execute_gap_finder(self, overnight: bool = False) -> bool:
        """Execute gap finder"""
        mode = "gap-night" if overnight else "gap"
        self.log("="*60)
        self.log(f"DIRECT MCP GAP FINDER STARTED - {mode.upper()}")

        success, output, error = self.execute_direct_booking_via_subprocess(mode)

        if success:
            self.log(f"Gap finder ({mode}) completed successfully", "SUCCESS")
        else:
            self.log(f"Gap finder ({mode}) failed", "ERROR")
            self.log(f"Error: {error}", "ERROR")

        self.log("="*60)
        return success


def main():
    parser = argparse.ArgumentParser(description="Direct MCP Executor")
    parser.add_argument("action", choices=["prestage", "book", "gap", "gap-night"],
                       help="Action to perform")
    args = parser.parse_args()

    executor = DirectMCPExecutor()

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
            print(f"\n=== {args.action.upper()} EXECUTION SUCCESSFUL ===")
        else:
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