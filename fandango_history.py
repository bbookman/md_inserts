import os
import csv
import re
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
from markdown_generator import Markdown  # Import the Markdown class

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
        self.fandango_csv_file = self._find_fandango_csv_file()
        self.markdown_generator = Markdown()  # Initialize the Markdown generator
        self.last_error = None  # Track the last error message
    
    def _find_fandango_csv_file(self) -> str:
        """
        Find Fandango CSV files in the Downloads directory.
        
        Returns:
            str: Path to the Fandango CSV file.
        """
        download_dir = os.path.expanduser("~/Downloads")
        
        if not os.path.exists(download_dir):
            print(f"Downloads directory not found: {download_dir}")
            return ""
        
        # Look for the standard filename
        standard_file = os.path.join(download_dir, "FandangoPurchaseHistory.csv")
        if os.path.exists(standard_file):
            print(f"Found Fandango CSV file: {standard_file}")
            return standard_file
        
        return ""
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse various date formats from Fandango history.
        
        Args:
            date_str (str): Date string to parse.
            
        Returns:
            Optional[datetime]: Parsed datetime object or None if parsing fails.
        """
        if not date_str:
            return None
            
        # List of possible date formats to try, in order of preference
        date_formats = [
            '%Y-%m-%d',              # YYYY-MM-DD
            '%m/%d/%Y',              # MM/DD/YYYY
            '%m/%d/%y',              # MM/DD/YY
            '%A, %b %d %Y at %I:%M %p',  # Monday, Mar 9 2020 at 2:15 PM
            '%a, %b %d %Y at %I:%M %p',  # Mon, Mar 9 2020 at 2:15 PM
            '%B %d, %Y',             # March 9, 2020
            '%b %d, %Y'              # Mar 9, 2020
        ]
        
        # Try each format until one works
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                continue
        
        # If the above formats don't work, try to extract the date from the string
        # using regular expressions to handle non-standard formats
        date_patterns = [
            r'(\w+, \w+ \d{1,2} \d{4})',       # Monday, Mar 9 2020
            r'(\w+ \d{1,2}, \d{4})',           # March 9, 2020
            r'(\d{1,2}/\d{1,2}/\d{2,4})'       # MM/DD/YY or MM/DD/YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                extracted_date = match.group(1)
                
                # Try each date format with the extracted date string
                for date_format in date_formats:
                    try:
                        return datetime.strptime(extracted_date, date_format)
                    except ValueError:
                        continue
        
        return None
    
    def get_purchases_by_date(self) -> defaultdict:
        """
        Parse the CSV file and organize Fandango purchases by date.

        Returns:
            defaultdict: Dictionary where keys are dates (YYYY-MM-DD) and values are lists of movie dictionaries.
        """
        purchases_by_date = defaultdict(list)
        
        # Check for CSV file
        if not self.fandango_csv_file or not os.path.exists(self.fandango_csv_file):
            self.last_error = "Fandango CSV file not found"
            print(f"{self.last_error}: {self.fandango_csv_file}")
            return purchases_by_date
            
        # Parse the CSV file to get movie entries
        try:
            movie_entries = []
            
            with open(self.fandango_csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    movie_entries.append({
                        'movie_name': row.get('Movie', ''),
                        'date_time': row.get('Date', ''),
                        'theater_name': row.get('Theater', ''),
                        'theater_address': row.get('Address', '')
                    })
            
            if not movie_entries:
                self.last_error = "No movie entries found in the CSV file"
                print(self.last_error)
                return purchases_by_date
                
            # Track entries with missing dates
            entries_with_missing_dates = 0
            
            for entry in movie_entries:
                # Parse the date and format it
                date_obj = self._parse_date(entry.get('date_time', ''))
                if not date_obj:
                    entries_with_missing_dates += 1
                    continue
                
                formatted_date = date_obj.strftime('%Y-%m-%d')
                
                # Add the full movie entry to the date's list
                purchases_by_date[formatted_date].append({
                    'movie_name': entry.get('movie_name', ''),
                    'theater_name': entry.get('theater_name', ''),
                    'theater_address': entry.get('theater_address', '')
                })
            
            # Debug: Show found dates
            print(f"Found Fandango purchase history for {len(purchases_by_date)} dates from CSV")
            if entries_with_missing_dates > 0:
                print(f"Skipped {entries_with_missing_dates} entries with missing or invalid dates")
                
            date_sample = list(purchases_by_date.keys())[:5] if purchases_by_date else []
            print(f"Sample dates: {date_sample}")
            
            if not purchases_by_date:
                self.last_error = "No purchase dates could be extracted from the movie entries"
            
            return purchases_by_date
            
        except Exception as e:
            self.last_error = f"Error parsing purchase data: {str(e)}"
            print(self.last_error)
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
                
            # Check if the file already contains Movies Attended section
            return "## Movies Attended" in content
        except Exception as e:
            print(f"Error checking file for Fandango history: {e}")
            return False

    def delete_fandango_history_file(self) -> bool:
        """
        Delete the Fandango history file after processing.
        
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not self.fandango_csv_file or not os.path.exists(self.fandango_csv_file):
            print(f"Fandango CSV file not found for deletion: {self.fandango_csv_file}")
            return False
            
        try:
            os.remove(self.fandango_csv_file)
            print(f"Successfully deleted Fandango CSV file: {self.fandango_csv_file}")
            return True
        except Exception as e:
            print(f"Error deleting Fandango CSV file {self.fandango_csv_file}: {e}")
            return False

    def append_purchases_to_files(self, delete_after_processing: bool = False) -> bool:
        """
        Process Fandango purchase history data from CSV. For each date with purchases,
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

        # Get purchases from CSV
        purchases_by_date = self.get_purchases_by_date()
        
        if not purchases_by_date:
            print("No Fandango purchase history data found to process.")
            return False

        processed_files = 0
        created_files = 0
        # Iterate through each date found in the Fandango history
        for file_date, purchase_data in purchases_by_date.items():
            try:
                # Extract year and month name from the date string (YYYY-MM-DD)
                date_obj = datetime.strptime(file_date, '%Y-%m-%d')
                year = date_obj.strftime('%Y')
                month = date_obj.strftime('%m') # Get month number (e.g., 02)
                month_name = date_obj.strftime('%B') # Get full month name (e.g., February)

                # Construct the target directory path as TARGET_DIR/YYYY/MM-Month/
                target_subdir = os.path.join(self.target_dir, year, f"{month}-{month_name}")
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
                
                # Generate markdown for the movie attendance
                movies_markdown = self.markdown_generator.generate_movies_attended_markdown(purchase_data)

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
                                file.write(movies_markdown)
                            print(f"  Appended Fandango history to existing file: {file_name}")
                            processed_files += 1
                        except Exception as e:
                            print(f"  Error appending to existing file {file_name}: {e}")

                else:
                    # File does not exist, create it and add history
                    print(f"  File does not exist, creating: {file_path}")
                    try:
                        with open(file_path, mode="w", encoding="utf-8") as file:
                            # Add the movie attendance section
                            file.write(movies_markdown)
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
            # Delete CSV file if it exists
            csv_deleted = self.delete_fandango_history_file()
            
            # Import and call the function to delete the fandango directory
            from fandango_downloader import delete_fandango_directory
            dir_deleted = delete_fandango_directory()
            
            # Return true only if both operations were successful
            return csv_deleted and dir_deleted
            
        return True