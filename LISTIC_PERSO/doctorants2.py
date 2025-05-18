import requests
from bs4 import BeautifulSoup
import re
import csv
import json
import os

def scrap_infos_contact(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Vérifie si la réponse est OK
        soup = BeautifulSoup(response.content, "html.parser")
        full_text = soup.get_text(separator="\n", strip=True)
        infos = {}

        # Extraire le nom
        h1_tags = soup.find_all("h1")
        if h1_tags:
            infos["name"] = h1_tags[0].text.strip()
        else:
            infos["name"] = "Non trouvé"
            
        infos["url_listic"] = url
        
        # Courriel académique
        match_univ_mail = re.search(r"\b[\w\.-]+@univ-smb\.fr\b", full_text)
        infos["email"] = match_univ_mail.group() if match_univ_mail else "Non trouvé"

        # email perso
        match_gmail = re.search(r"\b[\w\.-]+@gmail\.com\b", full_text)
        infos["email perso"] = match_gmail.group() if match_gmail else "Non trouvé"

        # LinkedIn
        match_linkedin = re.search(r"https?://www\.linkedin\.com/in/[^\s]+", full_text)
        infos["LinkedIn"] = match_linkedin.group() if match_linkedin else "Non trouvé"

        # phoneance
        match_tel_fr = re.search(r"\+33\s?\d{9}", full_text)
        infos["phone"] = match_tel_fr.group() if match_tel_fr else "Non trouvé"

        # WhatsApp Maroc
        match_wtsp = re.search(r"\+212\s?\(?0?\)?\d{9}", full_text)
        infos["WhatsApp"] = match_wtsp.group() if match_wtsp else "Non trouvé"

        # Bureau
        match_bureau = re.search(r"Bureau\s?:\s?([A-Z]\d+)", full_text)
        infos["office"] = match_bureau.group(1) if match_bureau else "Non trouvé"

        # Adresse
        adresse = "Non trouvée"
        for p in soup.find_all("p"):
            span = p.find("span")
            if span and "Adresse" in span.get_text():
                adresse = p.get_text(strip=True).replace("Adresse", "").replace(":", "").strip()
                break
        infos["address"] = adresse

        # Thème, Sujet, Résumé
        def extract_section(label):
            pattern = re.compile(rf"{label}\s*:\s*(.+?)(?=(\n\S|$))", re.DOTALL)
            match = pattern.search(full_text)
            return match.group(1).strip() if match else "Non trouvé"

        infos["Theme"] = extract_section("Theme")
        infos["Sujet"] = extract_section("Sujet")
        infos["Résumé"] = extract_section("Résumé")

        return infos

    except requests.exceptions.RequestException as e:
        print(f"Erreur HTTP : {e}")
        return None

def save_to_json(doctorants_info, doctorants_externe_info, filename):
    try:
        # S'assurer que le répertoire existe
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Répertoire créé: {directory}")
        
        # Charger le fichier JSON existant ou créer une nouvelle structure
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        # Ajouter ou mettre à jour les sections doctorants et doctorants_externe
        data['doctorants'] = doctorants_info
        data['doctorants_externe'] = doctorants_externe_info

        # Sauvegarder les données dans le fichier JSON
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"✅ Données sauvegardées dans {filename}.")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde des données : {e}")

def main():
    doctorants = [
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/zaid-allal/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/sabrine-bouaziz/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/karima-boutalbi/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/pierre-dardouillet/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/ranya-el-hadri/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/dana-el-hajjar/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/fatema-el-husseini/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/david-esale-yoka/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/youssouph%20FAYE/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/romain-ferrer/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/francesco-floris/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/douba-jafuno/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/utpal-kant/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/andrew-mary-huet-de-barochez/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/paul-mathieu/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/emma-moliere/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/saloua-naama/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/elimy-rebeca-ojeda-mena/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/maria-papadopoulos/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/maverick-perrollaz/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/matteo-salis/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/georgios-sarlas/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/francois-xavier-sikoumo-fogue/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/matthieu-verlynde/",
        "https://www.univ-smb.fr/listic/presentation/membres/post-docs-doctorants/lea-zuccali/",
    ]

    doctorants_info = []

    for url in doctorants:
        print(f"Scraping les informations pour : {url}")
        infos = scrap_infos_contact(url)
        if infos:
            doctorants_info.append(infos)
            print(f"Informations pour {infos.get('name', 'Non trouvé')} enregistrées.")

    doctorants_externe = [
        "https://www.univ-smb.fr/listic/en/presentation_listic/membres/post-docs-doctorants/remi-beisson/",
        "https://www.univ-smb.fr/listic/en/presentation_listic/membres/post-docs-doctorants/abdelaziz-ouazzani-chahdi/"
    ]

    doctorants_externe_info = []
    for url in doctorants_externe:
        print(f"Scraping les informations pour : {url}")
        infos = scrap_infos_contact(url)
        if infos:
            doctorants_externe_info.append(infos)
            print(f"Informations pour {infos.get('name', 'Non trouvé')} enregistrées.")
    
    # Chemin absolu pour le répertoire du script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, "data", "Enseignants.json")
    
    # Sauvegarder les données dans Enseignants.json
    save_to_json(doctorants_info, doctorants_externe_info, json_file_path)

if __name__ == "__main__":
    main()