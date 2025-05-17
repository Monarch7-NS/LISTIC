#!/usr/bin/env python3
"""
DBLP Professor Data Scraper

This script scrapes academic data for professors from the DBLP computer science bibliography database.
It takes a JSON file containing professor names as input and outputs a JSON file with their academic data.
"""

import json
import time
import requests
from bs4 import BeautifulSoup
import re
import logging
from urllib.parse import quote
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DBLPScraper:
    """Class to scrape professor data from DBLP."""
    
    def __init__(self, input_file, output_file, max_workers=5, delay=1):
        """
        Initialize the scraper with input and output file paths.
        
        Args:
            input_file (str): Path to JSON file containing professor names
            output_file (str): Path to save the scraped data
            max_workers (int): Maximum number of concurrent workers for threading
            delay (float): Delay between requests to avoid overloading the server
        """
        self.input_file = input_file
        self.output_file = output_file
        self.max_workers = max_workers
        self.delay = delay
        self.base_url = "https://dblp.org/search/author?q="
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.professors_data = {}
    
    def load_professors(self):
        """Load professor names from the input JSON file."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'teachers' in data:
                    return data['teachers']
                else:
                    logger.error(f"No 'teachers' key found in {self.input_file}")
                    return []
        except Exception as e:
            logger.error(f"Error loading professors from {self.input_file}: {e}")
            return []
    
    def normalize_name(self, name):
        """
        Normalize professor name for better search results.
        
        Args:
            name (str): Original professor name
            
        Returns:
            str: Normalized name for search
        """
        # Convert to lowercase and remove special characters
        normalized = name.lower()
        
        # Handle name formats (Last, First or First Last)
        if ',' in normalized:
            parts = normalized.split(',')
            if len(parts) >= 2:
                normalized = f"{parts[1].strip()} {parts[0].strip()}"
        
        # Remove all-caps formatting
        if name.isupper():
            normalized = name.title()
        
        # Handle "Firstname LASTNAME" format
        parts = name.split()
        if len(parts) >= 2 and parts[-1].isupper():
            last_name = parts[-1].title()
            first_parts = [p for p in parts[:-1]]
            normalized = ' '.join(first_parts) + ' ' + last_name
        
        return normalized.strip()
    
    def search_professor(self, name):
        """
        Search for a professor on DBLP and extract their data.
        
        Args:
            name (str): Professor name to search for
            
        Returns:
            dict: Professor data including publications, affiliations, etc.
        """
        logger.info(f"Searching for professor: {name}")
        
        # Initialize professor data structure
        professor_data = {
            "name": name,
            "normalized_name": self.normalize_name(name),
            "dblp_url": None,
            "publications": [],
            "publication_count": 0,
            "coauthors": [],
            "venues": [],
            "years": [],
            "found": False,
            "search_url": None
        }
        
        try:
            # Use normalized name for search
            normalized_name = professor_data["normalized_name"]
            search_url = f"{self.base_url}{quote(normalized_name)}"
            professor_data["search_url"] = search_url
            
            response = requests.get(search_url, headers=self.headers)
            
            if response.status_code != 200:
                logger.warning(f"Failed to get search results for {name}. Status code: {response.status_code}")
                return professor_data
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if we were redirected directly to an author page
            if "pid" in response.url:
                author_url = response.url
                professor_data["dblp_url"] = author_url
                author_soup = soup  # We're already on the author page
            else:
                # Look for author profiles in search results
                author_entries = soup.select('li.entry.person')
                
                if not author_entries:
                    # Try to find exact matches section
                    exact_matches = soup.find(text=re.compile("Exact matches", re.IGNORECASE))
                    if exact_matches:
                        exact_section = exact_matches.find_parent('div')
                        if exact_section:
                            author_links = exact_section.select('a')
                            if author_links:
                                author_url = author_links[0].get('href')
                                if not author_url.startswith('http'):
                                    author_url = f"https://dblp.org{author_url}"
                                professor_data["dblp_url"] = author_url
                            else:
                                logger.warning(f"No author links found in exact matches for {name}")
                                return professor_data
                        else:
                            logger.warning(f"No exact matches section found for {name}")
                            return professor_data
                    else:
                        logger.warning(f"No author profile found for {name}")
                        return professor_data
                else:
                    # Get the first author profile (most relevant match)
                    author_entry = author_entries[0]
                    author_link = author_entry.select_one('a')
                    
                    if not author_link:
                        logger.warning(f"No author link found for {name}")
                        return professor_data
                    
                    # Get the author profile URL
                    author_url = author_link.get('href')
                    if not author_url.startswith('http'):
                        author_url = f"https://dblp.org{author_url}"
                    
                    professor_data["dblp_url"] = author_url
                    
                    # Get the author profile page
                    time.sleep(self.delay)  # Be nice to the server
                    author_response = requests.get(author_url, headers=self.headers)
                    
                    if author_response.status_code != 200:
                        logger.warning(f"Failed to get author profile for {name}. Status code: {author_response.status_code}")
                        return professor_data
                    
                    author_soup = BeautifulSoup(author_response.text, 'html.parser')
            
            # Extract publications
            publication_entries = author_soup.select('li.entry')
            
            for pub in publication_entries:
                pub_data = {}
                
                # Get publication title
                title_elem = pub.select_one('.title')
                if title_elem:
                    pub_data["title"] = title_elem.text.strip()
                
                # Get publication year
                year_elem = pub.select_one('.year')
                if year_elem:
                    year = year_elem.text.strip()
                    pub_data["year"] = year
                    professor_data["years"].append(year)
                
                # Get publication venue
                venue_elem = pub.select_one('.venue')
                if venue_elem:
                    venue = venue_elem.text.strip()
                    pub_data["venue"] = venue
                    professor_data["venues"].append(venue)
                
                # Get co-authors
                authors_elem = pub.select('.authors a')
                coauthors = []
                for author in authors_elem:
                    author_name = author.text.strip()
                    if author_name.lower() != normalized_name.lower():
                        coauthors.append(author_name)
                        professor_data["coauthors"].append(author_name)
                
                pub_data["coauthors"] = coauthors
                
                # Get publication URL
                pub_link = pub.select_one('a.publ')
                if pub_link:
                    pub_url = pub_link.get('href')
                    if not pub_url.startswith('http'):
                        pub_url = f"https://dblp.org{pub_url}"
                    pub_data["url"] = pub_url
                
                professor_data["publications"].append(pub_data)
            
            # Update publication count
            professor_data["publication_count"] = len(professor_data["publications"])
            
            # Remove duplicates from coauthors and venues
            professor_data["coauthors"] = list(set(professor_data["coauthors"]))
            professor_data["venues"] = list(set(professor_data["venues"]))
            professor_data["years"] = list(set(professor_data["years"]))
            
            # Sort years chronologically
            professor_data["years"] = sorted(professor_data["years"])
            
            # Mark as found if we have publications
            if professor_data["publication_count"] > 0:
                professor_data["found"] = True
                logger.info(f"Successfully scraped data for {name}. Found {professor_data['publication_count']} publications.")
            else:
                logger.warning(f"No publications found for {name}")
            
        except Exception as e:
            logger.error(f"Error scraping data for {name}: {e}")
        
        return professor_data
    
    def scrape_all_professors(self):
        """Scrape data for all professors using multithreading."""
        professors = self.load_professors()
        
        if not professors:
            logger.error("No professors to scrape.")
            return
        
        logger.info(f"Starting to scrape data for {len(professors)} professors.")
        
        # Use ThreadPoolExecutor for concurrent scraping
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit scraping tasks
            future_to_professor = {executor.submit(self.search_professor, name): name for name in professors}
            
            # Process results as they complete
            for future in as_completed(future_to_professor):
                name = future_to_professor[future]
                try:
                    professor_data = future.result()
                    self.professors_data[name] = professor_data
                except Exception as e:
                    logger.error(f"Exception occurred while processing {name}: {e}")
        
        # Save the scraped data
        self.save_data()
        
        # Log summary
        found_count = sum(1 for data in self.professors_data.values() if data.get("found", False))
        logger.info(f"Scraping completed. Found data for {found_count} out of {len(professors)} professors.")
        
        return self.professors_data
    
    def save_data(self):
        """Save the scraped data to the output JSON file."""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump({"professors": self.professors_data}, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {self.output_file}")
        except Exception as e:
            logger.error(f"Error saving data to {self.output_file}: {e}")

def main():
    """Main function to run the scraper."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape professor data from DBLP.')
    parser.add_argument('--input', '-i', type=str, default='./teachers.json',
                        help='Path to JSON file containing professor names')
    parser.add_argument('--output', '-o', type=str, default='./professors_data.json',
                        help='Path to save the scraped data')
    parser.add_argument('--workers', '-w', type=int, default=3,
                        help='Maximum number of concurrent workers')
    parser.add_argument('--delay', '-d', type=float, default=1.0,
                        help='Delay between requests in seconds')
    
    args = parser.parse_args()
    
    scraper = DBLPScraper(args.input, args.output, args.workers, args.delay)
    scraper.scrape_all_professors()


if __name__ == "__main__":
    main()
