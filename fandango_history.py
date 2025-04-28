import os
import glob
import re
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
from bs4 import BeautifulSoup

class FandangoHistoryProcessor:
    """
    Class to process and append Fandango purchase history to markdown files.
    """

    def __init__(self, config: Dict):
        """
        Initialize the processor with configuration.

        Args:
            config (Dict): Configuration dictionary.
        """
        self.target_dir = config.get("TARGET_DIR", "")
        self.fandango_html_file = self._find_fandango_html_file()
    
    def _find_fandango_html_file(self) -> str:
        """
        Find Fandango HTML files in the Downloads directory.
        
        Returns:
            str: Path to the Fandango HTML file.
        """
        download_dir = os.path.expanduser("~/Downloads/fandango")
        
        if not os.path.exists(download_dir):
            print(f"Fandango HTML directory not found: {download_dir}")
            return ""
        
        # First look for the standard filename
        standard_file = os.path.join(download_dir, "fandango_purchase_history.html")
        if os.path.exists(standard_file):
            print(f"Found Fandango HTML file: {standard_file}")
            return standard_file
        
        # If standard file not found, look for any HTML files
        html_files = glob.glob(os.path.join(download_dir, "*.html"))
        
        if html_files:
            # Sort by modification time (newest first)
            html_files.sort(key=os.path.getmtime, reverse=True)
            print(f"Found Fandango HTML file: {html_files[0]}")
            return html_files[0]
        else:
            print(f"No Fandango HTML files found in: {download_dir}")
            return ""
    
    def parse_fandango_html(self) -> List[Dict]:
        """
        Parse the Fandango HTML file to extract movie information.
        
        Returns:
            List[Dict]: List of dictionaries containing movie information.
        """
        if not self.fandango_html_file or not os.path.exists(self.fandango_html_file):
            print(f"Fandango HTML file not found: {self.fandango_html_file}")
            return []
        
        try:
            with open(self.fandango_html_file, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all movie entries
            movie_entries = []
            
            # Look for elements with js-fav-movie-heart class - these contain movie names in data-name attribute
            favorite_buttons = soup.find_all(class_='js-fav-movie-heart')
            
            movie_ids_processed = set()  # To avoid duplicates
            
            for button in favorite_buttons:
                # Extract the movie name from data-name attribute
                movie_name = button.get('data-name', '')
                movie_id = button.get('data-id', '')
                
                if not movie_name or not movie_id or movie_id in movie_ids_processed:
                    continue
                
                movie_ids_processed.add(movie_id)
                
                # Find the nearest containing purchase item/container
                purchase_container = self._find_parent_purchase_container(button)
                
                date_time = ''
                theater_name = ''
                theater_address = ''
                
                if purchase_container:
                    # Extract date and time
                    date_time_element = purchase_container.find(class_='dark__sub__text') or purchase_container.find(class_='purchase-date')
                    date_time = date_time_element.text.strip() if date_time_element else ''
                    
                    # Extract theater info
                    theater_info = self._extract_theater_info(purchase_container)
                    theater_name = theater_info.get('theater_name', '')
                    theater_address = theater_info.get('theater_address', '')
                
                # Parse the date string into a structured format if possible
                date_obj = self._parse_date(date_time)
                formatted_date = date_obj.strftime('%Y-%m-%d') if date_obj else ''
                
                # Create a movie entry dictionary
                movie_entry = {
                    'movie_name': movie_name,
                    'date_time': date_time,
                    'theater_name': theater_name,
                    'theater_address': theater_address,
                    'formatted_date': formatted_date,
                    'movie_id': movie_id
                }
                
                movie_entries.append(movie_entry)
            
            # If we didn't find any movies with the favorite buttons, try alternative methods
            if not movie_entries:
                print("No movie entries found with favorite buttons, trying alternative methods...")
                
                # Look for movie titles in list items
                movie_items = soup.find_all(class_='purchase-item') or soup.find_all(class_='list-item')
                
                for item in movie_items:
                    movie_name_element = item.find(class_='movie-title') or item.find(class_='list-item__title')
                    
                    if not movie_name_element:
                        continue
                    
                    movie_name = movie_name_element.text.strip()
                    
                    # Extract date and time
                    date_time_element = item.find(class_='dark__sub__text') or item.find(class_='purchase-date') 
                    date_time = date_time_element.text.strip() if date_time_element else ''
                    
                    # Extract theater info
                    theater_info = self._extract_theater_info(item)
                    theater_name = theater_info.get('theater_name', '')
                    theater_address = theater_info.get('theater_address', '')
                    
                    # Parse the date
                    date_obj = self._parse_date(date_time)
                    formatted_date = date_obj.strftime('%Y-%m-%d') if date_obj else ''
                    
                    # Create a movie entry dictionary
                    movie_entry = {
                        'movie_name': movie_name,
                        'date_time': date_time,
                        'theater_name': theater_name,
                        'theater_address': theater_address,
                        'formatted_date': formatted_date
                    }
                    
                    movie_entries.append(movie_entry)
            
            print(f"Found {len(movie_entries)} movie entries in Fandango HTML")
            return movie_entries
        
        except Exception as e:
            print(f"Error parsing Fandango HTML: {e}")
            return []
    
    def _find_parent_purchase_container(self, element) -> Optional[BeautifulSoup]:
        """
        Find the parent purchase container for a movie element.
        
        Args:
            element: BeautifulSoup element to start searching from.
            
        Returns:
            Optional[BeautifulSoup]: Parent container element or None if not found.
        """
        # Try to find the closest parent that's a purchase item
        current = element
        max_levels = 5  # Don't go up too many levels
        
        for _ in range(max_levels):
            if current.parent is None:
                return None
                
            current = current.parent
            
            # Check if this is a purchase container
            classes = current.get('class', [])
            if classes and any(c in ['purchase-item', 'list-item', 'purchase-history-item'] for c in classes):
                return current
        
        return None
    
    def _extract_theater_info(self, element) -> Dict:
        """
        Extract theater name and address from the HTML element.
        
        Args:
            element: BeautifulSoup element potentially containing theater information.
            
        Returns:
            Dict: Dictionary with theater_name and theater_address keys.
        """
        info = {
            'theater_name': '',
            'theater_address': ''
        }
        
        # Look for theater information in various potential locations in the HTML
        
        # Option 1: Check for elements with "additional-movie-info-section" class
        additional_info = element.find(class_='list-item__description--additional-movie-info-section')
        if additional_info:
            # Theater name is often in a link element
            theater_link = additional_info.find('a')
            if theater_link:
                info['theater_name'] = theater_link.text.strip()
            
            # Address might be in an aside or paragraph element
            address_element = additional_info.find('aside') or additional_info.find('p')
            if address_element:
                info['theater_address'] = address_element.text.strip()
        
        # Option 2: Check for theater information in sibling elements
        if not info['theater_name']:
            theater_element = element.find_next(text=re.compile(r'Theater|Cinema|AMC|Regal', re.IGNORECASE))
            if theater_element and theater_element.parent:
                info['theater_name'] = theater_element.strip()
                
                # Address might be in nearby elements
                address_element = theater_element.parent.find_next('p') or theater_element.parent.find_next('div')
                if address_element:
                    info['theater_address'] = address_element.text.strip()
        
        return info
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string from Fandango format to datetime object.
        
        Args:
            date_str (str): Date string from Fandango HTML.
            
        Returns:
            Optional[datetime]: Datetime object or None if parsing fails.
        """
        if not date_str:
            return None
        
        # Common date formats in Fandango
        date_formats = [
            '%m/%d/%y', '%m/%d/%Y', 
            '%B %d, %Y', '%b %d, %Y',
            '%A, %B %d, %Y', '%a, %b %d, %Y',
            '%Y-%m-%d'
        ]
        
        # Try to extract date with various formats and patterns
        for date_format in date_formats:
            try:
                # Try a direct conversion first
                return datetime.strptime(date_str, date_format)
            except ValueError:
                pass
        
        # If direct conversion fails, try to extract date using regex patterns
        date_patterns = [
            r'(\w+ \d{1,2}, \d{4})',  # Month DD, YYYY
            r'(\d{1,2}/\d{1,2}/\d{2,4})',  # MM/DD/YY or MM/DD/YYYY
            r'(\d{4}-\d{2}-\d{2})'  # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                extracted_date = match.group(1)
                # Try the formats again with the extracted date
                for date_format in date_formats:
                    try:
                        return datetime.strptime(extracted_date, date_format)
                    except ValueError:
                        continue
        
        return None
    
    def get_purchases_by_date(self) -> defaultdict:
        """
        Parse the HTML file and organize Fandango purchases by date.

        Returns:
            defaultdict: Dictionary where keys are dates (YYYY-MM-DD) and values are lists of movie entries.
        """
        purchases_by_date = defaultdict(list)
        
        # Parse the HTML file to get movie entries
        movie_entries = self.parse_fandango_html()
        
        for entry in movie_entries:
            # Skip entries without a valid formatted date
            if not entry.get('formatted_date'):
                continue
            
            date_key = entry['formatted_date']
            
            # Create a markdown entry with movie name, theater, and date
            theater_info = ''
            if entry.get('theater_name'):
                theater_info = f" at {entry['theater_name']}"
                if entry.get('theater_address'):
                    theater_info += f" ({entry['theater_address']})"
            
            # Format as a markdown list item
            purchase_entry = f"* {entry['movie_name']}{theater_info}"
            
            # Add the entry to the purchases by date
            if purchase_entry not in purchases_by_date[date_key]:
                purchases_by_date[date_key].append(purchase_entry)
        
        # Debug: Show found dates
        print(f"Found Fandango purchase history for {len(purchases_by_date)} dates from HTML")
        date_sample = list(purchases_by_date.keys())[:5] if purchases_by_date else []
        print(f"Sample dates: {date_sample}")
        
        return purchases_by_date
    
    def file_already_has_fandango_history(self, file_path: str) -> bool:
        """
        Check if a file already contains Fandango history section.
        
        Args:
            file_path (str): Path to the markdown file.
            
        Returns:
            bool: True if the file already has Fandango history, False otherwise.
        """
        try:
            if not os.path.exists(file_path):
                return False
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check if the file already contains Fandango history section
            return "## Fandango Purchase History" in content
        except Exception as e:
            print(f"Error checking file for Fandango history: {e}")
            return False

    def delete_fandango_history_file(self) -> bool:
        """
        Delete the Fandango history file after processing.
        
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not self.fandango_html_file or not os.path.exists(self.fandango_html_file):
            print(f"Fandango HTML file not found for deletion: {self.fandango_html_file}")
            return False
            
        try:
            os.remove(self.fandango_html_file)
            print(f"Successfully deleted Fandango HTML file: {self.fandango_html_file}")
            return True
        except Exception as e:
            print(f"Error deleting Fandango HTML file {self.fandango_html_file}: {e}")
            return False

    def append_purchases_to_files(self, delete_after_processing: bool = False) -> bool:
        """
        Process Fandango purchase history data from HTML. For each date with purchases,
        ensure a corresponding markdown file exists in the correct Year/MM-Month Name subdirectory
        and append the history if it's not already present. Creates the file and directories if needed.
        
        Args:
            delete_after_processing (bool): Whether to delete the history files after processing.
            
        Returns:
            bool: True if processing was successful, False otherwise.
        """
        if not os.path.exists(self.target_dir):
            print(f"Target directory not found: {self.target_dir}")
            return False
            
        # Check if target directory is writable
        if not os.access(self.target_dir, os.W_OK):
            print(f"Error: Target directory is not writable: {self.target_dir}")
            return False

        # Get purchases from HTML
        purchases_by_date = self.get_purchases_by_date()
        
        if not purchases_by_date:
            print("No Fandango purchase history data found to process.")
            return False

        processed_files = 0
        created_files = 0
        # Iterate through each date found in the Fandango history
        for file_date, purchases in purchases_by_date.items():
            try:
                # Extract year and month name from the date string (YYYY-MM-DD)
                date_obj = datetime.strptime(file_date, '%Y-%m-%d')
                year = date_obj.strftime('%Y')
                month_number = date_obj.strftime('%m') # Get month number (e.g., 02)
                month_name = date_obj.strftime('%B') # Get full month name (e.g., February)

                # Construct the target directory path including Year/MM-Month Name
                target_subdir = os.path.join(self.target_dir, year, f"{month_number}-{month_name}")
                file_name = f"{file_date}.md"
                file_path = os.path.join(target_subdir, file_name)

                print(f"Processing Fandango date: {file_date} -> {file_path}")

                # Ensure the target subdirectory exists
                try:
                    os.makedirs(target_subdir, exist_ok=True)
                except OSError as e:
                    print(f"Error creating directory {target_subdir}: {e}")
                    continue
                    
                # Check if subdirectory is writable
                if not os.access(target_subdir, os.W_OK):
                    print(f"Error: Directory is not writable: {target_subdir}")
                    continue

                # Check if the target file exists
                if os.path.exists(file_path):
                    print(f"  File exists: {file_path}")
                    
                    # Check if file is writable
                    if not os.access(file_path, os.W_OK):
                        print(f"  Error: File is not writable: {file_path}")
                        continue
                        
                    # Check if file already has Fandango history section
                    if self.file_already_has_fandango_history(file_path):
                        print(f"  File {file_name} already has Fandango history section. Skipping.")
                        continue
                    else:
                        # Append Fandango history to existing file
                        try:
                            with open(file_path, mode="a", encoding="utf-8") as file:
                                file.write("\n## Fandango Purchase History\n\n")
                                file.write("\n".join(purchases))
                                file.write("\n")
                            print(f"  Appended Fandango history to existing file: {file_name}")
                            processed_files += 1
                        except Exception as e:
                            print(f"  Error appending to existing file {file_name}: {e}")

                else:
                    # File does not exist, create it and add history
                    print(f"  File does not exist, creating: {file_path}")
                    try:
                        with open(file_path, mode="w", encoding="utf-8") as file:
                            # Add the Fandango history section
                            file.write("## Fandango Purchase History\n\n")
                            file.write("\n".join(purchases))
                            file.write("\n")
                        print(f"  Created file and added Fandango history: {file_name}")
                        created_files += 1
                    except Exception as e:
                        print(f"  Error creating file {file_name}: {e}")
            except ValueError:
                 print(f"Skipping invalid date format: {file_date}")
                 continue
            except Exception as e:
                 print(f"An unexpected error occurred processing date {file_date}: {e}")
                 continue

        print(f"Finished processing Fandango history. Appended to {processed_files} existing file(s), created {created_files} new file(s).")
        
        # Delete the history files if requested and there was at least one file processed
        if delete_after_processing and (processed_files > 0 or created_files > 0):
            # Delete HTML file if it exists
            return self.delete_fandango_history_file()
            
        return True