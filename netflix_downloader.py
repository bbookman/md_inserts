import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def load_config(config_path='config.json'):
    """Load configuration from JSON file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def download_netflix_history(config):
    """
    Automate logging into Netflix and downloading viewing history.
    
    Args:
        config (dict): Configuration with Netflix credentials and URL
    """
    # Extract values from config
    url = config.get("NETFLIX_HISTORY_URL")
    username = config.get("EMAIL_ADDRESS")
    password = config.get("NETFLIX_PASSWORD")
    
    # Validate required parameters
    if not url:
        print("Error: Netflix history URL not found in config.")
        return
    
    if not username or not password:
        print("Error: Netflix username and password required in config.")
        return
    
    # Set up Chrome options - let browser use default download location
    chrome_options = Options()
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to Netflix history URL
        print(f"Navigating to Netflix viewing history page: {url}")
        driver.get(url)
        
        # Check if we're on the login page
        if "login" in driver.current_url:
            print("Login page detected, attempting to log in...")
            
            # Find username field and enter username
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "userLoginId"))
            )
            username_field.send_keys(username)
            
            # Find password field and enter password
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            
            # Click submit button
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            
            # Wait for login to complete
            print("Waiting for login to complete...")
            time.sleep(5)
        
        # Wait for viewing history page to load
        print("Waiting for viewing history page to load...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Download all"))
        )
        
        # Click the "Download all" link
        print("Clicking 'Download all' link...")
        download_link = driver.find_element(By.LINK_TEXT, "Download all")
        download_link.click()
        
        # Wait for download to start
        print("Waiting for download to complete...")
        time.sleep(5)
        
        print("Download initiated successfully!")
        print("File should be saved to your browser's default download location")
        
    except TimeoutException:
        print("Timeout waiting for page elements. Check your internet connection or Netflix page structure.")
    except NoSuchElementException as e:
        print(f"Could not find element: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the browser
        driver.quit()
