#!/usr/bin/env python3
"""
Claude MCP Golf Booking Agent
This script provides the interface between cron and Claude Code's MCP tools
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path

class ClaudeMCPBookingAgent:
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
            "email": "Sid.saini1@gmail.com",
            "password": "160599Golf",
            "login_url": "https://kingvalley.clublink.ca/login"
        }

        # Course priorities (must select exactly 6)
        self.courses = [
            "King Valley",
            "King's Riding",
            "Wyndance",
            "Station Creek South",
            "Diamondback",
            "Station Creek North"  # Updated 6th course
        ]

        # Cloudflare challenge position
        self.cloudflare_coords = (464, 572)

    def log(self, message, level="INFO"):
        """Enhanced logging with levels and detailed timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        elapsed = (datetime.now() - self.start_time).total_seconds()
        log_message = f"[{timestamp}] [{level}] [+{elapsed:.3f}s] {message}"
        print(log_message)

        # Write to multiple log files for redundancy
        log_files = [
            self.log_dir / f"claude_mcp_{datetime.now().strftime('%Y%m%d')}.log",
            self.log_dir / f"claude_{self.start_time.strftime('%Y%m%d_%H%M%S')}.log"
        ]

        for log_file in log_files:
            with open(log_file, "a") as f:
                f.write(log_message + "\n")

    def log_environment(self):
        """Log detailed environment information for debugging"""
        self.log("="*60, "DEBUG")
        self.log("ENVIRONMENT CHECK", "DEBUG")
        self.log(f"Script: {sys.argv[0]}", "DEBUG")
        self.log(f"Arguments: {' '.join(sys.argv[1:])}", "DEBUG")
        self.log(f"Working Directory: {os.getcwd()}", "DEBUG")
        self.log(f"Python Version: {sys.version}", "DEBUG")
        self.log(f"User: {os.environ.get('USER', 'unknown')}", "DEBUG")
        self.log(f"PATH: {os.environ.get('PATH', 'not set')}", "DEBUG")
        self.log(f"Start Time: {self.start_time.isoformat()}", "DEBUG")
        self.log(f"Log Directory: {self.log_dir}", "DEBUG")
        self.log(f"Cron Environment: {os.environ.get('CRON', 'Not from cron')}", "DEBUG")
        self.log("="*60, "DEBUG")

    def create_mcp_instructions(self, action="book", booking_date=None, num_players=1):
        """
        Create structured instructions for Claude Code to execute via MCP tools
        """
        if not booking_date:
            booking_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")

        self.log(f"Creating instructions for action: {action}", "DEBUG")
        self.log(f"Booking date: {booking_date}", "DEBUG")
        self.log(f"Number of players: {num_players}", "DEBUG")

        instructions = {
            "task": "golf_booking",
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "parameters": {
                "booking_date": booking_date,
                "num_players": num_players,
                "time_range": {
                    "start": "07:00",
                    "end": "11:00"
                },
                "prefer_earliest": True
            },
            "credentials": self.credentials,
            "courses": self.courses,
            "workflow": []
        }

        if action == "prestage":
            instructions["workflow"] = [
                {
                    "step": 1,
                    "action": "navigate",
                    "tool": "mcp__playwright__browser_navigate",
                    "params": {"url": self.credentials["login_url"]},
                    "description": "Navigate to login page"
                },
                {
                    "step": 2,
                    "action": "snapshot",
                    "tool": "mcp__playwright__browser_snapshot",
                    "description": "Capture page state"
                },
                {
                    "step": 3,
                    "action": "login",
                    "description": "Analyze login form and enter appropriate credentials",
                    "sub_steps": [
                        "Analyze login form to determine if it requires email or membership number",
                        "If email format required: Use Sid.saini1@gmail.com",
                        "If membership number required: Use 224816",
                        "Type password: 160599Golf",
                        "Click login button"
                    ]
                },
                {
                    "step": 4,
                    "action": "navigate_booking",
                    "description": "Go to Tee Times Plus"
                },
                {
                    "step": 5,
                    "action": "prepare_form",
                    "description": "Fill booking form but don't submit",
                    "details": {
                        "select_courses": self.courses,
                        "set_date": booking_date,
                        "set_players": num_players,
                        "set_time_range": "7:00 AM - 11:00 AM"
                    }
                }
            ]

        elif action == "book":
            instructions["workflow"] = [
                {
                    "step": 1,
                    "action": "verify_ready",
                    "description": "Ensure form is ready"
                },
                {
                    "step": 2,
                    "action": "precise_search",
                    "description": "Click Search at exactly 6:30:00.000",
                    "timing": {
                        "target_time": "06:30:00.000",
                        "tolerance_ms": 50
                    }
                },
                {
                    "step": 3,
                    "action": "cloudflare_handler",
                    "description": "Handle Cloudflare challenge instantly",
                    "critical": True,
                    "timing": {
                        "max_delay_ms": 200,
                        "mouse_coords": self.cloudflare_coords,
                        "strategy": "hover_then_click"
                    }
                },
                {
                    "step": 4,
                    "action": "select_time",
                    "description": "Click first available tee time"
                },
                {
                    "step": 5,
                    "action": "confirm_booking",
                    "description": "Complete the booking"
                },
                {
                    "step": 6,
                    "action": "capture_confirmation",
                    "tool": "mcp__playwright__browser_take_screenshot",
                    "description": "Save confirmation screenshot"
                }
            ]

        return instructions

    def generate_claude_prompt(self, instructions):
        """
        Generate the prompt for Claude Code to execute the booking
        """
        prompt = f"""You are an intelligent golf booking agent. Execute the following booking task using Playwright MCP tools.

CRITICAL: This is a time-sensitive booking that opens at exactly 6:30 AM. Speed and precision are essential.

## Task Details:
{json.dumps(instructions, indent=2)}

## Execution Requirements:

1. **Timing Precision**:
   - For 'book' action, you must click Search at EXACTLY 6:30:00 AM
   - Use system time checks to ensure microsecond precision

2. **Login Adaptation**:
   - Analyze the login form to determine if it requires:
     * Email format: Use Sid.saini1@gmail.com
     * Membership number: Use 224816
   - Password: 160599Golf
   - The system may change between email and membership login, adapt accordingly

3. **Cloudflare Handling**:
   - The challenge appears immediately after clicking Search
   - You MUST move the mouse to coordinates {self.cloudflare_coords} and click
   - This must happen within 200ms or the booking will fail
   - Use mcp__playwright__browser_hover followed by mcp__playwright__browser_click

4. **Course Selection**:
   - You must select exactly 6 courses from the list
   - Use the provided course names in priority order

5. **Adaptive Behavior**:
   - Use browser_snapshot to understand page state
   - Adapt to any UI changes you observe
   - If something fails, try alternative approaches

6. **Success Criteria**:
   - Booking confirmed within 15 seconds of 6:30 AM
   - Screenshot of confirmation saved
   - Earliest available time secured

Begin execution now. Use the Playwright MCP tools to complete this booking."""

        return prompt

    def execute_prestaging(self):
        """
        Execute pre-staging at 6:25 AM
        """
        self.log("="*60)
        self.log("PRE-STAGING PHASE STARTED")
        self.log(f"Target booking date: {(datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')}")
        self.log(f"Courses to select: {', '.join(self.courses)}")
        self.log(f"Number of players: 1")
        self.log(f"Time range: 7:00 AM - 11:00 AM")

        instructions = self.create_mcp_instructions(action="prestage")
        prompt = self.generate_claude_prompt(instructions)

        # Save prompt for Claude Code to read
        prompt_file = self.base_dir / "current_claude_prompt.txt"
        with open(prompt_file, "w") as f:
            f.write(prompt)

        self.log(f"Pre-staging prompt saved to {prompt_file}")
        self.log("Claude Code should now execute the pre-staging workflow")
        self.log(f"Prompt size: {len(prompt)} characters")
        self.log("Waiting for Claude Code to execute...")
        self.log("="*60)

        return prompt_file

    def execute_booking(self):
        """
        Execute booking at exactly 6:30 AM
        """
        self.log("="*60)
        self.log("BOOKING PHASE STARTED", "CRITICAL")
        self.log(f"Current time: {datetime.now().isoformat()}")
        self.log(f"Target time: 6:30:00.000")

        # Wait for exact time if needed
        target_time = datetime.now().replace(hour=6, minute=30, second=0, microsecond=0)
        current_time = datetime.now()

        if current_time < target_time:
            wait_seconds = (target_time - current_time).total_seconds()
            self.log(f"Waiting {wait_seconds:.3f} seconds until 6:30:00 AM")
            time.sleep(wait_seconds)

        instructions = self.create_mcp_instructions(action="book")
        prompt = self.generate_claude_prompt(instructions)

        # Save prompt for Claude Code
        prompt_file = self.base_dir / "current_claude_prompt.txt"
        with open(prompt_file, "w") as f:
            f.write(prompt)

        self.log("EXECUTE NOW! Booking prompt ready for Claude Code", "CRITICAL")
        self.log(f"Prompt saved to {prompt_file}")
        self.log(f"Prompt size: {len(prompt)} characters")
        self.log(f"Execution time: {datetime.now().isoformat()}")
        self.log("Claude Code must handle Cloudflare within 1 second!", "CRITICAL")
        self.log("="*60)

        return prompt_file

    def test_booking_flow(self):
        """
        Test the complete flow without actual booking
        """
        self.log("Starting test booking flow")

        instructions = self.create_mcp_instructions(action="test")
        instructions["workflow"].append({
            "step": "final",
            "action": "abort_before_confirmation",
            "description": "Stop before final booking confirmation"
        })

        prompt = self.generate_claude_prompt(instructions)

        # Save test prompt
        prompt_file = self.base_dir / "test_claude_prompt.txt"
        with open(prompt_file, "w") as f:
            f.write(prompt)

        self.log(f"Test prompt saved to {prompt_file}")

        return prompt_file


