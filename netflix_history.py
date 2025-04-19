import os
import csv
from datetime import datetime
from typing import Dict, List
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
        self.netflix_file_path = config.get("NETFLIX_FILE_LOCATION", "")

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

    def append_shows_to_files(self):
        """
        Append Netflix shows to markdown files in the target directory based on the date in the file name.
        """
        if not os.path.exists(self.target_dir):
            print(f"Target directory not found: {self.target_dir}")
            return

        # Get shows organized by date
        shows_by_date = self.get_shows_by_date()

        # Process each markdown file in the target directory
        for file_name in os.listdir(self.target_dir):
            if file_name.endswith(".md"):
                file_date = os.path.splitext(file_name)[0]  # Extract date from file name
                file_path = os.path.join(self.target_dir, file_name)

                if file_date in shows_by_date:
                    print(f"Checking Netflix history for file: {file_name}")
                    
                    # Check if file already has Netflix history section
                    if self.file_already_has_netflix_history(file_path):
                        print(f"File {file_name} already has Netflix history section. Skipping.")
                        continue
                    
                    # Append Netflix history
                    with open(file_path, mode="a", encoding="utf-8") as file:
                        file.write("\n## Netflix Viewing History\n\n")
                        file.write("\n".join(shows_by_date[file_date]))
                        file.write("\n")
                    print(f"Added Netflix history to {file_name}")
                else:
                    print(f"No Netflix shows found for date {file_date}")