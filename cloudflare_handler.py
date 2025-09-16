#!/usr/bin/env python3
"""
Cloudflare Challenge Handler
Critical module for handling Cloudflare challenges during golf booking
Must click at coordinates (464, 572) within milliseconds of challenge appearance
"""

import time
from datetime import datetime
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class CloudflareHandler:
    def __init__(self, driver=None):
        self.driver = driver
        self.cloudflare_coords = (464, 572)
        self.max_wait_time = 5  # seconds
        self.click_timeout = 0.2  # 200ms maximum delay

    def log(self, message):
        """Log with timestamp for debugging"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] CLOUDFLARE: {message}")

    def detect_cloudflare_challenge(self):
        """
        Detect if Cloudflare challenge is present
        Returns True if challenge detected, False otherwise
        """
        try:
            # Look for common Cloudflare challenge indicators
            indicators = [
                "//input[@type='checkbox']",  # Cloudflare checkbox
                "//*[contains(text(), 'Verify you are human')]",
                "//*[contains(text(), 'Please wait')]",
                "//*[contains(@class, 'cf-browser-verification')]",
                "//*[contains(@class, 'cloudflare')]"
            ]

            for indicator in indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        self.log(f"Cloudflare challenge detected: {indicator}")
                        return True
                except:
                    continue

            return False
        except Exception as e:
            self.log(f"Error detecting Cloudflare challenge: {e}")
            return False

    def handle_challenge_instant(self):
        """
        Handle Cloudflare challenge with instant clicking
        CRITICAL: Must execute within 200ms for booking success
        """
        start_time = time.time()
        self.log("Starting instant Cloudflare challenge handling")

        try:
            # Move to Cloudflare checkbox coordinates immediately
            actions = ActionChains(self.driver)

            # Method 1: Direct coordinate click
            self.log(f"Clicking at coordinates {self.cloudflare_coords}")
            actions.move_by_offset(self.cloudflare_coords[0], self.cloudflare_coords[1])
            actions.click()
            actions.perform()

            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            self.log(f"Coordinate click executed in {elapsed:.1f}ms")

            # Brief wait to see if challenge resolves
            time.sleep(0.5)

            # Method 2: Try to find checkbox element if coordinate click failed
            if self.detect_cloudflare_challenge():
                self.log("Challenge still present, trying element-based approach")
                try:
                    # Look for checkbox input
                    checkbox = WebDriverWait(self.driver, 1).until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox']"))
                    )
                    checkbox.click()
                    elapsed = (time.time() - start_time) * 1000
                    self.log(f"Checkbox click executed in {elapsed:.1f}ms")
                except Exception as e:
                    self.log(f"Checkbox click failed: {e}")

            # Final verification
            time.sleep(1)
            if not self.detect_cloudflare_challenge():
                total_time = (time.time() - start_time) * 1000
                self.log(f"SUCCESS: Cloudflare challenge resolved in {total_time:.1f}ms")
                return True
            else:
                self.log("WARNING: Challenge may still be present")
                return False

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            self.log(f"ERROR handling Cloudflare challenge in {elapsed:.1f}ms: {e}")
            return False

    def handle_challenge_with_retry(self, max_attempts=3):
        """
        Handle Cloudflare challenge with retry logic
        """
        for attempt in range(max_attempts):
            self.log(f"Cloudflare challenge attempt {attempt + 1}/{max_attempts}")

            if self.handle_challenge_instant():
                return True

            if attempt < max_attempts - 1:
                self.log(f"Attempt {attempt + 1} failed, retrying in 0.5s")
                time.sleep(0.5)

        self.log("All Cloudflare challenge attempts failed")
        return False

    def wait_and_handle_challenge(self, timeout=5):
        """
        Wait for Cloudflare challenge to appear and handle it immediately
        """
        start_time = time.time()
        self.log(f"Waiting for Cloudflare challenge (timeout: {timeout}s)")

        while time.time() - start_time < timeout:
            if self.detect_cloudflare_challenge():
                self.log("Cloudflare challenge detected, handling immediately")
                return self.handle_challenge_instant()
            time.sleep(0.1)  # Check every 100ms

        self.log("No Cloudflare challenge detected within timeout")
        return True  # No challenge is also success

def handle_cloudflare_with_selenium(driver):
    """
    Standalone function to handle Cloudflare with Selenium driver
    """
    handler = CloudflareHandler(driver)
    return handler.handle_challenge_with_retry()

def handle_cloudflare_coordinates_only(driver, coords=(464, 572)):
    """
    Minimal Cloudflare handler - just click coordinates
    For use when speed is absolutely critical
    """
    try:
        actions = ActionChains(driver)
        actions.move_by_offset(coords[0], coords[1])
        actions.click()
        actions.perform()
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"Cloudflare coordinate click failed: {e}")
        return False

if __name__ == "__main__":
    print("Cloudflare Handler Module")
    print("This module provides instant Cloudflare challenge handling")
    print("Key functions:")
    print("- CloudflareHandler class for full functionality")
    print("- handle_cloudflare_with_selenium() for simple integration")
    print("- handle_cloudflare_coordinates_only() for speed-critical situations")

    if not SELENIUM_AVAILABLE:
        print("WARNING: Selenium not available. Install with: pip install selenium")