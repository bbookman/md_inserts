import json
import time
import os
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service # Service might not be needed if chromedriver is in PATH
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def load_config(config_path='config.json'):
    """Load configuration from JSON file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def download_netflix_history(config, password):
    """
    Automate logging into Netflix and downloading viewing history using headless browser.

    Args:
        config (dict): Configuration with Netflix credentials (excluding password) and URL
        password (str): The Netflix password provided by the user.
    """
    print("DEBUG: download_netflix_history function started.") # Added
    # Extract values from config
    url = config.get("NETFLIX_HISTORY_URL")
    username = config.get("EMAIL_ADDRESS")
    print(f"DEBUG: URL: {url}, Username: {username}")
    # Validate required parameters
    if not url:
        print("Error: Netflix history URL not found in config.")
        return False
    if not username:
        print("Error: Netflix EMAIL_ADDRESS required in config.")
        return False
    if not password:
        print("Error: Netflix password is required.")
        return False

    # Set download directory (user's Downloads folder)
    download_dir = os.path.expanduser("~/Downloads")
    print(f"DEBUG: Download directory set to: {download_dir}")
    if not os.path.exists(download_dir):
        print(f"WARNING: Download directory does not exist: {download_dir}")
        # Attempt to create it? Or just warn? For now, just warn.

    # Set up Chrome options for headless mode
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new") # Commented out to disable headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    print("DEBUG: Chrome options configured (headless mode disabled).") # Modified log

    # Configure download behavior for headless mode
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    print("DEBUG: Chrome download preferences configured.") # Added

    # Initialize the driver
    driver = None # Initialize driver to None
    download_successful = False # Initialize success flag
    print("DEBUG: Attempting to initialize WebDriver...")
    try:
        # Consider using webdriver-manager if chromedriver isn't in PATH
        # from webdriver_manager.chrome import ChromeDriverManager
        # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver = webdriver.Chrome(options=chrome_options)
        print("DEBUG: WebDriver initialized successfully.")

        # Navigate to Netflix history URL
        print(f"DEBUG: Navigating to URL: {url}")
        driver.get(url)
        print(f"DEBUG: Navigation complete. Current URL: {driver.current_url}")

        # Check if we're on the login page
        if "login" in driver.current_url:
            print("DEBUG: Login page detected.")
            try:
                # Find username field and enter username
                print("DEBUG: Waiting for username field...")
                username_field = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "userLoginId"))
                )
                print("DEBUG: Username field found. Entering username.")
                username_field.send_keys(username)

                # Find password field and enter password
                print("DEBUG: Finding password field...")
                password_field = driver.find_element(By.NAME, "password")
                print("DEBUG: Password field found. Entering password.")
                password_field.send_keys(password)

                # Click submit button
                print("DEBUG: Finding submit button...")
                submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                print("DEBUG: Submit button found. Clicking submit.")
                submit_button.click()

                # Wait for login to complete (check for an element on the target page)
                print("DEBUG: Waiting for page load after login (expecting 'Download all' link)...")
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "Download all"))
                )
                print("DEBUG: Login successful, history page loaded.")

            except TimeoutException:
                print("ERROR: Timeout during login or waiting for history page after login.")
                # driver.save_screenshot("login_timeout_screenshot.png") # Optional: save screenshot for debugging
                raise # Re-raise the exception to be caught by the outer block
            except NoSuchElementException as e:
                print(f"ERROR: Could not find login element: {e}")
                # driver.save_screenshot("login_element_not_found_screenshot.png") # Optional
                raise
        else:
             print("DEBUG: Login page not detected, assuming already logged in or on history page.")

        # Wait for viewing history page elements if not already waited for post-login
        print("DEBUG: Waiting for 'Download all' link to be present...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Download all"))
        )
        print("DEBUG: 'Download all' link confirmed present.")

        # Click the "Download all" link
        print("DEBUG: Finding 'Download all' link...")
        download_link = driver.find_element(By.LINK_TEXT, "Download all")
        print("DEBUG: Clicking 'Download all' link...")
        download_link.click()
        print("DEBUG: 'Download all' link clicked.")

        # Wait for download to start and complete
        print(f"DEBUG: Starting wait loop for download completion in {download_dir} (max 90s)...")
        max_wait_time = 90  # Increased wait time
        start_time = time.time()
        file_found = False
        downloaded_file_path = None

        while time.time() - start_time < max_wait_time:
            try:
                # Check for file existence
                found_files = [f for f in os.listdir(download_dir) if f.startswith("NetflixViewingHistory") and f.endswith(".csv")]
                if found_files:
                    # Sort by modification time (newest first) to handle multiple downloads
                    found_files.sort(key=lambda f: os.path.getmtime(os.path.join(download_dir, f)), reverse=True)
                    downloaded_file_path = os.path.join(download_dir, found_files[0])
                    print(f"DEBUG: File found in loop: {downloaded_file_path}")
                    file_found = True
                    download_successful = True # Set success flag
                    break # Exit loop once file is found
                else:
                    # Print status periodically
                    if int(time.time() - start_time) % 10 == 0: # Print every 10 seconds
                         print(f"INFO: Still waiting for download... ({int(time.time() - start_time)}s elapsed)")

            except FileNotFoundError:
                 print(f"ERROR: Download directory {download_dir} seems to have disappeared during check.")
                 break # Stop checking if directory is gone
            except Exception as list_err:
                 print(f"ERROR: Could not list download directory contents: {list_err}")
                 # Decide whether to break or continue trying
                 break

            if not file_found:
                time.sleep(2)  # Wait 2 seconds before checking again

        if file_found:
            print("DEBUG: Download loop finished. File was found.")
        else:
            print(f"DEBUG: Download loop finished. File NOT found after {max_wait_time} seconds.")
            download_successful = False # Ensure flag is false if timeout

    except TimeoutException as e:
        print(f"ERROR: Timeout waiting for page elements. Check internet or Netflix page structure. {e}")
        download_successful = False # Ensure flag is false on error
    except NoSuchElementException as e:
        print(f"ERROR: Could not find a required element during automation: {e}")
        download_successful = False # Ensure flag is false on error
    except Exception as e:
        # Catch any other unexpected errors during WebDriver operation
        print(f"ERROR: An unexpected error occurred during Netflix download: {e}")
        import traceback
        traceback.print_exc() # Print detailed traceback
        download_successful = False # Ensure flag is false on error
    finally:
        # Close the browser
        if driver:
            print("DEBUG: Quitting WebDriver.")
            driver.quit()
        else:
            print("DEBUG: WebDriver was not initialized, nothing to quit.")
        print(f"DEBUG: Exiting download_netflix_history function. Success: {download_successful}") # Modified log
        return download_successful # Return the success status
