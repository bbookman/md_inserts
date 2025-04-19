import os
import csv
from typing import Dict, List
from collections import defaultdict

class MusicHistoryProcessor:
    """
    Class to process and append music history to markdown files.
    """

    def __init__(self, config: Dict):
        """
        Initialize the processor with configuration.

        Args:
            config (Dict): Configuration dictionary.
        """
        self.target_dir = config.get("TARGET_DIR", "")
        self.music_file_path = config.get("APPLE_MUSIC_FILE_PATH", "")

    def get_tracks_by_date(self) -> defaultdict:
        """
        Read the CSV file and organize tracks by date.
        Uses a file with columns: "Track Name", "Last Played Date", "Is User Initiated".
        Last Played Date is in Unix epoch timestamp (milliseconds).

        Returns:
            defaultdict: A dictionary where keys are dates (YYYY-MM-DD) and values are lists of unique tracks.
        """
        tracks_by_date = defaultdict(list)

        if not os.path.exists(self.music_file_path):
            print(f"Music file not found: {self.music_file_path}")
            return tracks_by_date

        try:
            with open(self.music_file_path, mode="r", encoding="utf-8") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    # Get track name
                    track_name = row.get("Track Name", "")
                    
                    # Convert Unix timestamp (milliseconds) to datetime
                    try:
                        timestamp_ms = int(row.get("Last Played Date", "0"))
                        from datetime import datetime
                        date_played = datetime.fromtimestamp(timestamp_ms / 1000)  # Convert ms to seconds
                        formatted_date = date_played.strftime('%Y-%m-%d')
                        
                        # Create a simple bullet point entry
                        track_entry = f"* {track_name}"
                        
                        # Avoid duplicates for the same date
                        if track_entry not in tracks_by_date[formatted_date]:
                            tracks_by_date[formatted_date].append(track_entry)
                    except (ValueError, TypeError):
                        # Skip rows with invalid timestamps
                        continue
        except Exception as e:
            print(f"Error processing music file: {e}")
        
        return tracks_by_date

    def append_tracks_to_files(self):
        """
        Append tracks to markdown files in the target directory based on the date in the file name.
        Uses a simple bullet point format with just the track names.
        """
        if not os.path.exists(self.target_dir):
            print(f"Target directory not found: {self.target_dir}")
            return

        # Get tracks organized by date
        tracks_by_date = self.get_tracks_by_date()

        # Process each markdown file in the target directory
        for file_name in os.listdir(self.target_dir):
            if file_name.endswith(".md"):
                file_date = os.path.splitext(file_name)[0]  # Extract date from file name
                file_path = os.path.join(self.target_dir, file_name)

                if file_date in tracks_by_date:
                    print(f"Appending tracks for date {file_date} to file {file_name}")
                    
                    # Check if file already has music history section
                    with open(file_path, mode="r", encoding="utf-8") as file:
                        content = file.read()
                        if "## Music Listening History" in content:
                            print(f"File {file_name} already has music history section. Skipping.")
                            continue
                    
                    # Append music history
                    with open(file_path, mode="a", encoding="utf-8") as file:
                        file.write("\n## Music Listening History\n\n")
                        file.write("\n".join(tracks_by_date[file_date]))
                        file.write("\n")
                else:
                    print(f"No tracks found for date {file_date}")