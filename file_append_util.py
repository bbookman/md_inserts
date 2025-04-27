from typing import Any
import os

class Append:
    """
    Generic class for appending data to a file.
    """

    def append_to_file(self, file_path: str, data: Any) -> bool:
        """
        Appends the given data to the specified file.

        Args:
            file_path (str): The path to the file to append to.
            data (Any): The data to append. If not a string, it will be converted.
            
        Returns:
            bool: True if the append operation was successful, False otherwise.
        """
        try:
            # Validate that the directory exists, create it if it doesn't
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    print(f"Created directory: {directory}")
                except OSError as e:
                    print(f"Error creating directory {directory}: {e}")
                    return False
            
            # Check if the directory is writable
            if directory and not os.access(directory, os.W_OK):
                print(f"Error: Directory {directory} is not writable")
                return False
                
            # If appending to an existing file, check if it's writable
            if os.path.exists(file_path) and not os.access(file_path, os.W_OK):
                print(f"Error: File {file_path} is not writable")
                return False
                
            # Now perform the write operation
            with open(file_path, 'a', encoding='utf-8') as f:
                if not isinstance(data, str):
                    data = str(data)
                f.write(data + '\n')
            return True
        except Exception as e:
            print(f"Error appending to file {file_path}: {e}")
            return False

# Example usage:
# append_util = Append()
# append_util.append_to_file('example.md', 'This is a new line to append.')