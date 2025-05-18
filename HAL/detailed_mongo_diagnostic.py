#!/usr/bin/env python3
"""
Script de diagnostic détaillé pour MongoDB LISTIC
"""

from pymongo import MongoClient
import json

def diagnose_listic_mongodb():
    """Diagnostique détaillé des données LISTIC dans MongoDB"""
    
    try:
        # Se connecter à MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        
        print("=== DIAGNOSTIC MONGODB LISTIC ===\n")
        
        # 1. Lister toutes les bases
        databases = client.list_database_names()
        print("1. Bases de données disponibles:")
        for db_name in databases:
            if db_name not in ['admin', 'config', 'local']:
                print(f"   - {db_name}")
        
        # 2. Examiner chaque base en détail
        print("\n2. Détails par base de données:")
        for db_name in databases:
            if db_name not in ['admin', 'config', 'local']:
                db = client[db_name]
                collections = db.list_collection_names()
                print(f"\n   Base: {db_name}")
                
                if not collections:
                    print("      (aucune collection)")
                    continue
                
                for col_name in collections:
                    try:
                        collection = db[col_name]
                        count = collection.count_documents({})
                        print(f"      - {col_name}: {count} documents")
                        
                        # Montrer un document exemple
                        if count > 0:
                            sample = collection.find_one()
                            if sample:
                                print(f"         Clés disponibles: {list(sample.keys())}")
                                if 'name' in sample:
                                    print(f"         Exemple nom: {sample['name']}")
                                if 'category' in sample:
                                    print(f"         Catégorie: {sample['category']}")
                    except Exception as e:
                        print(f"      - {col_name}: Erreur - {e}")
        
        # 3. Test spécifique pour listic_personnes
        print("\n3. Test pour 'listic_personnes':")
        for db_name in ['listic_data', 'project_data', 'listic_offres_data']:
            if db_name in databases:
                db = client[db_name]
                if 'listic_personnes' in db.list_collection_names():
                    collection = db['listic_personnes']
                    count = collection.count_documents({})
                    print(f"   TROUVÉ: {db_name}.listic_personnes ({count} documents)")
                    
                    if count > 0:
                        # Montrer quelques exemples
                        samples = list(collection.find({}, {"name": 1, "category": 1}).limit(3))
                        for sample in samples:
                            name = sample.get('name', 'N/A')
                            category = sample.get('category', 'N/A')
                            print(f"      - {name} (catégorie: {category})")
                    break
        else:
            print("   Collection 'listic_personnes' NON TROUVÉE")
        
        # 4. Chercher des collections avec des noms
        print("\n4. Collections contenant des noms de personnes:")
        for db_name in databases:
            if db_name not in ['admin', 'config', 'local']:
                db = client[db_name]
                for col_name in db.list_collection_names():
                    collection = db[col_name]
                    try:
                        # Chercher un document avec un champ 'name'
                        sample_with_name = collection.find_one({"name": {"$exists": True}})
                        if sample_with_name:
                            count = collection.count_documents({"name": {"$exists": True}})
                            print(f"   {db_name}.{col_name}: {count} docs avec 'name'")
                            
                            # Montrer quelques noms
                            names = list(collection.find({"name": {"$exists": True}}, {"name": 1}).limit(3))
                            for doc in names:
                                print(f"      - {doc.get('name')}")
                    except:
                        continue
        
        print("\n=== FIN DU DIAGNOSTIC ===")
        client.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    diagnose_listic_mongodb()