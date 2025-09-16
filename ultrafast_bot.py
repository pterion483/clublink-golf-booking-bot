#!/usr/bin/env python3
"""
Ultrafast Golf Booking Bot
Main booking bot that runs at 6:30 AM for precise tee time booking
Integrates with cloudflare_handler for instant challenge resolution
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# Import selenium for web automation
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Import local cloudflare handler
try:
    from cloudflare_handler import CloudflareHandler
    CLOUDFLARE_HANDLER_AVAILABLE = True
except ImportError:
    CLOUDFLARE_HANDLER_AVAILABLE = False

class UltrafastGolfBot:
    def __init__(self):
        self.base_dir = Path("/home/dmin1/Golf Tee Times Bot")
        self.log_dir = self.base_dir / "logs"
        self.screenshot_dir = self.base_dir / "screenshots"

        # Create directories
        self.log_dir.mkdir(exist_ok=True)
        self.screenshot_dir.mkdir(exist_ok=True)

        # Booking configuration
        self.credentials = {
            "membership": "224816",
            "password": "160599Golf",
            "login_url": "https://kingvalley.clublink.ca/login"
        }

        # Course selection (exactly 6 required)
        self.courses = [
            "King Valley",
            "King's Riding",
            "Wyndance",
            "Station Creek South",
            "Diamondback",
            "Station Creek North"
        ]

        # Timing configuration
        self.target_time = "06:30:00"
        self.cloudflare_coords = (464, 572)

        # Browser setup
        self.driver = None
        self.cloudflare_handler = None

    def log(self, message, level="INFO"):
        """Enhanced logging with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)

        # Also write to log file
        log_file = self.log_dir / f"ultrafast_bot_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, "a") as f:
            f.write(log_message + "\n")

    def setup_browser(self):
        """Setup Chrome browser with optimal settings for speed"""
        if not SELENIUM_AVAILABLE:
            self.log("ERROR: Selenium not available. Install with: pip install selenium", "ERROR")
            return False

        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Faster loading
            chrome_options.add_argument("--window-size=1920,1080")

            # Headless mode for production
            if os.environ.get('HEADLESS', 'true').lower() == 'true':
                chrome_options.add_argument("--headless")

            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)

            # Setup Cloudflare handler
            if CLOUDFLARE_HANDLER_AVAILABLE:
                self.cloudflare_handler = CloudflareHandler(self.driver)

            self.log("Browser setup completed successfully")
            return True

        except Exception as e:
            self.log(f"ERROR setting up browser: {e}", "ERROR")
            return False

    def login(self):
        """Login to ClubLink"""
        try:
            self.log("Navigating to login page")
            self.driver.get(self.credentials["login_url"])

            # Wait for and fill membership number
            membership_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "membership"))
            )
            membership_field.clear()
            membership_field.send_keys(self.credentials["membership"])

            # Fill password
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(self.credentials["password"])

            # Click login
            login_button = self.driver.find_element(By.XPATH, "//input[@type='submit' or @type='button']")
            login_button.click()

            # Wait for successful login
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Tee Times"))
            )

            self.log("Login successful")
            return True

        except Exception as e:
            self.log(f"ERROR during login: {e}", "ERROR")
            return False

    def navigate_to_booking(self):
        """Navigate to Tee Times Plus booking system"""
        try:
            self.log("Navigating to Tee Times Plus")

            # Click Tee Times Plus link
            tee_times_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Tee Times Plus"))
            )
            tee_times_link.click()

            # Switch to new tab/window if opened
            if len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.log("Switched to Tee Times Plus window")

            # Wait for booking form to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "search") or (By.XPATH, "//input[@value='Search']"))
            )

            self.log("Successfully navigated to booking system")
            return True

        except Exception as e:
            self.log(f"ERROR navigating to booking system: {e}", "ERROR")
            return False

    def setup_booking_form(self, booking_date=None, num_players=1):
        """Setup the booking form with desired parameters"""
        try:
            if not booking_date:
                booking_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")

            self.log(f"Setting up booking form for {booking_date}, {num_players} players")

            # Set date
            date_field = self.driver.find_element(By.NAME, "date")
            date_field.clear()
            date_field.send_keys(booking_date)

            # Set number of players
            players_field = self.driver.find_element(By.NAME, "players")
            players_field.clear()
            players_field.send_keys(str(num_players))

            # Select courses (exactly 6 required)
            self.log(f"Selecting courses: {', '.join(self.courses)}")
            for course in self.courses:
                try:
                    course_checkbox = self.driver.find_element(By.XPATH, f"//input[@type='checkbox']/..//text()[contains(., '{course}')]/../input")
                    if not course_checkbox.is_selected():
                        course_checkbox.click()
                        self.log(f"Selected course: {course}")
                except Exception as e:
                    self.log(f"WARNING: Could not select course {course}: {e}", "WARN")

            # Set time range (7:00 AM - 11:00 AM)
            try:
                start_time = self.driver.find_element(By.NAME, "start_time")
                start_time.clear()
                start_time.send_keys("07:00")

                end_time = self.driver.find_element(By.NAME, "end_time")
                end_time.clear()
                end_time.send_keys("11:00")
            except:
                self.log("Could not set specific time range, using defaults", "WARN")

            self.log("Booking form setup completed")
            return True

        except Exception as e:
            self.log(f"ERROR setting up booking form: {e}", "ERROR")
            return False

    def wait_for_exact_time(self, target_time="06:30:00"):
        """Wait until exactly the target time to click search"""
        self.log(f"Waiting for exact time: {target_time}")

        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            current_ms = datetime.now().strftime("%H:%M:%S.%f")[:-3]

            if current_time == target_time:
                self.log(f"TARGET TIME REACHED: {current_ms}")
                return True

            time.sleep(0.001)  # Check every millisecond

    def execute_search_with_cloudflare_handling(self):
        """Execute search and immediately handle Cloudflare challenge"""
        try:
            start_time = time.time()
            self.log("EXECUTING SEARCH - CRITICAL TIMING PHASE")

            # Find and click search button
            search_button = self.driver.find_element(By.XPATH, "//input[@value='Search' or @type='submit']")
            search_button.click()

            click_time = (time.time() - start_time) * 1000
            self.log(f"Search button clicked in {click_time:.1f}ms")

            # IMMEDIATELY handle Cloudflare challenge
            if self.cloudflare_handler:
                self.log("Invoking Cloudflare handler")
                success = self.cloudflare_handler.wait_and_handle_challenge(timeout=3)
                if success:
                    self.log("Cloudflare challenge handled successfully")
                else:
                    self.log("WARNING: Cloudflare challenge handling failed", "WARN")
            else:
                # Fallback: direct coordinate click
                self.log("Using fallback Cloudflare handling")
                time.sleep(0.5)  # Brief wait for challenge to appear
                actions = ActionChains(self.driver)
                actions.move_by_offset(self.cloudflare_coords[0], self.cloudflare_coords[1])
                actions.click()
                actions.perform()

            total_time = (time.time() - start_time) * 1000
            self.log(f"Search + Cloudflare handling completed in {total_time:.1f}ms")

            return True

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            self.log(f"ERROR in search/Cloudflare phase ({elapsed:.1f}ms): {e}", "ERROR")
            return False

    def select_first_available_time(self):
        """Select the first available tee time"""
        try:
            self.log("Searching for available tee times")

            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'book')] | //button[contains(text(), 'Book')]"))
            )

            # Find first available booking link/button
            booking_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'book')] | //button[contains(text(), 'Book')]")

            if booking_elements:
                first_slot = booking_elements[0]
                slot_text = first_slot.text or first_slot.get_attribute("title") or "Unknown time"
                self.log(f"Selecting first available slot: {slot_text}")
                first_slot.click()
                return True
            else:
                self.log("ERROR: No available tee times found", "ERROR")
                return False

        except Exception as e:
            self.log(f"ERROR selecting tee time: {e}", "ERROR")
            return False

    def confirm_booking(self):
        """Confirm the booking"""
        try:
            self.log("Confirming booking")

            # Look for confirmation button
            confirm_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='Confirm'] | //button[contains(text(), 'Confirm')]"))
            )
            confirm_button.click()

            # Wait for booking confirmation
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'confirmed') or contains(text(), 'booked')]"))
            )

            self.log("BOOKING CONFIRMED SUCCESSFULLY!")

            # Take confirmation screenshot
            screenshot_path = self.screenshot_dir / f"booking_confirmed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(str(screenshot_path))
            self.log(f"Confirmation screenshot saved: {screenshot_path}")

            return True

        except Exception as e:
            self.log(f"ERROR confirming booking: {e}", "ERROR")
            return False

    def run_ultrafast_booking(self):
        """Main booking execution method"""
        self.log("="*60)
        self.log("ULTRAFAST GOLF BOOKING BOT STARTED")
        self.log(f"Target time: {self.target_time}")
        self.log(f"Courses: {', '.join(self.courses)}")
        self.log("="*60)

        try:
            # Setup browser
            if not self.setup_browser():
                return False

            # Login
            if not self.login():
                return False

            # Navigate to booking system
            if not self.navigate_to_booking():
                return False

            # Setup booking form
            if not self.setup_booking_form():
                return False

            # Wait for exact target time
            self.wait_for_exact_time(self.target_time)

            # Execute search with Cloudflare handling
            if not self.execute_search_with_cloudflare_handling():
                return False

            # Select first available time
            if not self.select_first_available_time():
                return False

            # Confirm booking
            if not self.confirm_booking():
                return False

            self.log("ULTRAFAST BOOKING COMPLETED SUCCESSFULLY!")
            return True

        except Exception as e:
            self.log(f"CRITICAL ERROR in ultrafast booking: {e}", "ERROR")
            return False

        finally:
            if self.driver:
                self.driver.quit()
                self.log("Browser closed")

def main():
    """Main entry point"""
    if not SELENIUM_AVAILABLE:
        print("ERROR: Selenium not available. Install with: pip install selenium")
        sys.exit(1)

    bot = UltrafastGolfBot()
    success = bot.run_ultrafast_booking()

    if success:
        print("Booking completed successfully!")
        sys.exit(0)
    else:
        print("Booking failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()