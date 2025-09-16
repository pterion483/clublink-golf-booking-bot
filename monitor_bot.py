#!/usr/bin/env python3
"""
Golf Bot Monitor
Monitors the status of the golf booking system and provides diagnostic information
"""

import os
import sys
import json
import time
import psutil
from datetime import datetime, timedelta
from pathlib import Path

class GolfBotMonitor:
    def __init__(self):
        self.base_dir = Path("/home/dmin1/Golf Tee Times Bot")
        self.log_dir = self.base_dir / "logs"
        self.screenshot_dir = self.base_dir / "screenshots"

        # Key files to monitor
        self.critical_files = [
            "cloudflare_handler.py",
            "ultrafast_bot.py",
            "claude_mcp_booking.py",
            "morning_gap_finder_claude.py",
            "overnight_gap_finder_claude.py",
            "cron_wrapper.sh",
            "CLAUDE.md"
        ]

    def log(self, message, level="INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)

        # Write to monitor log
        monitor_log = self.log_dir / f"monitor_{datetime.now().strftime('%Y%m%d')}.log"
        with open(monitor_log, "a") as f:
            f.write(log_message + "\n")

    def check_system_health(self):
        """Check overall system health"""
        self.log("="*60)
        self.log("GOLF BOT SYSTEM HEALTH CHECK")
        self.log("="*60)

        health_status = {
            "timestamp": datetime.now().isoformat(),
            "files": {},
            "logs": {},
            "system": {},
            "cron": {},
            "overall_status": "UNKNOWN"
        }

        # Check critical files
        self.log("Checking critical files...")
        for file_name in self.critical_files:
            file_path = self.base_dir / file_name
            if file_path.exists():
                stat = file_path.stat()
                health_status["files"][file_name] = {
                    "exists": True,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "executable": os.access(file_path, os.X_OK)
                }
                self.log(f"✓ {file_name} - {stat.st_size} bytes, modified {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                health_status["files"][file_name] = {"exists": False}
                self.log(f"✗ {file_name} - MISSING", "ERROR")

        # Check log directory and recent logs
        self.log("\nChecking logs...")
        if self.log_dir.exists():
            log_files = list(self.log_dir.glob("*.log"))
            health_status["logs"]["total_files"] = len(log_files)

            # Check for recent activity
            today = datetime.now().strftime("%Y%m%d")
            recent_logs = [f for f in log_files if today in f.name]
            health_status["logs"]["today_files"] = len(recent_logs)

            self.log(f"✓ Log directory exists - {len(log_files)} total files, {len(recent_logs)} from today")

            # Check last booking attempt
            booking_logs = list(self.log_dir.glob("*booking*.log"))
            if booking_logs:
                latest_booking_log = max(booking_logs, key=lambda f: f.stat().st_mtime)
                health_status["logs"]["last_booking_attempt"] = datetime.fromtimestamp(latest_booking_log.stat().st_mtime).isoformat()
                self.log(f"✓ Last booking attempt: {datetime.fromtimestamp(latest_booking_log.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                health_status["logs"]["last_booking_attempt"] = None
                self.log("⚠ No booking logs found", "WARN")
        else:
            health_status["logs"]["error"] = "Log directory missing"
            self.log("✗ Log directory missing", "ERROR")

        # Check system resources
        self.log("\nChecking system resources...")
        health_status["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else None
        }

        self.log(f"✓ CPU: {health_status['system']['cpu_percent']:.1f}%")
        self.log(f"✓ Memory: {health_status['system']['memory_percent']:.1f}%")
        self.log(f"✓ Disk: {health_status['system']['disk_percent']:.1f}%")

        # Check for running processes
        booking_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(keyword in cmdline.lower() for keyword in ['golf', 'booking', 'claude_mcp', 'ultrafast']):
                    booking_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        health_status["system"]["booking_processes"] = booking_processes
        if booking_processes:
            self.log(f"⚠ Found {len(booking_processes)} potentially related processes running", "WARN")
            for proc in booking_processes:
                self.log(f"  PID {proc['pid']}: {proc['cmdline']}")
        else:
            self.log("✓ No booking processes currently running")

        # Check cron status
        self.log("\nChecking cron configuration...")
        try:
            import subprocess
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                cron_lines = result.stdout.strip().split('\n')
                golf_cron_lines = [line for line in cron_lines if 'golf' in line.lower() or 'booking' in line.lower()]
                health_status["cron"]["total_entries"] = len(cron_lines)
                health_status["cron"]["golf_entries"] = len(golf_cron_lines)
                health_status["cron"]["configured"] = True

                self.log(f"✓ Cron configured - {len(cron_lines)} total entries, {len(golf_cron_lines)} golf-related")
                for line in golf_cron_lines:
                    self.log(f"  {line}")
            else:
                health_status["cron"]["configured"] = False
                self.log("✗ No cron entries found", "WARN")
        except Exception as e:
            health_status["cron"]["error"] = str(e)
            self.log(f"✗ Error checking cron: {e}", "ERROR")

        # Determine overall status
        critical_files_missing = sum(1 for f in self.critical_files if not (self.base_dir / f).exists())
        if critical_files_missing == 0:
            if health_status["logs"].get("today_files", 0) > 0:
                health_status["overall_status"] = "HEALTHY"
            else:
                health_status["overall_status"] = "IDLE"
        else:
            health_status["overall_status"] = "DEGRADED"

        self.log(f"\nOVERALL STATUS: {health_status['overall_status']}")

        return health_status

    def check_next_booking_time(self):
        """Check when the next booking is scheduled"""
        self.log("\nChecking next booking schedule...")

        # Calculate next 6:30 AM
        now = datetime.now()
        tomorrow_630 = (now + timedelta(days=1)).replace(hour=6, minute=30, second=0, microsecond=0)

        # If it's before 6:30 AM today, next booking is today
        if now.hour < 6 or (now.hour == 6 and now.minute < 30):
            next_booking = now.replace(hour=6, minute=30, second=0, microsecond=0)
        else:
            next_booking = tomorrow_630

        time_until = next_booking - now
        hours, remainder = divmod(time_until.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        self.log(f"Next booking: {next_booking.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"Time until booking: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")

        return {
            "next_booking": next_booking.isoformat(),
            "time_until_seconds": time_until.total_seconds(),
            "time_until_formatted": f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        }

    def tail_recent_logs(self, lines=20):
        """Show recent log entries"""
        self.log(f"\nShowing last {lines} log entries...")

        log_files = []
        if self.log_dir.exists():
            # Get all log files modified in the last 24 hours
            cutoff = datetime.now() - timedelta(hours=24)
            for log_file in self.log_dir.glob("*.log"):
                if datetime.fromtimestamp(log_file.stat().st_mtime) > cutoff:
                    log_files.append(log_file)

        if not log_files:
            self.log("No recent log files found")
            return

        # Sort by modification time
        log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        # Show entries from most recent log file
        recent_log = log_files[0]
        self.log(f"Reading from: {recent_log.name}")

        try:
            with open(recent_log, 'r') as f:
                lines_list = f.readlines()
                recent_lines = lines_list[-lines:] if len(lines_list) > lines else lines_list

                for line in recent_lines:
                    print(f"  {line.rstrip()}")

        except Exception as e:
            self.log(f"Error reading log file: {e}", "ERROR")

    def run_full_monitor(self):
        """Run complete monitoring check"""
        self.log("Starting comprehensive golf bot monitoring...")

        # System health check
        health = self.check_system_health()

        # Next booking time
        booking_info = self.check_next_booking_time()

        # Recent logs
        self.tail_recent_logs()

        # Summary
        self.log("\n" + "="*60)
        self.log("MONITORING SUMMARY")
        self.log("="*60)
        self.log(f"Overall Status: {health['overall_status']}")
        self.log(f"Critical Files: {len([f for f in health['files'].values() if f.get('exists')])}/{len(self.critical_files)}")
        self.log(f"Next Booking: {booking_info['time_until_formatted']}")
        self.log(f"System Load: CPU {health['system']['cpu_percent']:.1f}%, Memory {health['system']['memory_percent']:.1f}%")

        # Save status to file
        status_file = self.base_dir / "bot_status.json"
        with open(status_file, 'w') as f:
            json.dump({
                "health": health,
                "booking": booking_info,
                "last_check": datetime.now().isoformat()
            }, f, indent=2)

        self.log(f"Status saved to: {status_file}")

        return health['overall_status'] == "HEALTHY"

def main():
    """Main entry point"""
    monitor = GolfBotMonitor()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "health":
            health = monitor.check_system_health()
            sys.exit(0 if health['overall_status'] in ['HEALTHY', 'IDLE'] else 1)

        elif command == "logs":
            lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            monitor.tail_recent_logs(lines)

        elif command == "next":
            monitor.check_next_booking_time()

        elif command == "full":
            success = monitor.run_full_monitor()
            sys.exit(0 if success else 1)

        else:
            print("Usage: monitor_bot.py {health|logs|next|full}")
            print("  health - Check system health")
            print("  logs [N] - Show last N log entries (default 20)")
            print("  next - Show next booking time")
            print("  full - Complete monitoring check")
            sys.exit(1)
    else:
        # Default: run full monitoring
        success = monitor.run_full_monitor()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()