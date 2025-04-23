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
        if not self.target_dir:
            print(f"ERROR: No target directory specified in config.")
            self.target_dir = None
        elif not os.path.exists(self.target_dir):
            print(f"Target directory specified in config does not exist: {self.target_dir}")
            try:
                # Create the directory structure if it doesn't exist
                os.makedirs(self.target_dir, exist_ok=True)
                print(f"Created target directory: {self.target_dir}")
            except OSError as e:
                print(f"ERROR: Failed to create target directory {self.target_dir}: {e}")
                print(f"ERROR details - errno: {e.errno}, strerror: {e.strerror}, filename: {e.filename}")
                self.target_dir = None  # Mark as invalid if creation fails
        elif not os.path.isdir(self.target_dir):
            print(f"ERROR: Target path specified in config is not a directory: {self.target_dir}")
            self.target_dir = None  # Mark as invalid if not a directory

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