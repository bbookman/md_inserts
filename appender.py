import os
from typing import Optional

class Appender:
    """
    Class for appending content to files.
    """
    
    def append_file(self, markdown: str, target_file: str) -> bool:
        """
        Append markdown content to the specified file.
        
        Args:
            markdown (str): Content to append to the file
            target_file (str): Path to the file to append to
            
        Returns:
            bool: True if append was successful, False otherwise
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            
            # Append content to the file
            with open(target_file, 'a', encoding='utf-8') as file:
                file.write('\n\n' + markdown)
            
            return True
        except Exception as e:
            print(f"Error appending to file {target_file}: {e}")
            return False