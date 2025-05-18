
import requests
from bs4 import BeautifulSoup as bs
import re
def make_soup(url):
    html = requests.get(url).content
    soup = bs(html,"html.parser")
    return soup

soup = make_soup("https://www.univ-smb.fr/listic/en/presentation_listic/membres/collaborateurs-benevoles/")
tbody = soup.find('tbody')

# Transformation en dictionnaire
data = []
if tbody:
    rows = tbody.find_all('tr')  # Trouver toutes les lignes du tableau
    for row in rows:
        cells = row.find_all('td')  # Trouver toutes les cellules de la ligne
        if cells:
            name_cell = cells[0]
            name = name_cell.get_text(strip=True)  # Nom
            if name_cell.find('a') != None :
                link = name_cell.find('a')['href']
            else:
                link = ""

            # Poste

            monodata = {}
            monodata["name"] = name
            if link != "":
                monodata["url_listic"] = "https://www.univ-smb.fr" + link

            # Ajouter les données au dictionnaire
            data.append(monodata)


# Affichage du dictionnaire
print(data)

soup = make_soup(data[0]["url_listic"])
data[0]["email"]=soup.find("div", id="c2147").getText(strip=True).split(":")[1]

data[0]["Theme"]=soup.find("div", id="c2145").find("div", class_="indent").find("h3").find_next_sibling("p").get_text(strip=True)
data[0]

soup = make_soup(data[1]["url_listic"]).find("div", id="c2147").find_all("p")
soup = [x.get_text(strip=True).split(":")[1] for x in soup]
data[1]["email"]=soup[0]
data[1]["phone"]=soup[1]
data[1]["adresse"]=soup[2]
data[1]

import json
import os

# Charger le fichier Enseignants.json existant
json_path = os.path.join("data", "Enseignants.json")
with open(json_path, "r", encoding="utf-8") as f:
    enseignants_data = json.load(f)

# Ajouter ou remplacer la clé "collaborateurs_benevoles" avec la liste data
enseignants_data["collaborateurs_benevoles"] = data

# Sauvegarder le fichier JSON mis à jour
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(enseignants_data, f, ensure_ascii=False, indent=4)

print("Ajout de collaborateurs_benevoles terminé.")

soup = make_soup("https://www.univ-smb.fr/listic/presentation/membres/chercheurs-associes/")
tbody = soup.find('tbody')

# Transformation en dictionnaire
data = []
if tbody:
    rows = tbody.find_all('tr')  # Trouver toutes les lignes du tableau
    for row in rows:
        cells = row.find_all('td')  # Trouver toutes les cellules de la ligne
        if cells:
            name_cell = cells[0]
            name = name_cell.get_text(strip=True)  # Nom
            if name_cell.find('a') != None :
                link = name_cell.find('a')['href']
            else:
                link = ""

            # Poste

            monodata = {}
            monodata["name"] = name
            if link != "":
                monodata["url_listic"] = "https://www.univ-smb.fr" + link

            # Ajouter les données au dictionnaire
            data.append(monodata)


# Affichage du dictionnaire
print(data)

soup = make_soup(data[5]["url_listic"])
lis = [x.get_text(strip=True).split(":")[1] for x in soup.find("div", id="c2147").find_all("p")]
data[5]["email"]=lis[0]
data[5]["phone"]=lis[1]
data[5]["adresse"]=lis[2]
data[5]["website"]= soup.find("div", id="c2146").find("p").get_text(strip=True).split(":")[1]+":"+soup.find("div", id="c2146").find("p").get_text(strip=True).split(":")[2]
data[5]["Theme"]=soup.find("div", id="c2146").find_all("p")[1].get_text(strip=True).split(":")[1]
data[5]

import json
import os

# Charger le fichier Enseignants.json existant
json_path = os.path.join("data", "Enseignants.json")
with open(json_path, "r", encoding="utf-8") as f:
    enseignants_data = json.load(f)

# Ajouter ou remplacer la clé "collaborateurs_benevoles" avec la liste data
enseignants_data["chercheurs_associes"] = data

# Sauvegarder le fichier JSON mis à jour
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(enseignants_data, f, ensure_ascii=False, indent=4)

print("Ajout de collaborateurs_benevoles terminé.")