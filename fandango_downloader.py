import json
import time
import os
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime

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

    # Set download directory (user's Downloads folder)
    download_dir = os.path.expanduser("~/Downloads")
    
    # Create fandango directory inside downloads if it doesn't exist
    fandango_dir = os.path.join(download_dir, "fandango")
    os.makedirs(fandango_dir, exist_ok=True)
    print(f"DEBUG: Fandango directory set to: {fandango_dir}")
    
    # Create screenshots directory
    screenshots_dir = os.path.join(fandango_dir, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    print(f"DEBUG: Screenshots will be saved to: {screenshots_dir}")
    
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
        
        # Function to take screenshot with timestamp
        def take_screenshot(name):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{screenshots_dir}/{timestamp}_{name}.png"
            driver.save_screenshot(filename)
            print(f"DEBUG: Screenshot saved to {filename}")

        # Navigate to Fandango sign-in URL directly
        print(f"DEBUG: Navigating to URL: {url}")
        driver.get(url)
        print(f"DEBUG: Navigation complete. Current URL: {driver.current_url}")
        
        # Take screenshot of the login page
        take_screenshot("login_page")
        
        # Give the page time to fully load
        time.sleep(5)
        
        try:
            # Look for the form elements directly using more specific selectors
            print("DEBUG: Attempting to locate and fill login form...")
            
            # Wait for page to be fully loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "signin-form"))
            )
            take_screenshot("form_loaded")

            # Find email field - using the full CSS selector path
            print("DEBUG: Finding email field...")
            email_input = driver.find_element(By.CSS_SELECTOR, "#email")
            print("DEBUG: Email field found. Clearing any existing text...")
            email_input.clear()
            print(f"DEBUG: Entering username: {username}")
            email_input.send_keys(username)
            take_screenshot("email_entered")
            
            # Find password field
            print("DEBUG: Finding password field...")
            password_input = driver.find_element(By.CSS_SELECTOR, "#password")
            print("DEBUG: Password field found. Clearing any existing text...")
            password_input.clear()
            print("DEBUG: Entering password...")
            password_input.send_keys(password)
            take_screenshot("password_entered")
            
            # Find and click the submit button
            print("DEBUG: Finding submit button...")
            submit_button = driver.find_element(By.CSS_SELECTOR, "#sign-in-submit-btn")
            print("DEBUG: Submit button found. Clicking...")
            
            # Use JavaScript to click the button (sometimes more reliable)
            driver.execute_script("arguments[0].click();", submit_button)
            print("DEBUG: Submit button clicked via JavaScript")
            take_screenshot("after_submit_click")
            
            # Wait for login to complete and redirect to dashboard
            print("DEBUG: Waiting for login to complete...")
            WebDriverWait(driver, 30).until(
                EC.url_contains("dashboard")
            )
            print("DEBUG: Login successful, redirected to dashboard.")
            take_screenshot("dashboard_loaded")
            
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
                
                # Take screenshot of the current page
                take_screenshot(f"page_{current_page}")
                
                # Extract movies from this page
                print(f"DEBUG: Extracting data from page {current_page}")
                
                # Find favorite buttons (most reliable way to get movie names)
                fav_buttons = driver.find_elements(By.CSS_SELECTOR, ".js-fav-movie-heart")
                page_has_data = False
                
                if fav_buttons:
                    page_has_data = True
                    print(f"Found {len(fav_buttons)} movie favorite buttons on page {current_page}")
                    
                    # Extract and print detailed info about each movie found for debugging
                    for i, btn in enumerate(fav_buttons):
                        movie_name = btn.get_attribute("data-name")
                        movie_id = btn.get_attribute("data-id")
                        movie_type = btn.get_attribute("data-type")
                        if movie_name:
                            print(f"  Movie #{i+1}: '{movie_name}' (ID: {movie_id}, Type: {movie_type})")
                            
                            # Find the parent purchase container to extract related info
                            purchase_container = None
                            current_element = btn
                            
                            # Traverse up the DOM to find container
                            for _ in range(5):  # Limit search depth
                                try:
                                    parent = current_element.find_element(By.XPATH, "./..")
                                    if parent:
                                        classes = parent.get_attribute("class") or ""
                                        if any(c in classes for c in ["purchase-item", "list-item"]):
                                            purchase_container = parent
                                            break
                                        current_element = parent
                                except:
                                    break
                            
                            # Extract date, theater, and other information
                            date_time = "Unknown"
                            theater_name = "Unknown"
                            theater_address = "Unknown"
                            
                            if purchase_container:
                                try:
                                    date_elem = purchase_container.find_element(By.CSS_SELECTOR, ".dark__sub__text, .purchase-date, [class*='date']")
                                    if date_elem:
                                        date_time = date_elem.text.strip()
                                except:
                                    pass
                                    
                                try:
                                    theater_elem = purchase_container.find_element(By.CSS_SELECTOR, ".theater-name, [class*='theater']")
                                    if theater_elem:
                                        theater_name = theater_elem.text.strip()
                                except:
                                    pass
                                    
                                try:
                                    address_elem = purchase_container.find_element(By.CSS_SELECTOR, ".theater-address, [class*='address'], aside, .dark__tertiary__text")
                                    if address_elem:
                                        theater_address = address_elem.text.strip()
                                except:
                                    pass
                            
                            # Add to the purchase data collection
                            all_purchase_data.append({
                                "movie": movie_name,
                                "date": date_time,
                                "theater": theater_name,
                                "address": theater_address,
                                "page": current_page
                            })
                else:
                    # If no favorite buttons, try to find purchase items directly
                    purchase_items = driver.find_elements(By.CSS_SELECTOR, ".purchase-item, .list-item")
                    
                    if purchase_items:
                        page_has_data = True
                        print(f"Found {len(purchase_items)} purchase items on page {current_page}")
                        page_data = _process_purchase_items(driver, purchase_items, current_page)
                        all_purchase_data.extend(page_data)
                
                # Save this page's HTML
                page_html_path = os.path.join(fandango_dir, f"fandango_purchase_history_page_{current_page}.html")
                with open(page_html_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"DEBUG: Saved page {current_page} HTML to {page_html_path}")
                
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
                
                # Also save a combined HTML file for the parser
                main_html_path = os.path.join(fandango_dir, "fandango_purchase_history.html")
                with open(main_html_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"DEBUG: Saved final page HTML to {main_html_path} for parsing")
                
                download_successful = True
            else:
                print("WARNING: No purchase data was collected across all pages")

        except TimeoutException as e:
            print(f"ERROR: Timeout during process: {e}")
            take_screenshot("timeout_error")
            download_successful = False
        except NoSuchElementException as e:
            print(f"ERROR: Could not find a required element: {e}")
            take_screenshot("element_not_found")
            download_successful = False
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")
            take_screenshot("unexpected_error")
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

