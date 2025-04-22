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
        # Check if the target directory exists upon initialization
        if not self.target_dir or not os.path.exists(self.target_dir):
            print(f"ERROR: Target directory specified in config does not exist: {self.target_dir}")
            # Optionally, create the directory:
            # try:
            #     os.makedirs(self.target_dir)
            #     print(f"Created directory: {self.target_dir}")
            # except OSError as e:
            #     print(f"Error creating directory {self.target_dir}: {e}")
            #     self.target_dir = None # Mark as invalid if creation fails
            self.target_dir = None # Mark directory as invalid if it doesn't exist
        elif not os.path.isdir(self.target_dir):
            print(f"ERROR: Target path specified in config is not a directory: {self.target_dir}")
            self.target_dir = None # Mark directory as invalid

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