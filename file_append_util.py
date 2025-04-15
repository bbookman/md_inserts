from typing import Any

class Append:
    """
    Generic class for appending data to a file.
    """

    def append_to_file(self, file_path: str, data: Any) -> None:
        """
        Appends the given data to the specified file.

        Args:
            file_path (str): The path to the file to append to.
            data (Any): The data to append. If not a string, it will be converted.
        """
        with open(file_path, 'a', encoding='utf-8') as f:
            if not isinstance(data, str):
                data = str(data)
            f.write(data + '\n')

# Example usage:
# append_util = Append()
# append_util.append_to_file('example.md', 'This is a new line to append.')