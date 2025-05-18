#!/usr/bin/env python3
"""
Script pour importer les données des enseignants du LISTIC depuis Enseignants.json vers MongoDB
Évite les doublons et conserve la structure JSON originale
"""

import json
import os
import hashlib
from datetime import datetime
from pymongo import MongoClient

def generate_unique_id(person_data):
    """
    Génère un ID unique basé sur le contenu d'une personne pour éviter les doublons
    """
    # Exclure certains champs qui peuvent changer (comme les timestamps) de l'ID unique
    data_for_id = {k: v for k, v in person_data.items() if k not in ['last_updated', '_id']}
    content = json.dumps(data_for_id, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def save_category_to_mongodb(collection, data_list, category_name):
    """
    Sauvegarde une catégorie de personnes dans MongoDB en évitant les doublons
    """
    if not data_list:
        print(f"⚠️ Aucune donnée trouvée pour la catégorie '{category_name}'")
        return
    
    saved_count = 0
    updated_count = 0
    skipped_count = 0
    
    for person in data_list:
        # Générer un ID unique pour cette personne
        unique_id = generate_unique_id(person)
        person['_unique_id'] = unique_id
        person['category'] = category_name
        person['last_updated'] = datetime.now().isoformat()
        
        try:
            # Utiliser replace_one avec upsert pour éviter les doublons
            result = collection.replace_one(
                {'_unique_id': unique_id},  # Filtre pour trouver le document
                person,                     # Document à insérer/remplacer
                upsert=True                # Créer si n'existe pas
            )
            
            if result.upserted_id:
                saved_count += 1
            elif result.modified_count > 0:
                updated_count += 1
            else:
                skipped_count += 1
                
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde de {person.get('name', 'Inconnu')}: {e}")
    
    print(f"📊 '{category_name}': {saved_count} nouveaux, {updated_count} mis à jour, {skipped_count} inchangés")

def load_enseignants_data(json_file_path):
    """
    Charge les données depuis le fichier Enseignants.json
    """
    if not os.path.exists(json_file_path):
        print(f"❌ Le fichier {json_file_path} n'existe pas!")
        print("Assurez-vous d'avoir exécuté main_scraper.py d'abord.")
        return None
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f"✅ Données chargées depuis {json_file_path}")
        return data
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de décodage JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors du chargement du fichier: {e}")
        return None

def save_complete_structure(db, all_data):
    """
    Sauvegarde la structure complète du JSON dans une collection séparée
    """
    complete_data = {
        "_id": "all_enseignants",
        "data": all_data,
        "last_updated": datetime.now().isoformat(),
        "total_categories": len(all_data),
        "statistics": {
            category: len(data) if isinstance(data, list) else 1 
            for category, data in all_data.items()
        }
    }
    
    try:
        db["complete_structure"].replace_one(
            {"_id": "all_enseignants"},
            complete_data,
            upsert=True
        )
        print("✅ Structure complète sauvegardée dans 'complete_structure'")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde de la structure complète: {e}")

def main():
    """
    Fonction principale
    """
    print("🚀 Démarrage de l'import MongoDB pour les données LISTIC")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Chemin vers le fichier JSON
    json_file_path = os.path.join("data", "Enseignants.json")
    
    # Charger les données
    all_data = load_enseignants_data(json_file_path)
    if not all_data:
        return
    
    # Connexion à MongoDB
    try:
        # Remplacez par votre chaîne de connexion MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["listic_personnes"]  # Nom de la base de données
        print("✅ Connexion à MongoDB établie")
    except Exception as e:
        print(f"❌ Erreur de connexion à MongoDB: {e}")
        print("Vérifiez que MongoDB est démarré et accessible.")
        return
    
    # Définir les catégories et leurs collections correspondantes
    categories_mapping = {
        "enseignants_chercheurs": "enseignants_chercheurs",
        "émérite": "emerites",
        "doctorants": "doctorants", 
        "doctorants_externe": "doctorants_externes",
        "administratif_et_technique": "administratifs_techniques",
        "collaborateurs_benevoles": "collaborateurs_benevoles",
        "chercheurs_associes": "chercheurs_associes"
    }
    
    print(f"\n{'='*60}")
    print("📋 IMPORT DES DONNÉES PAR CATÉGORIE")
    print(f"{'='*60}")
    
    total_saved = 0
    total_updated = 0
    
    # Traiter chaque catégorie
    for category_key, collection_name in categories_mapping.items():
        if category_key in all_data:
            data_list = all_data[category_key]
            print(f"\n🔄 Traitement de '{category_key}' -> Collection '{collection_name}'")
            
            collection = db[collection_name]
            save_category_to_mongodb(collection, data_list, category_key)
        else:
            print(f"⚠️ Catégorie '{category_key}' non trouvée dans les données")
    
    # Sauvegarder la structure complète
    print(f"\n{'='*60}")
    print("💾 SAUVEGARDE DE LA STRUCTURE COMPLÈTE")
    print(f"{'='*60}")
    save_complete_structure(db, all_data)
    
    # Statistiques finales
    print(f"\n{'='*60}")
    print("📊 STATISTIQUES FINALES")
    print(f"{'='*60}")
    
    # Compter les documents dans chaque collection
    for category_key, collection_name in categories_mapping.items():
        try:
            count = db[collection_name].count_documents({})
            print(f"📋 {collection_name}: {count} documents")
        except:
            print(f"📋 {collection_name}: Erreur lors du comptage")
    
    print(f"\n✅ Import terminé!")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Fermer la connexion
    client.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Interruption par l'utilisateur (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()