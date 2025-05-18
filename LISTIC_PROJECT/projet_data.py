
#importation des bibliothèques
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
from pymongo import MongoClient
import hashlib

#get the content of the page
url = "https://www.univ-smb.fr/listic/projets-et-partenaires/liste-projets/"
res = requests.get(url).content
soup = bs(res, 'html.parser')

#table internationale
mytab = soup.find('div' , id="Internationaux").find('table')
# get the header of the table
tabinter_heade = []
tab = mytab.find_all('tr')
for i in tab:
    for y in i.find_all('th'):
        tabinter_heade.append(y.text.strip())
tabinter_heade
#get the content of the table
tabinter_value = []
for i in mytab.find_all('tr')[1:]:
      td_tags = i.find_all('td')
      td_tags = [td.text for td in td_tags]
      tabinter_value.append(td_tags)
# create a dataframe
df_inter = pd.DataFrame(tabinter_value, columns=tabinter_heade)

headers =tabinter_heade
rows = tabinter_value


internationale_data  = []
for row in rows:
    project_dict = dict(zip(headers, row))
    internationale_data.append(project_dict)

#table nationale
mytab = soup.find('div' , id="Nationaux").find('table')
# get the header of the table
tabnat_heade = []
tab = mytab.find_all('tr')
for i in tab:
    for y in i.find_all('th'):
        tabnat_heade.append(y.text.strip())
tabnat_heade
#get the content of the table
tabnat_value = []
for i in mytab.find_all('tr')[1:]:
      td_tags = i.find_all('td')
      td_tags = [td.text for td in td_tags]
      tabnat_value.append(td_tags)
# create a dataframe
df_nat = pd.DataFrame(tabnat_value, columns=tabnat_heade)
#dictionnary
headers =tabnat_heade
rows = tabnat_value


nationale_data  = []
for row in rows:
    project_dict = dict(zip(headers, row))
    nationale_data.append(project_dict)

#table regionale
mytab = soup.find('div', id="Nationaux").find_all('table')
tab = mytab[1].find_all("tbody")
# get the header of the table
tabreg_heade = []
for i in tab:
    for y in i.find_all('th'):
        tabreg_heade.append(y.text.strip())
tabreg_heade
#get the content of the table
tabreg_value = []
for i in tab:
      td_tags = i.find_all('td')
      td_tags = [td.text for td in td_tags]
      tabreg_value.append(td_tags)
# create a dataframe
df_reg = pd.DataFrame(tabreg_value, columns=tabreg_heade)
#dictionnary
headers =tabreg_heade
rows = tabreg_value

regionale_data  = []
for row in rows:
    project_dict = dict(zip(headers, row))
    regionale_data.append(project_dict)

# table incubation
mytab = soup.find('div' ,id="Internationaux").find_all("table")
tab = mytab[3].find_all("tbody")
# get the header of the table
tabinc_heade = []
for i in tab:
    for y in i.find_all('th'):
        tabinc_heade.append(y.text.strip())
tabinc_heade
#get the content of the table
tabinc_value = [td.text.strip() for i in tab for td in i.find_all('td')]
# create a dataframe
rows = [tabinc_value[i:i+len(tabinc_heade)] for i in range(0, len(tabinc_value), len(tabinc_heade))]
df = pd.DataFrame(rows, columns=tabinc_heade)
#dictionnary
data = [dict(zip(tabinc_heade, tabinc_value[i:i+len(tabinc_heade)])) for i in range(0, len(tabinc_value), len(tabinc_heade))]

# Combine all data into a dictionary (même structure que le JSON)
all_tables = {
    "Internationaux": internationale_data,
    "Nationaux": nationale_data,
    "Regionaux": regionale_data,
    "Incubation": data
}

# Save the dictionary to a JSON file
with open("all_tables.json", "w", encoding="utf-8") as json_file:
    json.dump(all_tables, json_file, ensure_ascii=False, indent=4)

# Fonction pour générer un ID unique basé sur le contenu
def generate_unique_id(project_data):
    """Génère un ID unique basé sur le contenu du projet pour éviter les doublons"""
    # Créer une chaîne basée sur le contenu du projet
    content = json.dumps(project_data, sort_keys=True, ensure_ascii=False)
    # Générer un hash MD5 de cette chaîne
    return hashlib.md5(content.encode('utf-8')).hexdigest()

# Fonction pour sauvegarder sans doublons
def save_to_mongodb_no_duplicates(collection, data_list, collection_name):
    """Sauvegarde les données dans MongoDB en évitant les doublons"""
    saved_count = 0
    updated_count = 0
    
    for project in data_list:
        # Générer un ID unique pour ce projet
        unique_id = generate_unique_id(project)
        project['_unique_id'] = unique_id
        
        # Utiliser replace_one avec upsert pour éviter les doublons
        result = collection.replace_one(
            {'_unique_id': unique_id},  # Filtre pour trouver le document
            project,                    # Document à insérer/remplacer
            upsert=True                # Créer si n'existe pas
        )
        
        if result.upserted_id:
            saved_count += 1
        elif result.modified_count > 0:
            updated_count += 1
    
    print(f"Collection '{collection_name}': {saved_count} nouveaux projets ajoutés, {updated_count} mis à jour")

# Connect to MongoDB
try:
    client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
    db = client["listic_projets"]  # Database name
    
    # Sauvegarder les données dans MongoDB avec la même structure que le JSON
    # et éviter les doublons
    save_to_mongodb_no_duplicates(db["Internationaux"], internationale_data, "Internationaux")
    save_to_mongodb_no_duplicates(db["Nationaux"], nationale_data, "Nationaux")
    save_to_mongodb_no_duplicates(db["Regionaux"], regionale_data, "Regionaux")
    save_to_mongodb_no_duplicates(db["Incubation"], data, "Incubation")
    
    # Optionnel: Sauvegarder aussi la structure complète dans une collection séparée
    # Cela permet d'avoir exactement la même structure que le fichier JSON
    complete_data = {
        "_id": "all_projects",  # ID fixe pour cette structure
        "data": all_tables,
        "last_updated": pd.Timestamp.now().isoformat()
    }
    
    db["complete_structure"].replace_one(
        {"_id": "all_projects"},
        complete_data,
        upsert=True
    )
    
    print("✅ Data has been successfully saved to MongoDB without duplicates.")
    print("📊 Collections créées:")
    print("   - Internationaux")
    print("   - Nationaux") 
    print("   - Regionaux")
    print("   - Incubation")
    print("   - complete_structure (structure JSON complète)")
    
except Exception as e:
    print(f"❌ Erreur lors de la connexion à MongoDB: {e}")
    print("Vérifiez que MongoDB est démarré et accessible.")