import os
import json
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

class YelpReviewProcessor:
    """
    Class for parsing Yelp HTML tables with user reviews and appending them to markdown files.
    Extracts Date, Business Name, Rating, and Comment columns.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the parser with configuration.

        Args:
            config (Dict[str, Any]): Configuration dictionary containing path to HTML file and target directory.
        """
        self.html_file_path = config.get("YELP_USER_REVIEWS_HTML", "")
        self.target_dir = config.get("TARGET_DIR", "")
        
    def _validate_file_exists(self) -> bool:
        """
        Validate that the HTML file exists.

        Returns:
            bool: True if file exists, False otherwise.
        """
        if not self.html_file_path:
            print("Error: YELP_USER_REVIEWS_HTML path not specified in config")
            return False
            
        if not os.path.exists(self.html_file_path):
            print(f"Error: Yelp HTML file not found: {self.html_file_path}")
            return False
            
        return True
    
    def parse_review_table(self) -> List[Dict[str, Any]]:
        """
        Parse the HTML table and extract Date, Business Name, Rating, and Comment.

        Returns:
            List[Dict[str, Any]]: List of dictionaries with review data.
        """
        if not self._validate_file_exists():
            return []
            
        reviews = []
        
        try:
            # Read and parse the HTML file
            with open(self.html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
                
            # Parse HTML using Beautiful Soup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the table - in this case we're looking for the table with review data
            table = soup.find('table')
            
            if not table:
                print("Error: Could not find table in HTML file")
                return []
                
            # Get all rows except the header row
            rows = table.find_all('tr')
            
            # Process the rows to extract data
            for row in rows:
                # Skip header row if it exists
                if row.find('th'):
                    continue
                    
                cells = row.find_all('td')
                
                # Make sure we have enough cells for our columns of interest
                if len(cells) >= 4:
                    # Extract and clean data - we need the Date, Business Name, Rating, and Comment
                    date_text = cells[0].text.strip() if cells[0] else ""
                    business_name = cells[1].text.strip() if cells[1] else ""
                    rating = cells[2].text.strip() if cells[2] else ""
                    comment = cells[3].text.strip() if cells[3] else ""
                    
                    # Try to format the date properly
                    formatted_date = self._format_date(date_text)
                    
                    # Try to convert rating to numeric value
                    numeric_rating = self._parse_rating(rating)
                    
                    # Create review object
                    review = {
                        "date": formatted_date,
                        "business_name": business_name,
                        "rating": numeric_rating,
                        "comment": comment
                    }
                    
                    reviews.append(review)
            
            print(f"Successfully parsed {len(reviews)} reviews from Yelp HTML file")
            
        except Exception as e:
            print(f"Error parsing Yelp HTML file: {e}")
            
        return reviews
    
    def _format_date(self, date_string: str) -> str:
        """
        Format the date string to a standard format (ISO format).
        
        Args:
            date_string (str): The date string from the HTML table.
            
        Returns:
            str: Formatted date string in ISO format.
        """
        try:
            # The dates in the Yelp table appear to be in ISO format already (YYYY-MM-DDTHH:MM:SS+00:00)
            # Parse and standardize the date
            date_obj = datetime.strptime(date_string.strip(), "%Y-%m-%dT%H:%M:%S+00:00")
            return date_obj.strftime("%Y-%m-%d")
        except Exception:
            # If we can't parse it, return as is
            return date_string
            
    def _parse_rating(self, rating_string: str) -> float:
        """
        Parse rating string to numeric value.
        
        Args:
            rating_string (str): The rating string from the HTML table.
            
        Returns:
            float: Numeric rating value.
        """
        try:
            # Extract numbers from string, handling edge cases
            cleaned_rating = rating_string.strip()
            return float(cleaned_rating)
        except Exception:
            # If we can't parse it, return 0
            return 0.0
    
    def get_reviews_as_json(self) -> str:
        """
        Get reviews as a JSON string.
        
        Returns:
            str: JSON string containing review data.
        """
        reviews = self.parse_review_table()
        return json.dumps(reviews, indent=2)
    
    def get_reviews_as_dict(self) -> List[Dict[str, Any]]:
        """
        Get reviews as a list of dictionaries.
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries with review data.
        """
        return self.parse_review_table()
    
    def get_reviews_by_date(self) -> defaultdict:
        """
        Organize reviews by date.
        
        Returns:
            defaultdict: A dictionary where keys are dates (YYYY-MM-DD) and values are lists of reviews for that date.
        """
        reviews_by_date = defaultdict(list)
        
        # Get all reviews
        reviews = self.parse_review_table()
        
        # Group reviews by date
        for review in reviews:
            date = review.get("date")
            # Only add if we have a valid date
            if date and len(date) == 10:  # YYYY-MM-DD format is 10 characters
                reviews_by_date[date].append(review)
        
        return reviews_by_date
    
    def file_already_has_yelp_reviews(self, file_path: str) -> bool:
        """
        Check if the file already has a Yelp reviews section.
        
        Args:
            file_path (str): Path to the markdown file.
            
        Returns:
            bool: True if the file already has Yelp reviews, False otherwise.
        """
        try:
            if not os.path.exists(file_path):
                return False
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check if the file already contains Yelp reviews section
            return "## Yelp Reviews" in content
        except Exception as e:
            print(f"Error checking file for Yelp reviews: {e}")
            return False
    
    def format_reviews_as_markdown_table(self, reviews: List[Dict[str, Any]]) -> str:
        """
        Format reviews as a markdown table.
        
        Args:
            reviews (List[Dict[str, Any]]): List of review dictionaries.
            
        Returns:
            str: Markdown table string.
        """
        if not reviews:
            return ""
            
        # Create table header
        markdown = "| Business | Rating | Review |\n"
        markdown += "|---------|--------|--------|\n"
        
        # Add table rows
        for review in reviews:
            business = review.get("business_name", "").replace("|", "\\|")  # Escape pipe characters
            rating = str(review.get("rating", ""))
            comment = review.get("comment", "").replace("|", "\\|").replace("\n", " ")  # Escape pipes and replace newlines
            
            # Truncate long comments for readability in the table
            if len(comment) > 100:
                comment = comment[:97] + "..."
                
            markdown += f"| {business} | {rating} | {comment} |\n"
            
        return markdown
    
    def append_reviews_to_files(self):
        """
        Process Yelp review data. For each date with reviews, ensure a corresponding 
        markdown file exists in the correct Year/Month Name subdirectory and append 
        the reviews if they're not already present. Creates files and directories if needed.
        """
        if not os.path.exists(self.target_dir):
            print(f"Target directory not found: {self.target_dir}")
            return
            
        # Check if target directory is writable
        if not os.access(self.target_dir, os.W_OK):
            print(f"Error: Target directory is not writable: {self.target_dir}")
            return
        
        # Get reviews organized by date (YYYY-MM-DD)
        reviews_by_date = self.get_reviews_by_date()
        
        if not reviews_by_date:
            print("No Yelp review data found to process.")
            return
        
        processed_files = 0
        created_files = 0
        # Iterate through each date found in the reviews
        for file_date, reviews in reviews_by_date.items():
            try:
                # Extract year and month name from the date string (YYYY-MM-DD)
                date_obj = datetime.strptime(file_date, '%Y-%m-%d')
                year = date_obj.strftime('%Y')
                month_name = date_obj.strftime('%B')  # Get full month name (e.g., February)
                
                # Construct the target directory path including Year/Month Name
                target_subdir = os.path.join(self.target_dir, year, month_name)
                file_name = f"{file_date}.md"
                file_path = os.path.join(target_subdir, file_name)
                
                print(f"Processing Yelp reviews for date: {file_date} -> {file_path}")
                
                # Ensure the target subdirectory exists
                try:
                    os.makedirs(target_subdir, exist_ok=True)
                except OSError as e:
                    print(f"Error creating directory {target_subdir}: {e}")
                    continue
                    
                # Check if the subdirectory is writable
                if not os.access(target_subdir, os.W_OK):
                    print(f"Error: Directory is not writable: {target_subdir}")
                    continue
                
                # Format the reviews as a markdown table
                markdown_table = self.format_reviews_as_markdown_table(reviews)
                
                # Check if the target file exists
                if os.path.exists(file_path):
                    print(f"  File already exists: {file_path}")
                    # Check if file is writable
                    if not os.access(file_path, os.W_OK):
                        print(f"  Error: File is not writable: {file_path}")
                        continue
                        
                    # Check if file already has Yelp reviews section
                    if self.file_already_has_yelp_reviews(file_path):
                        print(f"  File already has Yelp reviews section. Skipping.")
                        continue
                    
                    # Append Yelp reviews to existing file
                    try:
                        with open(file_path, mode="a", encoding="utf-8") as file:
                            file.write("\n## Yelp Reviews\n\n")
                            file.write(markdown_table)
                        print(f"  Appended Yelp reviews to existing file: {file_name}")
                        processed_files += 1
                    except Exception as e:
                        print(f"  Error appending to existing file {file_name}: {e}")
                
                else:
                    # File does not exist, create it and add reviews
                    print(f"  File does not exist, creating: {file_path}")
                    try:
                        with open(file_path, mode="w", encoding="utf-8") as file:
                            # Add the Yelp reviews section
                            file.write("## Yelp Reviews\n\n")
                            file.write(markdown_table)
                        print(f"  Created file and added Yelp reviews: {file_name}")
                        created_files += 1
                    except Exception as e:
                        print(f"  Error creating file {file_name}: {e}")
            
            except ValueError:
                print(f"Skipping invalid date format: {file_date}")
                continue
            except Exception as e:
                print(f"An unexpected error occurred processing date {file_date}: {e}")
                continue
        
        print(f"Finished processing Yelp reviews. Appended to {processed_files} existing file(s), created {created_files} new file(s).")