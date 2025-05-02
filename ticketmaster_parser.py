import os
import csv
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

class TicketmasterProcessor:
    """
    Class to process and append Ticketmaster/event history from CSV file to markdown files.
    """

    def __init__(self, config: Dict):
        """
        Initialize the processor with configuration.

        Args:
            config (Dict): Configuration dictionary.
        """
        self.target_dir = config.get("TARGET_DIR", "")
        self.csv_file_path = config.get("TICKET_MASTER_CSV_FILE", "")
        self.last_error = None
        
        # Add debug output to verify file path and existence
        print(f"DEBUG: TicketmasterProcessor initialized with:")
        print(f"DEBUG: Target directory: {self.target_dir}")
        print(f"DEBUG: CSV file path: {self.csv_file_path}")
        print(f"DEBUG: CSV file exists: {os.path.exists(self.csv_file_path)}")
        if os.path.exists(self.csv_file_path):
            try:
                with open(self.csv_file_path, 'r', encoding='utf-8') as f:
                    print(f"DEBUG: CSV file can be opened successfully")
                    first_line = f.readline().strip()
                    print(f"DEBUG: CSV file first line: {first_line}")
            except Exception as e:
                print(f"DEBUG: Error opening CSV file: {e}")

    def get_events_by_date(self) -> defaultdict:
        """
        Read the CSV file and organize events by date.

        Returns:
            defaultdict: A dictionary where keys are dates (YYYY-MM-DD) and values are lists of events.
        """
        events_by_date = defaultdict(list)

        if not self.csv_file_path or not os.path.exists(self.csv_file_path):
            self.last_error = f"Ticketmaster CSV file not found: {self.csv_file_path}"
            print(self.last_error)
            return events_by_date

        try:
            # Modified approach: Read the file manually to handle CSV formatting issues
            with open(self.csv_file_path, mode="r", encoding="utf-8") as file:
                # Skip header line
                header = file.readline().strip()
                print(f"DEBUG: CSV header: {header}")
                
                # Process each line manually
                row_count = 0
                processed_rows = 0
                skipped_rows = 0
                
                for line in file:
                    row_count += 1
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                    
                    # Count the commas to determine the field boundaries
                    parts = line.split(',')
                    
                    # Checking for proper structure
                    if len(parts) >= 3:
                        # For dates like "Feb 29, 2020", the split will produce:
                        # ["Feb 29", " 2020", "location", "event"]
                        # Need to reconstruct the date properly
                        date_str = parts[0]
                        
                        # If date appears to be split because it contains a comma
                        if len(parts) > 3 and not date_str.strip().endswith(')'):
                            # Merge the first two parts for the date
                            date_str = date_str + "," + parts[1]
                            # Shift the remaining parts
                            location = parts[2] if len(parts) > 2 else ""
                            event = ','.join(parts[3:]) if len(parts) > 3 else ""
                        else:
                            # Normal case without comma in date
                            location = parts[1] if len(parts) > 1 else ""
                            event = ','.join(parts[2:]) if len(parts) > 2 else ""
                    else:
                        # If we don't have enough parts, try to extract what we can
                        date_str = parts[0] if parts else ""
                        location = parts[1] if len(parts) > 1 else ""
                        event = parts[2] if len(parts) > 2 else ""
                    
                    # Debug output for the first few rows
                    if row_count <= 5:
                        print(f"DEBUG: Line {row_count}: {line}")
                        print(f"DEBUG: Parsed - date: '{date_str}', location: '{location}', event: '{event}'")
                    
                    # Skip if no date or event
                    if not date_str or not event:
                        skipped_rows += 1
                        if row_count <= 5:
                            print(f"DEBUG: Skipping row {row_count} - missing date or event")
                        continue
                    
                    # Convert date string to standard format
                    try:
                        formatted_date = self._format_date(date_str)
                        if formatted_date:
                            events_by_date[formatted_date].append({
                                "event": event,
                                "location": location
                            })
                            processed_rows += 1
                            if row_count <= 5:
                                print(f"DEBUG: Successfully added event for date: {formatted_date}")
                        else:
                            skipped_rows += 1
                            if row_count <= 5:
                                print(f"DEBUG: Failed to format date: '{date_str}'")
                    except Exception as e:
                        skipped_rows += 1
                        print(f"Error parsing date '{date_str}': {e}")
            
            print(f"DEBUG: Total rows: {row_count}, Processed: {processed_rows}, Skipped: {skipped_rows}")
            print(f"Found ticketmaster events for {len(events_by_date)} dates")
            if events_by_date:
                sample_dates = list(events_by_date.keys())[:5]
                print(f"Sample dates: {sample_dates}")
            
        except Exception as e:
            self.last_error = f"Error processing Ticketmaster CSV file: {e}"
            print(self.last_error)
        
        return events_by_date
    
    def _format_date(self, date_string: str) -> Optional[str]:
        """
        Format the date string to a standard format (YYYY-MM-DD).
        
        Args:
            date_string (str): The date string from the CSV.
            
        Returns:
            str or None: Formatted date string in YYYY-MM-DD format, or None if parsing fails.
        """
        if not date_string:
            return None
        
        print(f"DEBUG: Attempting to format date: '{date_string}'")
        
        # List of date formats to try
        date_formats = [
            '%Y-%m-%d',              # YYYY-MM-DD
            '%b %d, %Y',             # Feb 29, 2020
            '%B %d, %Y',             # February 29, 2020
            '%m/%d/%Y',              # MM/DD/YYYY
            '%m/%d/%y',              # MM/DD/YY
            '%d %b %Y',              # 29 Feb 2020 
            '%d %B %Y',              # 29 February 2020
        ]
        
        for fmt in date_formats:
            try:
                print(f"DEBUG: Trying format '{fmt}' for date '{date_string}'")
                date_obj = datetime.strptime(date_string, fmt)
                formatted_date = date_obj.strftime('%Y-%m-%d')
                print(f"DEBUG: Successfully parsed '{date_string}' to '{formatted_date}' using format '{fmt}'")
                return formatted_date
            except ValueError:
                continue
        
        print(f"DEBUG: Failed to parse date '{date_string}' with any format")
        return None
    
    def file_already_has_events(self, file_path: str) -> bool:
        """
        Check if the file already has an events section.
        
        Args:
            file_path (str): Path to the markdown file.
            
        Returns:
            bool: True if the file already has an events section, False otherwise.
        """
        if not os.path.exists(file_path):
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check if the file already contains events section
            return "## Events" in content
        except Exception as e:
            print(f"Error checking file for events section: {e}")
            return False

    def append_events_to_files(self) -> bool:
        """
        Process Ticketmaster event data. For each date with events, ensure a corresponding
        markdown file exists in the correct Year/Month Name subdirectory and append
        the events if they're not already present. Creates files and directories if needed.
        
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
        
        # Get events organized by date
        events_by_date = self.get_events_by_date()
        
        if not events_by_date:
            print("No Ticketmaster event data found to process.")
            return False
        
        processed_files = 0
        created_files = 0
        
        # Iterate through each date found in the events
        for file_date, events in events_by_date.items():
            try:
                # Extract year and month name from the date string (YYYY-MM-DD)
                date_obj = datetime.strptime(file_date, '%Y-%m-%d')
                year = date_obj.strftime('%Y')
                month_number = date_obj.strftime('%m')  # Get month number (e.g., 02)
                month_name = date_obj.strftime('%B')  # Get full month name (e.g., February)
                
                # Construct the target directory path including Year/Month structure
                target_subdir = os.path.join(self.target_dir, year, f"{month_number}-{month_name}")
                file_name = f"{file_date}.md"
                file_path = os.path.join(target_subdir, file_name)
                
                print(f"Processing events for date: {file_date} -> {file_path}")
                
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
                
                # Format the events as markdown
                events_content = "\n## Events\n\n"
                for event in events:
                    if event["location"]:
                        events_content += f"{file_date}: {event['event']}, {event['location']}\n"
                    else:
                        events_content += f"{file_date}: {event['event']}\n"
                
                # Check if the target file exists
                if os.path.exists(file_path):
                    print(f"  File exists: {file_path}")
                    
                    # Check if file is writable
                    if not os.access(file_path, os.W_OK):
                        print(f"  Error: File is not writable: {file_path}")
                        continue
                        
                    # Check if file already has events section
                    if self.file_already_has_events(file_path):
                        print(f"  File {file_name} already has events section. Skipping.")
                        continue
                    
                    # Append events to existing file
                    try:
                        with open(file_path, mode="a", encoding="utf-8") as file:
                            file.write("\n" + events_content)
                        print(f"  Appended events to existing file: {file_name}")
                        processed_files += 1
                    except Exception as e:
                        print(f"  Error appending to existing file {file_name}: {e}")
                
                else:
                    # File does not exist, create it and add events
                    print(f"  File does not exist, creating: {file_path}")
                    try:
                        with open(file_path, mode="w", encoding="utf-8") as file:
                            file.write(events_content)
                        print(f"  Created file and added events: {file_name}")
                        created_files += 1
                    except Exception as e:
                        print(f"  Error creating file {file_name}: {e}")
            
            except ValueError:
                print(f"Skipping invalid date format: {file_date}")
                continue
            except Exception as e:
                print(f"An unexpected error occurred processing date {file_date}: {e}")
                continue
        
        print(f"Finished processing Ticketmaster events. Appended to {processed_files} existing file(s), created {created_files} new file(s).")
        return True