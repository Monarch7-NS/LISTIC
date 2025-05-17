import requests
from bs4 import BeautifulSoup
import csv
import os

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from lxml import html  # Import lxml for XPath


url = "https://www.univ-smb.fr/listic/presentation/membres/administratifs-techniques/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Extract the relevant table
table = soup.find("table")
rows = table.find_all("tr")[1:]  # skip header

data = []

for row in rows:
    cols = row.find_all("td")
    if len(cols) >= 2:
        name = cols[0].get_text(strip=True)
        title = cols[1].get_text(strip=True)
        data.append({
            "name": name,
            "title": title
        })

# Determine the path to save the CSV file in the same directory as this script
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(current_dir, "administratifs_et_techniques.csv")

# Save to CSV
with open(csv_file_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "title"])
    writer.writeheader()
    writer.writerows(data)

print(f"✅ CSV file created at: {csv_file_path}")


# Function to extract email using XPath
def extract_email_from_xpath(url):
    response = requests.get(url)
    tree = html.fromstring(response.content)  # Parse the HTML content with lxml

    # Use XPath to find the email
    email_xpath = "/html/body/div[2]/div/div/div/main/article/div/div[2]/p[1]"
    email = tree.xpath(f"{email_xpath}/text()")  # Extract the text from the specified path

    # Clean the email format if it's broken
    if email:
        email_text = email[0].strip()
        # Replace the broken email format (–@–) with a proper "@" symbol
        email_text = email_text.replace(" –@– ", "@")
        return email_text
    return None

# Function to extract profile information from a given URL
def extract_profile(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    name_tag = soup.find("h1", class_="entry-title")
    name = name_tag.get_text(strip=True) if name_tag else None

    # Extract email using XPath function
    email = extract_email_from_xpath(url)

    # Get all the text content from the page
    full_text = soup.get_text(separator="\n")

    # Use regular expressions to extract additional information
    phone_match = re.search(r'Téléphone\s*:\s*(\+33\(0\)\s*\d[\d\s]*)', full_text)
    fax_match = re.search(r'télécopie\s*:\s*(\+33\(0\)\s*\d[\d\s]*)', full_text)
    office_match = re.search(r'Bureau\s*:\s*(A\d+)', full_text)
    address_match = re.search(r'Adresse\s*:\s*(LISTIC[^\n]+)', full_text)
    title_match = re.search(r'(.+)\nContact', full_text)

    # Extract and clean the phone number
    phone = phone_match.group(1).strip().replace(" ", "") if phone_match else None
    # Extract and clean the fax number
    fax = fax_match.group(1).strip().replace(" ", "") if fax_match else None
    # Extract the office number
    office = office_match.group(1).strip() if office_match else None
    # Extract the address
    address = address_match.group(1).strip() if address_match else None
    # Extract the title or use a default value if not found
    title = title_match.group(1).strip() if title_match else "Personnel administratif"

    # Return all extracted data as a structured dictionary
    return {
        "name": name,
        "title": title,
        "email": email,
        "phone": phone,
        "fax": fax,
        "office": office,
        "address": address,
        "profile_url": url
    }

# Function to scrape Florent BALDINI's information from the table
def scrape_florent_baldini(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table containing personnel information
    table = soup.find("table")
    rows = table.find_all("tr")[1:]  # Skip the header row

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            name = cols[0].get_text(strip=True)
            title = cols[1].get_text(strip=True)
            # Check if the row corresponds to Florent BALDINI
            if name == "Florent BALDINI":
                return {
                    "name": name,
                    "title": title,
                    "email": None,  # Email is not available
                    "phone": None,  # Phone number is not available
                    "fax": None,  # Fax number is not available
                    "office": None,  # Office number is not available
                    "address": None,  # Address is not available
                    "profile_url": None  # Profile URL is not available
                }
    return None  # Return None if Florent BALDINI is not found

# Function to manually add the email for Alseny DIALLO if it's missing
def add_diallo_email(profiles):
    for profile in profiles:
        # Check if the profile belongs to Alseny DIALLO and if the email is missing
        if profile["name"] == "Alseny DIALLO" and profile["email"] is None:
            # Add the correct email for Alseny DIALLO
            profile["email"] = "alseny.diallo@univ-smb.fr"
    return profiles

# List of URLs to scrape
urls = [
    "https://www.univ-smb.fr/listic/presentation/membres/administratifs-techniques/alseny/",
    "https://www.univ-smb.fr/listic/presentation/membres/administratifs-techniques/magali-lina-viandaz/"
]

# Extract profiles from the given URLs
profiles = [extract_profile(url) for url in urls]

# Manually add Alseny DIALLO's email if it's missing
profiles = add_diallo_email(profiles)

# Scrape Florent BALDINI's information and add it to the profiles
florent_baldini_info = scrape_florent_baldini("https://www.univ-smb.fr/listic/presentation/membres/administratifs-techniques/")
if florent_baldini_info:
    profiles.append(florent_baldini_info)

# Determine the path to save the JSON file in the same directory as the script
current_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(current_dir, "administratifs_et_techniques.json")

# Save the extracted profiles to a JSON file
with open(json_file_path, "w", encoding="utf-8") as f:
    json.dump(profiles, f, indent=4, ensure_ascii=False)

# Print a success message with the file path
print(f"✅ Données extraites et sauvegardées dans {json_file_path}")
