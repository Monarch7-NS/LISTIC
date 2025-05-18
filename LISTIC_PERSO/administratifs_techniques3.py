import requests
from bs4 import BeautifulSoup
import json
import re
import os
from lxml import html  # Import lxml for XPath

# Function to extract email using XPath
def extract_email_from_xpath(url):
    try:
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
    except Exception as e:
        print(f"Erreur lors de l'extraction de l'email depuis {url}: {e}")
        return None

# Function to extract profile information from a given URL
def extract_profile(url):
    try:
        if not url:
            return None
            
        print(f"Extraction des informations depuis: {url}")
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
            "url_listic": url
        }
    except Exception as e:
        print(f"Erreur lors de l'extraction du profil depuis {url}: {e}")
        return {
            "name": None,
            "title": None,
            "email": None,
            "phone": None,
            "fax": None,
            "office": None,
            "address": None,
            "url_listic": url
        }

# Fonction pour corriger les cas spéciaux
def fix_special_cases(profiles):
    for profile in profiles:
        # Correction pour Alseny DIALLO si l'email est manquant
        if profile["name"] == "Alseny DIALLO" and profile["email"] is None:
            profile["email"] = "alseny.diallo@univ-smb.fr"
    return profiles

# Fonction principale
def main():
    # URL de la page principale listant tous les personnels administratifs et techniques
    main_url = "https://www.univ-smb.fr/listic/presentation/membres/administratifs-techniques/"
    
    try:
        # Récupérer la liste de tous les membres
        response = requests.get(main_url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extraire les informations de base de la table
        table = soup.find("table")
        rows = table.find_all("tr")[1:]  # Ignorer l'en-tête
        
        all_profiles = []
        
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                name = cols[0].get_text(strip=True)
                title = cols[1].get_text(strip=True)
                
                # Récupérer l'URL du profil si disponible
                url_element = cols[0].find("a")
                profile_url = None
                
                if url_element:
                    profile_url = "https://www.univ-smb.fr" + url_element["href"]
                    # Extraire les informations détaillées du profil
                    profile_info = extract_profile(profile_url)
                    if profile_info:
                        all_profiles.append(profile_info)
                else:
                    # Pour les personnes sans URL de profil (comme Florent BALDINI)
                    all_profiles.append({
                        "name": name,
                        "title": title,
                        "email": None,
                        "phone": None,
                        "fax": None,
                        "office": None,
                        "address": None,
                        "url_listic": None
                    })
        
        # Appliquer les corrections pour les cas spéciaux
        all_profiles = fix_special_cases(all_profiles)
        
        # Déterminer le chemin du fichier "data/Enseignants.json"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, "data")
        json_file_path = os.path.join(data_dir, "Enseignants.json")
        
        # Créer le répertoire "data" s'il n'existe pas
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"✅ Répertoire créé: {data_dir}")
        
        # Charger les données existantes s'il y en a, sinon créer une structure vide
        existing_data = {}
        if os.path.exists(json_file_path):
            try:
                with open(json_file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                print(f"✅ Données existantes chargées depuis {json_file_path}")
            except json.JSONDecodeError:
                print(f"⚠️ Le fichier {json_file_path} existe mais n'est pas un JSON valide. Création d'un nouveau fichier.")
            except Exception as e:
                print(f"⚠️ Erreur lors de la lecture du fichier existant: {e}")
        
        # Ajouter la nouvelle section "administratif_et_technique" aux données existantes
        existing_data["administratif_et_technique"] = all_profiles
        
        # Sauvegarder toutes les données dans le fichier JSON
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Données extraites et sauvegardées dans {json_file_path}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du script: {e}")

# Exécuter la fonction principale
if __name__ == "__main__":
    main()