def main():
    parser = argparse.ArgumentParser(description="Claude MCP Golf Booking Agent")
    parser.add_argument("action", choices=["prestage", "book", "test"],
                       help="Action to perform")
    parser.add_argument("--date", help="Booking date (YYYY-MM-DD)")
    parser.add_argument("--players", type=int, default=1, help="Number of players")

    args = parser.parse_args()

    agent = ClaudeMCPBookingAgent()

    try:
        if args.action == "prestage":
            prompt_file = agent.execute_prestaging()
            print(f"\n=== PRESTAGING READY ===")
            print(f"Claude Code: Please read and execute: {prompt_file}")

        elif args.action == "book":
            prompt_file = agent.execute_booking()
            print(f"\n=== BOOKING NOW ===")
            print(f"Claude Code: IMMEDIATELY read and execute: {prompt_file}")

        elif args.action == "test":
            prompt_file = agent.test_booking_flow()
            print(f"\n=== TEST MODE ===")
            print(f"Claude Code: Please test the booking flow using: {prompt_file}")

    except Exception as e:
        import traceback
        agent.log(f"ERROR: {str(e)}", "ERROR")
        agent.log(f"Traceback:\n{traceback.format_exc()}", "ERROR")
        agent.log("BOOKING FAILED - Check logs for details", "ERROR")
        sys.exit(1)

    finally:
        agent.log(f"Script completed in {(datetime.now() - agent.start_time).total_seconds():.3f} seconds")
        agent.log("="*60)


if __name__ == "__main__":
    main()