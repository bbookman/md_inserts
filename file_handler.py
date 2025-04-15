import os
import json
from datetime import datetime, timedelta
from typing import Optional

class FILE_HANDLER:
    """
    Class for handling file operations related to date-based markdown files.
    """
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the file handler with configuration.
        
        Args:
            config_path (str): Path to the configuration file.
        """
        self.config = self._load_config(config_path)
        self.target_dir = self.config.get('TARGET_DIR', '')
        
    def _load_config(self, config_path: str) -> dict:
        """
        Load configuration from file.
        
        Args:
            config_path (str): Path to the configuration file.
            
        Returns:
            dict: Configuration data.
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def get_yesturday_file(self) -> Optional[str]:
        """
        Get the file path for yesterday's date formatted as YYYY-MM-DD.md.
        
        Returns:
            Optional[str]: Full path to yesterday's file if it exists, None otherwise.
        """
        # Get today's date and subtract one day
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        # Format the date as YYYY-MM-DD
        file_name = yesterday.strftime('%Y-%m-%d.md')
        
        # Build the full path
        file_path = os.path.join(self.target_dir, file_name)
        
        # Debug information
        print(f"Looking for file: {file_path}")
        print(f"Directory exists: {os.path.exists(self.target_dir)}")
        print(f"Directory contents: {os.listdir(self.target_dir)}")
        print(f"File exists (isfile): {os.path.isfile(file_path)}")
        print(f"File exists (exists): {os.path.exists(file_path)}")
        
        # Check if the file exists
        if os.path.isfile(file_path):
            return file_path
        else:
            print(f"File {file_path} does not exist.")
            return None