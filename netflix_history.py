import os
import csv
import glob
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

class NetflixHistoryProcessor:
    """
    Class to process and append Netflix viewing history to markdown files.
    """

    def __init__(self, config: Dict):
        """
        Initialize the processor with configuration.

        Args:
            config (Dict): Configuration dictionary.
        """
        self.target_dir = config.get("TARGET_DIR", "")
        self.netflix_file_path = self._find_netflix_history_file(config.get("NETFLIX_FILE_LOCATION", ""))
    
    def _find_netflix_history_file(self, file_path: str) -> str:
        """
        Find the first Netflix viewing history file in the directory.
        Handles cases where the file might be named differently (e.g., NetflixViewingHistory(1).csv).
        
        Args:
            file_path (str): Path specified in the config.
            
        Returns:
            str: Path to the first matching Netflix viewing history file.
        """
        # Extract directory and base filename
        directory = os.path.dirname(file_path)
        
        # If we can't find the directory, return the original path
        if not os.path.exists(directory):
            print(f"Netflix history directory not found: {directory}")
            return file_path
            
        # Look for any file that starts with NetflixViewingHistory and ends with .csv
        netflix_files = glob.glob(os.path.join(directory, "NetflixViewingHistory*.csv"))
        
        if netflix_files:
            # Sort by modification time (newest first)
            netflix_files.sort(key=os.path.getmtime, reverse=True)
            print(f"Found Netflix history file: {netflix_files[0]}")
            return netflix_files[0]
        else:
            print(f"No Netflix history files found in: {directory}")
            return file_path
    
    def get_shows_by_date(self) -> defaultdict:
        """
        Read the CSV file and organize Netflix shows by date.

        Returns:
            defaultdict: A dictionary where keys are dates (YYYY-MM-DD) and values are lists of unique shows.
        """
        shows_by_date = defaultdict(list)

        if not os.path.exists(self.netflix_file_path):
            print(f"Netflix history file not found: {self.netflix_file_path}")
            return shows_by_date

        try:
            with open(self.netflix_file_path, mode="r", encoding="utf-8") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    # Get title and date viewed
                    title = row.get("Title", "")
                    date_viewed = row.get("Date", "")
                    
                    # Skip if missing data
                    if not title or not date_viewed:
                        continue
                    
                    # Convert MM/DD/YY date format to YYYY-MM-DD
                    try:
                        date_obj = datetime.strptime(date_viewed, "%m/%d/%y")
                        formatted_date = date_obj.strftime('%Y-%m-%d')
                        
                        # Create a simple bullet point entry
                        show_entry = f"* {title}"
                        
                        # Avoid duplicates for the same date
                        if show_entry not in shows_by_date[formatted_date]:
                            shows_by_date[formatted_date].append(show_entry)
                    except (ValueError, TypeError):
                        print(f"Could not parse date: {date_viewed} for title: {title}")
                        continue
            
            # Debug: Show found dates
            print(f"Found Netflix history for {len(shows_by_date)} dates")
            date_sample = list(shows_by_date.keys())[:5] if shows_by_date else []
            print(f"Sample dates: {date_sample}")
            
        except Exception as e:
            print(f"Error processing Netflix file: {e}")
        
        return shows_by_date

    def file_already_has_netflix_history(self, file_path: str) -> bool:
        """
        Check if a file already contains Netflix history section.
        
        Args:
            file_path (str): Path to the markdown file.
            
        Returns:
            bool: True if the file already has Netflix history, False otherwise.
        """
        try:
            if not os.path.exists(file_path):
                return False
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check if the file already contains Netflix history section
            return "## Netflix Viewing History" in content
        except Exception as e:
            print(f"Error checking file for Netflix history: {e}")
            return False

    def delete_netflix_history_file(self) -> bool:
        """
        Delete the Netflix history CSV file after processing.
        
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not self.netflix_file_path or not os.path.exists(self.netflix_file_path):
            print(f"Netflix history file not found for deletion: {self.netflix_file_path}")
            return False
            
        try:
            os.remove(self.netflix_file_path)
            print(f"Successfully deleted Netflix history file: {self.netflix_file_path}")
            return True
        except Exception as e:
            print(f"Error deleting Netflix history file {self.netflix_file_path}: {e}")
            return False

    def append_shows_to_files(self, delete_after_processing: bool = False) -> bool:
        """
        Process Netflix history data. For each date with viewing history,
        ensure a corresponding markdown file exists in the correct Year/Month Name subdirectory
        and append the history if it's not already present. Creates the file and directories if needed.
        
        Args:
            delete_after_processing (bool): Whether to delete the Netflix history file after processing.
            
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

        # Get shows organized by date (YYYY-MM-DD)
        shows_by_date = self.get_shows_by_date()

        if not shows_by_date:
            print("No Netflix history data found to process.")
            return False

        processed_files = 0
        created_files = 0
        # Iterate through each date found in the Netflix history
        for file_date, shows in shows_by_date.items():
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

                print(f"Processing Netflix date: {file_date} -> {file_path}")

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
                        
                    # Check if file already has Netflix history section
                    if self.file_already_has_netflix_history(file_path):
                        print(f"  File {file_name} already has Netflix history section. Skipping.")
                        continue
                    else:
                        # Append Netflix history to existing file
                        try:
                            with open(file_path, mode="a", encoding="utf-8") as file:
                                file.write("\n## Netflix Viewing History\n\n")
                                file.write("\n".join(shows))
                                file.write("\n")
                            print(f"  Appended Netflix history to existing file: {file_name}")
                            processed_files += 1
                        except Exception as e:
                            print(f"  Error appending to existing file {file_name}: {e}")

                else:
                    # File does not exist, create it and add history
                    print(f"  File does not exist, creating: {file_path}")
                    try:
                        with open(file_path, mode="w", encoding="utf-8") as file:
                            # Add the Netflix history section (Removed Journal Entry header)
                            file.write("## Netflix Viewing History\n\n")
                            file.write("\n".join(shows))
                            file.write("\n")
                        print(f"  Created file and added Netflix history: {file_name}")
                        created_files += 1
                    except Exception as e:
                        print(f"  Error creating file {file_name}: {e}")
            except ValueError:
                 print(f"Skipping invalid date format: {file_date}")
                 continue
            except Exception as e:
                 print(f"An unexpected error occurred processing date {file_date}: {e}")
                 continue

        print(f"Finished processing Netflix history. Appended to {processed_files} existing file(s), created {created_files} new file(s).")
        
        # Delete the history file if requested and there was at least one file processed
        if delete_after_processing and (processed_files > 0 or created_files > 0):
            return self.delete_netflix_history_file()
            
        return True