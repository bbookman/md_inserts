import json
import time
import os
import getpass
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
from bs4 import BeautifulSoup

def load_config(config_path='config.json'):
    """Load configuration from JSON file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def download_fandango_history(config, password):
    """
    Automate logging into Fandango and downloading purchase history using visible browser.
    
    Args:
        config (dict): Configuration with Fandango credentials (excluding password) and URL
        password (str): The Fandango password provided by the user.
        
    Returns:
        bool: True if download was successful, False otherwise.
    """
    print("DEBUG: download_fandango_history function started.")
    
    # Extract values from config
    url = "https://www.fandango.com/accounts/sign-in"  # Direct login URL
    username = config.get("FANDANGO_USER_NAME")
    print(f"DEBUG: URL: {url}, Username: {username}")
    
    # Validate required parameters
    if not username:
        print("Error: FANDANGO_USER_NAME required in config.")
        return False
    if not password:
        print("Error: Fandango password is required.")
        return False

    # Set download directory (user's Downloads folder for CSV output)
    download_dir = os.path.expanduser("~/Downloads")
    
    # Create fandango directory inside the project folder instead of Downloads
    # Get the current working directory (project root)
    project_dir = os.path.dirname(os.path.abspath(__file__))
    fandango_dir = os.path.join(project_dir, "fandango")
    os.makedirs(fandango_dir, exist_ok=True)
    print(f"DEBUG: Fandango directory set to: {fandango_dir}")
    
    print(f"DEBUG: Download directory set to: {download_dir}")
    if not os.path.exists(download_dir):
        print(f"WARNING: Download directory does not exist: {download_dir}")
        # Attempt to create it
        try:
            os.makedirs(download_dir, exist_ok=True)
            print(f"Created download directory: {download_dir}")
        except Exception as e:
            print(f"ERROR: Could not create download directory: {e}")
            return False

    # Set up Chrome options for headed mode (visible browser)
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # Commented out for headed mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    print("DEBUG: Chrome options configured for headed mode (browser will be visible).")

    # Configure download behavior
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    print("DEBUG: Chrome download preferences configured.")

    # Initialize the driver
    driver = None
    download_successful = False
    print("DEBUG: Attempting to initialize WebDriver...")
    try:
        # Initialize Chrome WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        print("DEBUG: WebDriver initialized successfully.")

        # Navigate to Fandango sign-in URL directly
        print(f"DEBUG: Navigating to URL: {url}")
        driver.get(url)
        print(f"DEBUG: Navigation complete. Current URL: {driver.current_url}")
        
        # Give the page time to fully load
        time.sleep(5)
        
        try:
            # Look for the form elements directly using more specific selectors
            print("DEBUG: Attempting to locate and fill login form...")
            
            # Wait for page to be fully loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "signin-form"))
            )

            # Find email field - using the full CSS selector path
            print("DEBUG: Finding email field...")
            email_input = driver.find_element(By.CSS_SELECTOR, "#email")
            print("DEBUG: Email field found. Clearing any existing text...")
            email_input.clear()
            print(f"DEBUG: Entering username: {username}")
            email_input.send_keys(username)
            
            # Find password field
            print("DEBUG: Finding password field...")
            password_input = driver.find_element(By.CSS_SELECTOR, "#password")
            print("DEBUG: Password field found. Clearing any existing text...")
            password_input.clear()
            print("DEBUG: Entering password...")
            password_input.send_keys(password)
            
            # Find and click the submit button
            print("DEBUG: Finding submit button...")
            submit_button = driver.find_element(By.CSS_SELECTOR, "#sign-in-submit-btn")
            print("DEBUG: Submit button found. Clicking...")
            
            # Use JavaScript to click the button (sometimes more reliable)
            driver.execute_script("arguments[0].click();", submit_button)
            print("DEBUG: Submit button clicked via JavaScript")
            
            # Wait for login to complete and redirect to dashboard
            print("DEBUG: Waiting for login to complete...")
            WebDriverWait(driver, 30).until(
                EC.url_contains("dashboard")
            )
            print("DEBUG: Login successful, redirected to dashboard.")
            
            # Skip directly to URL-based pagination for purchase history
            print("\nDEBUG: Using URL-based pagination to extract purchase history...")
            
            # Initialize array to store all purchase data
            all_purchase_data = []
            current_page = 1
            max_pages = 20  # Safety limit
            
            # Continue fetching pages until no more data is found or reached max pages
            while current_page <= max_pages:
                # Construct the URL with page number
                page_url = f"https://www.fandango.com/accounts/my-purchases?pn={current_page}"
                print(f"\nDEBUG: Navigating to page {current_page} using URL: {page_url}")
                
                # Navigate to the page
                driver.get(page_url)
                
                # Wait for the page to load
                time.sleep(5)  # Initial wait
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".purchase-history, .js-fav-movie-heart, [data-name]"))
                    )
                except:
                    print(f"DEBUG: Timeout waiting for page {current_page} to load, but continuing anyway")
                
                # NEW APPROACH: Get complete page HTML and parse with BeautifulSoup
                print(f"DEBUG: Getting page source for page {current_page}")
                page_source = driver.page_source
                
                # Save HTML to file for debugging (optional)
                debug_html_path = os.path.join(fandango_dir, f"fandango_page_{current_page}.html")
                with open(debug_html_path, "w", encoding="utf-8") as f:
                    f.write(page_source)
                print(f"DEBUG: Saved HTML source to {debug_html_path}")
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Find all purchase items
                purchase_items = soup.select('.purchase-item, .list-item')
                page_has_data = False
                
                if purchase_items:
                    page_has_data = True
                    print(f"Found {len(purchase_items)} purchase items on page {current_page}")
                    
                    # Process each purchase item
                    for i, item in enumerate(purchase_items):
                        # Extract movie name
                        movie_name = "Unknown"
                        movie_fav = item.select_one('.js-fav-movie-heart')
                        if movie_fav and movie_fav.get('data-name'):
                            movie_name = movie_fav.get('data-name')
                        else:
                            movie_title = item.select_one('.movie-title, .list-item__title')
                            if movie_title:
                                movie_name = movie_title.text.strip()
                        
                        print(f"  Movie #{i+1}: '{movie_name}'")
                        
                        # Extract date - USING DIRECT HTML SEARCH
                        date_time = "Unknown"
                        
                        # First look for the "Purchase Completed" section
                        purchase_completed_section = None
                        for section in item.select('.list-item__description--additional-movie-info-section'):
                            strong_tags = section.select('strong')
                            for strong in strong_tags:
                                if "Purchase Completed" in strong.text:
                                    purchase_completed_section = section
                                    break
                            if purchase_completed_section:
                                break
                        
                        # Extract date from Purchase Completed section if found
                        if purchase_completed_section:
                            date_elem = purchase_completed_section.select_one('div.dark__sub__text')
                            if date_elem:
                                date_time = date_elem.text.strip()
                                print(f"  Found date in Purchase Completed section: {date_time}")
                        
                        # If date still unknown, try other methods
                        if date_time == "Unknown":
                            # Try all dark__sub__text elements
                            date_elements = item.select('div.dark__sub__text')
                            for date_elem in date_elements:
                                date_text = date_elem.text.strip()
                                # Check if it looks like a date (contains day of week, month, year, etc.)
                                if re.search(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', date_text) and \
                                   re.search(r'at', date_text) and \
                                   re.search(r'(AM|PM)', date_text):
                                    date_time = date_text
                                    print(f"  Found date via dark__sub__text: {date_time}")
                                    break
                        
                        # If date still unknown, use regex pattern matching on the entire item HTML
                        if date_time == "Unknown":
                            item_html = str(item)
                            date_patterns = [
                                r'((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2} \d{4} at \d{1,2}:\d{2} (?:AM|PM))',
                                r'(\d{1,2}/\d{1,2}/\d{4})',
                                r'(\d{4}-\d{2}-\d{2})'
                            ]
                            
                            for pattern in date_patterns:
                                matches = re.findall(pattern, item_html)
                                if matches:
                                    date_time = matches[0]
                                    print(f"  Found date via pattern match: {date_time}")
                                    break
                        
                        # Extract theater info
                        theater_name = "Unknown"
                        theater_link = item.select_one('a.dark__link[href*="theater-page"]')
                        if theater_link:
                            theater_name = theater_link.text.strip()
                            print(f"  Found theater: {theater_name}")
                        
                        # Enhanced address extraction with multiple approaches
                        theater_address = "Unknown"
                        
                        # APPROACH 1: Look for aside directly after theater link within same parent
                        if theater_link:
                            theater_section = theater_link.parent
                            if theater_section:
                                # Check for aside as direct sibling
                                aside_elem = theater_section.select_one('aside')
                                if aside_elem and aside_elem.text:
                                    theater_address = aside_elem.text.strip()
                                    print(f"  Found address (approach 1): {theater_address}")
                        
                        # APPROACH 2: Try to find any aside within the entire purchase item that's near a theater link
                        if theater_address == "Unknown":
                            theater_sections = item.select('.list-item__description--additional-movie-info-section')
                            for section in theater_sections:
                                if section.select_one('a.dark__link[href*="theater-page"]'):
                                    aside_elem = section.select_one('aside')
                                    if aside_elem and aside_elem.text:
                                        theater_address = aside_elem.text.strip()
                                        print(f"  Found address (approach 2): {theater_address}")
                                        break
                                        
                        # APPROACH 3: Look for any aside element in the container 
                        if theater_address == "Unknown":
                            aside_elems = item.select('aside')
                            for aside in aside_elems:
                                if aside.text and re.search(r'\d+.*\d{5}', aside.text):  # Look for text with street number and zip code
                                    theater_address = aside.text.strip()
                                    print(f"  Found address (approach 3): {theater_address}")
                                    break
                                    
                        # APPROACH 4: Look for any element with address-like content using text analysis
                        if theater_address == "Unknown" and theater_name != "Unknown":
                            # Find elements that might contain addresses by checking for address patterns
                            for elem in item.select('div, span, p'):
                                text = elem.text.strip()
                                # Look for common address patterns
                                if (re.search(r'\d+\s+\w+\s+(?:St|Ave|Rd|Blvd|Lane|Dr|Circle|Hwy|Highway|Pkwy|Parkway)', text, re.IGNORECASE) or
                                    re.search(r'\w+,\s*[A-Z]{2}\s*\d{5}', text)):  # City, State ZIP
                                    theater_address = text
                                    print(f"  Found address (approach 4): {theater_address}")
                                    break

                        # Add to the purchase data collection
                        all_purchase_data.append({
                            "movie": movie_name,
                            "date": date_time,
                            "theater": theater_name,
                            "address": theater_address,
                            "page": current_page
                        })
                
                # If no data was found on this page, we've reached the end
                if not page_has_data:
                    print(f"DEBUG: No data found on page {current_page} - reached the end of purchase history")
                    break
                    
                # Move to the next page
                current_page += 1
            
            # Save all combined data to CSV
            if all_purchase_data:
                csv_path = os.path.join(download_dir, "FandangoPurchaseHistory.csv")
                with open(csv_path, "w", encoding="utf-8") as f:
                    f.write("Movie,Date,Theater,Address,Page\n")
                    for item in all_purchase_data:
                        f.write(f"\"{item['movie']}\",\"{item['date']}\",\"{item['theater']}\",\"{item['address']}\",{item['page']}\n")
                
                print(f"DEBUG: Saved {len(all_purchase_data)} total purchase records to {csv_path}")
                
                # Make sure the saved files actually exist before returning success
                if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
                    download_successful = True
                    print("DEBUG: Verified that files were successfully saved")
                else:
                    download_successful = False
                    print("DEBUG: Failed to save files or files are empty")
            else:
                print("WARNING: No purchase data was collected across all pages")
                download_successful = False

        except TimeoutException as e:
            print(f"ERROR: Timeout during process: {e}")
            download_successful = False
        except NoSuchElementException as e:
            print(f"ERROR: Could not find a required element: {e}")
            download_successful = False
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")
            download_successful = False

    except Exception as e:
        # Catch any other unexpected errors during WebDriver operation
        print(f"ERROR: An unexpected error occurred during Fandango download: {e}")
        import traceback
        traceback.print_exc()
        download_successful = False
    finally:
        # Close the browser
        if driver:
            print("DEBUG: Quitting WebDriver.")
            driver.quit()
        else:
            print("DEBUG: WebDriver was not initialized, nothing to quit.")
        print(f"DEBUG: Exiting download_fandango_history function. Success: {download_successful}")
        return download_successful

def delete_fandango_directory():
    """
    Delete the fandango directory that contains the HTML files.
    
    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    # Get the current working directory (project root)
    project_dir = os.path.dirname(os.path.abspath(__file__))
    fandango_dir = os.path.join(project_dir, "fandango")
    
    if not os.path.exists(fandango_dir):
        print(f"WARNING: Fandango directory not found for deletion: {fandango_dir}")
        return False
    
    try:
        # Use shutil.rmtree to remove directory and all its contents
        import shutil
        shutil.rmtree(fandango_dir)
        print(f"Successfully deleted Fandango directory: {fandango_dir}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to delete Fandango directory: {e}")
        return False