def _process_purchase_items(driver, purchase_items, page_number):
    """
    Process purchase items on a single page and extract movie data.
    
    Args:
        driver: Selenium WebDriver instance
        purchase_items: List of purchase item WebElements to process
        page_number: Current pagination page number
        
    Returns:
        list: List of dictionaries with movie data
    """
    items_data = []
    
    print(f"Processing {len(purchase_items)} items from page {page_number}")
    
    for idx, item in enumerate(purchase_items):
        try:
            # Initialize with default values
            movie_data = {
                "movie": "Unknown",
                "date": "",
                "theater": "",
                "address": "",
                "page": page_number
            }
            
            # Look for movie name in favorite button data-name attribute first (most reliable)
            try:
                fav_button = item.find_element(By.CSS_SELECTOR, ".js-fav-movie-heart")
                if fav_button:
                    movie_name = fav_button.get_attribute("data-name")
                    if movie_name:
                        movie_data["movie"] = movie_name
                        print(f"  Found movie via fav button: {movie_name}")
            except:
                # If no favorite button, try other methods
                pass
                
            # If movie name still unknown, try standard movie title element
            if movie_data["movie"] == "Unknown":
                try:
                    movie_title_elem = item.find_element(By.CSS_SELECTOR, ".movie-title, .list-item__title")
                    if movie_title_elem:
                        movie_data["movie"] = movie_title_elem.text.strip()
                        print(f"  Found movie via title element: {movie_data['movie']}")
                except:
                    # If still no title found, try any strong or h3 element in the item
                    try:
                        title_elem = item.find_element(By.CSS_SELECTOR, "strong, h3, .dark__text")
                        if title_elem:
                            movie_data["movie"] = title_elem.text.strip()
                            print(f"  Found movie via alternative element: {movie_data['movie']}")
                    except:
                        print(f"  Could not find movie title for item {idx+1} on page {page_number}")
            
            # Extract date
            try:
                date_elem = item.find_element(By.CSS_SELECTOR, ".purchase-date, .dark__sub__text, [class*='date']")
                if date_elem:
                    movie_data["date"] = date_elem.text.strip()
            except:
                print(f"  Could not find date for {movie_data['movie']}")
            
            # Extract theater information
            try:
                theater_elem = item.find_element(By.CSS_SELECTOR, ".theater-name, [class*='theater']")
                if theater_elem:
                    movie_data["theater"] = theater_elem.text.strip()
            except:
                # Try alternative approach - look for text that might contain theater info
                theater_texts = driver.execute_script("""
                    var elements = arguments[0].querySelectorAll('*');
                    var texts = [];
                    for (var i = 0; i < elements.length; i++) {
                        var text = elements[i].textContent.trim();
                        if (
                            (text.includes('AMC') || 
                            text.includes('Regal') || 
                            text.includes('Cinema') || 
                            text.includes('Theater') ||
                            text.includes('Theatre')) && 
                            text.length < 100
                        ) {
                            texts.push(text);
                        }
                    }
                    return texts;
                """, item)
                
                if theater_texts:
                    movie_data["theater"] = theater_texts[0]
            
            # Extract address information
            try:
                # Look for elements that might contain address (often follows theater name)
                address_elem = item.find_element(By.CSS_SELECTOR, ".theater-address, [class*='address'], aside, .dark__tertiary__text")
                if address_elem:
                    movie_data["address"] = address_elem.text.strip()
            except:
                # Theater addresses are hard to reliably extract - we'll use a fallback approach
                # Look for text that might be an address (contains numbers and common address words)
                address_texts = driver.execute_script("""
                    var elements = arguments[0].querySelectorAll('*');
                    var texts = [];
                    for (var i = 0; i < elements.length; i++) {
                        var text = elements[i].textContent.trim();
                        if (
                            /\\d+/.test(text) && 
                            (text.includes('St') || 
                            text.includes('Ave') || 
                            text.includes('Rd') || 
                            text.includes('Blvd') ||
                            text.includes('Street') ||
                            text.includes('Avenue') ||
                            text.includes('Road')) && 
                            text.length < 200
                        ) {
                            texts.push(text);
                        }
                    }
                    return texts;
                """, item)
                
                if address_texts:
                    movie_data["address"] = address_texts[0]
            
            # Add the processed item to our list
            items_data.append(movie_data)
            print(f"  Processed: {movie_data['movie']} at {movie_data['theater']}")
            
        except Exception as e:
            print(f"  Error processing item {idx+1} on page {page_number}: {e}")
    
    return items_data