import os
import csv
from datetime import datetime
from typing import Dict, List, Optional
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

    def file_already_has_music_history(self, file_path: str) -> bool:
        """
        Check if the file already has a music history section.

        Args:
            file_path (str): Path to the markdown file.

        Returns:
            bool: True if the file already has a music history section, False otherwise.
        """
        try:
            with open(file_path, mode="r", encoding="utf-8") as file:
                content = file.read()
                return "## Music Listening History" in content
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return False

    def append_tracks_to_files(self):
        """
        Append music tracks to markdown files in the target directory and subdirectories
        based on the date in the file name.
        """
        if not os.path.exists(self.target_dir):
            print(f"Target directory not found: {self.target_dir}")
            return

        # Get tracks organized by date
        tracks_by_date = self.get_tracks_by_date()

        if not tracks_by_date:
            print("No music history data found to process.")
            return

        processed_files = 0
        # Use os.walk for recursive search
        for root, dirs, files in os.walk(self.target_dir):
            for file_name in files:
                if file_name.endswith(".md"):
                    file_path = os.path.join(root, file_name)
                    # Extract date from file name (assuming YYYY-MM-DD.md)
                    file_date = os.path.splitext(file_name)[0]

                    if file_date in tracks_by_date:
                        print(f"Checking music history for file: {file_path}")

                        # Check if file already has music history section
                        if self.file_already_has_music_history(file_path):
                            print(f"  File already has music history section. Skipping.")
                            continue

                        # Append music history
                        try:
                            with open(file_path, mode="a", encoding="utf-8") as file:
                                file.write("\n## Apple Music Play History\n\n")
                                file.write("\n".join(tracks_by_date[file_date]))
                                file.write("\n")
                            print(f"  Added music history to {file_name}")
                            processed_files += 1
                        except Exception as e:
                            print(f"  Error appending music history to {file_name}: {e}")
                    # else: # Optional: Log if no music found for a file's date
                    #     print(f"No music tracks found for date {file_date} (file: {file_name})")

        print(f"Finished processing music history. Updated {processed_files} file(s).")