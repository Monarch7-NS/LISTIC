# DBLP Professor Data Scraper

A Python tool to scrape academic data for professors from the DBLP computer science bibliography database.

## Overview

This tool takes a JSON file containing professor names as input and outputs a JSON file with their academic data from DBLP, including publications, co-authors, venues, and years.

## Features

- Searches for professors on DBLP using their names
- Extracts publication data, co-authors, venues, and years
- Handles name variations and potential ambiguities
- Provides comprehensive error handling and logging
- Uses multithreading for faster processing
- Outputs structured JSON data

## Requirements

- Python 3.6+
- Required packages:
  - requests
  - beautifulsoup4
  - concurrent.futures (standard library)

## Installation

1. Clone or download this repository
2. Install required packages:
   ```
   pip install requests beautifulsoup4
   ```

## Usage

### Basic Usage

```
python scrape_professors_fixed.py
```

This will use the default input file (`./teachers.json`) and output file (`./professors_data.json`).

### Advanced Usage

```
python scrape_professors_fixed.py --input path/to/input.json --output path/to/output.json --workers 3 --delay 1.5
```

### Command-line Arguments

- `--input`, `-i`: Path to JSON file containing professor names (default: `./teachers.json`)
- `--output`, `-o`: Path to save the scraped data (default: `./professors_data.json`)
- `--workers`, `-w`: Maximum number of concurrent workers (default: 3)
- `--delay`, `-d`: Delay between requests in seconds (default: 1.0)

## Input Format

The input JSON file should have the following structure:

```json
{
    "teachers": [
        "Professor Name 1",
        "Professor Name 2",
        "Professor Name 3",
        ...
    ]
}
```

## Output Format

The output JSON file will have the following structure:

```json
{
    "professors": {
        "Professor Name 1": {
            "name": "Professor Name 1",
            "normalized_name": "professor name 1",
            "dblp_url": "https://dblp.org/pid/...",
            "publications": [
                {
                    "title": "Publication Title",
                    "year": "2023",
                    "venue": "Conference/Journal Name",
                    "coauthors": ["Coauthor 1", "Coauthor 2"],
                    "url": "https://dblp.org/rec/..."
                },
                ...
            ],
            "publication_count": 10,
            "coauthors": ["Coauthor 1", "Coauthor 2", ...],
            "venues": ["Venue 1", "Venue 2", ...],
            "years": ["2020", "2021", "2022", "2023"],
            "found": true,
            "search_url": "https://dblp.org/search/author?q=..."
        },
        ...
    }
}
```

## Troubleshooting

- If you encounter timeouts, try increasing the `--delay` parameter
- If you're getting too many timeouts, try reducing the `--workers` parameter
- Check the log file (`scraper.log`) for detailed error messages


