#!/usr/bin/env python3
"""
DBLP MongoDB Integration Script

Ce script enrichit les données de tous les enseignants stockées dans MongoDB 
avec leurs informations académiques depuis DBLP.
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
from pymongo import MongoClient
from datetime import datetime

# Configuration du logging sans emojis pour éviter les erreurs d'encodage
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dblp_enrichment.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DBLPMongoEnricher:
    """Classe pour enrichir les données de tous les enseignants avec DBLP depuis MongoDB."""
    
    def __init__(self, max_workers=3, delay=1.5):
        """
        Initialise l'enrichisseur DBLP.
        
        Args:
            max_workers (int): Nombre maximum de workers pour le multithreading
            delay (float): Délai entre les requêtes pour éviter la surcharge du serveur
        """
        self.max_workers = max_workers
        self.delay = delay
        self.base_url = "https://dblp.org/search/author?q="
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.db = None
        self.collection = None
        
    def connect_to_mongodb(self, connection_string="mongodb://localhost:27017/", db_name="listic_data"):
        """
        Se connecte à MongoDB et initialise la collection.
        
        Args:
            connection_string (str): Chaîne de connexion MongoDB
            db_name (str): Nom de la base de données
        """
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[db_name]
            
            # Vérifier quelles collections existent
            collections = self.db.list_collection_names()
            logger.info(f"Collections disponibles dans {db_name}: {collections}")
            
            # Essayer les différentes collections des scripts LISTIC
            possible_collections = [
                "listic_personnes",           # Collection que vous avez mentionnée
                "enseignants_chercheurs",     # De import_enseignants_mongodb.py
                "emerites",                   # De import_enseignants_mongodb.py
                "doctorants",                 # De import_enseignants_mongodb.py
                "doctorants_externes",        # De import_enseignants_mongodb.py
                "administratifs_techniques",   # De import_enseignants_mongodb.py
                "collaborateurs_benevoles",   # De import_enseignants_mongodb.py
                "chercheurs_associes"         # De import_enseignants_mongodb.py
            ]
            
            found_collections = []
            total_documents = 0
            
            for col_name in possible_collections:
                if col_name in collections:
                    found_collections.append(col_name)
                    count = self.db[col_name].count_documents({})
                    total_documents += count
                    logger.info(f"Collection {col_name}: {count} documents")
            
            if not found_collections:
                logger.error("Aucune collection de personnel trouvée!")
                logger.info("Collections disponibles: " + str(collections))
                return False
            
            # Priorité à listic_personnes si elle existe, sinon prendre la première trouvée
            if "listic_personnes" in collections:
                self.collection = self.db["listic_personnes"]
                collection_name = "listic_personnes"
            else:
                collection_name = found_collections[0]
                self.collection = self.db[collection_name]
            
            # Vérifier le contenu
            actual_count = self.collection.count_documents({})
            logger.info(f"Connexion MongoDB établie - Base: {db_name}, Collection: {collection_name}, Documents: {actual_count}")
            
            if actual_count == 0:
                logger.warning(f"La collection {collection_name} est vide!")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion à MongoDB: {e}")
            return False
    
    def get_all_teachers_from_mongodb(self):
        """
        Récupère tous les enseignants depuis toutes les collections valides.
        
        Returns:
            list: Liste des documents de tous les enseignants
        """
        try:
            all_teachers = []
            categories_stats = {}
            
            for collection_name in self.valid_collections:
                collection = self.db[collection_name]
                teachers = list(collection.find({}))
                all_teachers.extend(teachers)
                categories_stats[collection_name] = len(teachers)
                logger.info(f"Collection {collection_name}: {len(teachers)} enseignants récupérés")
            
            logger.info(f"Total: {len(all_teachers)} enseignants trouvés dans MongoDB")
            logger.info("Répartition par collection:")
            for collection_name, count in categories_stats.items():
                logger.info(f"   - {collection_name}: {count}")
            
            return all_teachers
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des enseignants: {e}")
            return []
    
    def get_all_teachers_from_multiple_collections(self):
        """
        Alternative: récupère depuis plusieurs collections si listic_personnes n'existe pas.
        """
        all_teachers = []
        collections_to_check = [
            "enseignants_chercheurs", 
            "doctorants",
            "doctorants_externes",
            "administratifs_techniques",
            "collaborateurs_benevoles", 
            "chercheurs_associes",
            "emerites"
        ]
        
        for col_name in collections_to_check:
            try:
                if col_name in self.db.list_collection_names():
                    collection = self.db[col_name]
                    teachers = list(collection.find({}))
                    
                    # Ajouter la catégorie si elle n'existe pas
                    for teacher in teachers:
                        if 'category' not in teacher:
                            teacher['category'] = col_name
                    
                    all_teachers.extend(teachers)
                    logger.info(f"Collection {col_name}: {len(teachers)} documents")
            except Exception as e:
                logger.error(f"Erreur pour la collection {col_name}: {e}")
        
        logger.info(f"Total: {len(all_teachers)} enseignants trouvés depuis multiples collections")
        return all_teachers
    
    def normalize_name(self, name):
        """
        Normalise le nom de l'enseignant pour une meilleure recherche.
        
        Args:
            name (str): Nom original de l'enseignant
            
        Returns:
            str: Nom normalisé pour la recherche
        """
        if not name:
            return ""
        
        # Convertir en minuscules et nettoyer
        normalized = name.lower().strip()
        
        # Gérer le format "Nom, Prénom" 
        if ',' in normalized:
            parts = normalized.split(',')
            if len(parts) >= 2:
                normalized = f"{parts[1].strip()} {parts[0].strip()}"
        
        # Gérer le format "Prénom NOM" (tout en majuscules)
        if name.isupper():
            normalized = name.title()
        
        # Gérer le format "Prénom NOM" avec NOM en majuscules
        parts = name.split()
        if len(parts) >= 2 and parts[-1].isupper():
            last_name = parts[-1].title()
            first_parts = [p for p in parts[:-1]]
            normalized = ' '.join(first_parts) + ' ' + last_name
        
        # Nettoyer les caractères spéciaux courants
        replacements = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'á': 'a', 'â': 'a', 'ä': 'a',
            'ç': 'c', 'ô': 'o', 'ù': 'u', 'û': 'u',
            'î': 'i', 'ï': 'i', 'ñ': 'n'
        }
        
        for accent, replacement in replacements.items():
            normalized = normalized.replace(accent, replacement)
        
        return normalized.strip()
    
    def search_teacher_on_dblp(self, teacher_doc):
        """
        Recherche un enseignant sur DBLP et extrait ses données.
        
        Args:
            teacher_doc (dict): Document MongoDB de l'enseignant
            
        Returns:
            dict: Données DBLP (None si non trouvées ou vides)
        """
        name = teacher_doc.get('name', '')
        category = teacher_doc.get('category', 'unknown')
        logger.info(f"Recherche DBLP pour: {name} ({category})")
        
        # Vérifier si les données DBLP existent déjà
        if teacher_doc.get('dblp_data'):
            logger.info(f"Données DBLP déjà présentes pour {name}, ignoré")
            return None
        
        try:
            # Normaliser le nom pour la recherche
            normalized_name = self.normalize_name(name)
            if not normalized_name:
                logger.warning(f"Impossible de normaliser le nom: {name}")
                return None
            
            # Effectuer la recherche
            search_url = f"{self.base_url}{quote(normalized_name)}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Échec de la recherche pour {name}. Status: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Vérifier si on a été redirigé directement vers une page d'auteur
            if "pid" in response.url:
                author_url = response.url
                author_soup = soup
            else:
                # Chercher dans les résultats de recherche
                author_entries = soup.select('li.entry.person')
                
                if not author_entries:
                    # Essayer de trouver la section des correspondances exactes
                    exact_matches = soup.find(text=re.compile("Exact matches", re.IGNORECASE))
                    if exact_matches:
                        exact_section = exact_matches.find_parent('div')
                        if exact_section:
                            author_links = exact_section.select('a')
                            if author_links:
                                author_url = author_links[0].get('href')
                                if not author_url.startswith('http'):
                                    author_url = f"https://dblp.org{author_url}"
                            else:
                                logger.warning(f"Aucun lien d'auteur trouvé pour {name}")
                                return None
                        else:
                            logger.warning(f"Section des correspondances exactes introuvable pour {name}")
                            return None
                    else:
                        logger.warning(f"Aucun profil d'auteur trouvé pour {name}")
                        return None
                else:
                    # Prendre le premier profil d'auteur (correspondance la plus pertinente)
                    author_entry = author_entries[0]
                    author_link = author_entry.select_one('a')
                    
                    if not author_link:
                        logger.warning(f"Aucun lien d'auteur pour {name}")
                        return None
                    
                    author_url = author_link.get('href')
                    if not author_url.startswith('http'):
                        author_url = f"https://dblp.org{author_url}"
                    
                    # Récupérer la page du profil de l'auteur
                    time.sleep(self.delay)
                    author_response = requests.get(author_url, headers=self.headers, timeout=10)
                    
                    if author_response.status_code != 200:
                        logger.warning(f"Échec du profil d'auteur pour {name}. Status: {author_response.status_code}")
                        return None
                    
                    author_soup = BeautifulSoup(author_response.text, 'html.parser')
            
            # Extraire les données DBLP
            dblp_data = {
                "dblp_url": author_url,
                "publications": [],
                "coauthors": [],
                "venues": [],
                "years": [],
                "last_updated": datetime.now().isoformat()
            }
            
            # Extraire les publications
            publication_entries = author_soup.select('li.entry')
            
            for pub in publication_entries:
                pub_data = {}
                
                # Titre de la publication
                title_elem = pub.select_one('.title')
                if title_elem:
                    pub_data["title"] = title_elem.text.strip()
                
                # Année de publication
                year_elem = pub.select_one('.year')
                if year_elem:
                    year = year_elem.text.strip()
                    pub_data["year"] = year
                    dblp_data["years"].append(year)
                
                # Venue de publication
                venue_elem = pub.select_one('.venue')
                if venue_elem:
                    venue = venue_elem.text.strip()
                    pub_data["venue"] = venue
                    dblp_data["venues"].append(venue)
                
                # Co-auteurs
                authors_elem = pub.select('.authors a')
                coauthors = []
                for author in authors_elem:
                    author_name = author.text.strip()
                    if author_name.lower() != normalized_name.lower():
                        coauthors.append(author_name)
                        dblp_data["coauthors"].append(author_name)
                
                pub_data["coauthors"] = coauthors
                
                # URL de la publication
                pub_link = pub.select_one('a.publ')
                if pub_link:
                    pub_url = pub_link.get('href')
                    if not pub_url.startswith('http'):
                        pub_url = f"https://dblp.org{pub_url}"
                    pub_data["url"] = pub_url
                
                # Ajouter la publication si elle a au moins un titre
                if pub_data.get("title"):
                    dblp_data["publications"].append(pub_data)
            
            # Nettoyer et dédupliquer
            dblp_data["coauthors"] = list(set(dblp_data["coauthors"]))
            dblp_data["venues"] = list(set(dblp_data["venues"]))
            dblp_data["years"] = sorted(list(set(dblp_data["years"])))
            dblp_data["publication_count"] = len(dblp_data["publications"])
            
            # Vérifier si on a trouvé des données utiles
            if dblp_data["publication_count"] > 0:
                logger.info(f"DBLP: {name} ({category}) - {dblp_data['publication_count']} publications trouvées")
                return dblp_data
            else:
                logger.warning(f"DBLP: Aucune publication trouvée pour {name} ({category})")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de la recherche DBLP pour {name}: {e}")
            return None
    
    def update_teacher_with_dblp_data(self, teacher_doc, dblp_data):
        """
        Met à jour le document de l'enseignant avec les données DBLP.
        
        Args:
            teacher_doc (dict): Document MongoDB de l'enseignant
            dblp_data (dict): Données DBLP à ajouter
        """
        try:
            # Déterminer dans quelle collection se trouve ce document
            teacher_category = teacher_doc.get('category', '')
            collection_name = None
            
            # Mapper la catégorie vers le nom de collection
            if teacher_category == 'enseignants_chercheurs':
                collection_name = 'enseignants_chercheurs'
            elif teacher_category == 'émérite':
                collection_name = 'emerites'
            elif teacher_category == 'doctorants':
                collection_name = 'doctorants'
            elif teacher_category == 'doctorants_externe':
                collection_name = 'doctorants_externes'
            elif teacher_category == 'administratif_et_technique':
                collection_name = 'administratifs_techniques'
            elif teacher_category == 'collaborateurs_benevoles':
                collection_name = 'collaborateurs_benevoles'
            elif teacher_category == 'chercheurs_associes':
                collection_name = 'chercheurs_associes'
            
            if not collection_name:
                logger.error(f"Impossible de déterminer la collection pour {teacher_doc.get('name')} (catégorie: {teacher_category})")
                return
            
            # Mettre à jour dans la bonne collection
            collection = self.db[collection_name]
            update_data = {
                "dblp_data": dblp_data,
                "last_dblp_update": datetime.now().isoformat()
            }
            
            result = collection.update_one(
                {"_id": teacher_doc["_id"]},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"MongoDB: Données DBLP mises à jour pour {teacher_doc.get('name')} dans {collection_name}")
            else:
                logger.warning(f"MongoDB: Aucune modification pour {teacher_doc.get('name')}")
                
        except Exception as e:
            logger.error(f"Erreur MongoDB pour {teacher_doc.get('name')}: {e}")
    
    def process_teacher(self, teacher_doc):
        """
        Traite un enseignant : recherche DBLP + mise à jour MongoDB.
        
        Args:
            teacher_doc (dict): Document MongoDB de l'enseignant
        """
        # Rechercher sur DBLP
        dblp_data = self.search_teacher_on_dblp(teacher_doc)
        
        if dblp_data:
            # Mettre à jour MongoDB avec les nouvelles données
            self.update_teacher_with_dblp_data(teacher_doc, dblp_data)
        
        # Respecter le délai même si aucune donnée trouvée
        time.sleep(self.delay)
    
    def enrich_all_teachers(self):
        """
        Enrichit tous les enseignants (toutes catégories) avec les données DBLP.
        """
        # Essayer d'abord la collection principale
        all_teachers = self.get_all_teachers_from_mongodb()
        
        # Si aucun résultat, essayer les collections multiples
        if not all_teachers:
            logger.info("Tentative de récupération depuis plusieurs collections...")
            all_teachers = self.get_all_teachers_from_multiple_collections()
        
        if not all_teachers:
            logger.error("Aucun enseignant à enrichir")
            return
        
        logger.info(f"Début de l'enrichissement pour {len(all_teachers)} enseignants (toutes catégories)")
        
        # Statistiques
        processed_count = 0
        enriched_count = 0
        error_count = 0
        skipped_count = 0
        
        # Compteurs par catégorie
        stats_by_category = {}
        
        # Utiliser ThreadPoolExecutor pour le traitement concurrent
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Soumettre les tâches
            future_to_teacher = {
                executor.submit(self.process_teacher, teacher): teacher 
                for teacher in all_teachers
            }
            
            # Traiter les résultats à mesure qu'ils arrivent
            for future in as_completed(future_to_teacher):
                teacher = future_to_teacher[future]
                processed_count += 1
                category = teacher.get('category', 'unknown')
                
                # Initialiser les stats pour cette catégorie si nécessaire
                if category not in stats_by_category:
                    stats_by_category[category] = {
                        'total': 0, 'enriched': 0, 'skipped': 0, 'errors': 0
                    }
                
                stats_by_category[category]['total'] += 1
                
                try:
                    future.result()
                    # Vérifier si les données ont été enrichies
                    # Il faut chercher dans la bonne collection
                    teacher_category = teacher.get('category', '')
                    collection_name = None
                    
                    # Mapper la catégorie vers le nom de collection
                    if teacher_category == 'enseignants_chercheurs':
                        collection_name = 'enseignants_chercheurs'
                    elif teacher_category == 'émérite':
                        collection_name = 'emerites'
                    elif teacher_category == 'doctorants':
                        collection_name = 'doctorants'
                    elif teacher_category == 'doctorants_externe':
                        collection_name = 'doctorants_externes'
                    elif teacher_category == 'administratif_et_technique':
                        collection_name = 'administratifs_techniques'
                    elif teacher_category == 'collaborateurs_benevoles':
                        collection_name = 'collaborateurs_benevoles'
                    elif teacher_category == 'chercheurs_associes':
                        collection_name = 'chercheurs_associes'
                    
                    if collection_name:
                        collection = self.db[collection_name]
                        updated_teacher = collection.find_one({"_id": teacher["_id"]})
                        
                        if updated_teacher and updated_teacher.get("dblp_data"):
                            enriched_count += 1
                            stats_by_category[category]['enriched'] += 1
                        elif updated_teacher and "dblp_data" in updated_teacher:
                            skipped_count += 1
                            stats_by_category[category]['skipped'] += 1
                    
                except Exception as e:
                    error_count += 1
                    stats_by_category[category]['errors'] += 1
                    logger.error(f"Erreur lors du traitement de {teacher.get('name')}: {e}")
                
                # Afficher le progrès périodiquement
                if processed_count % 10 == 0:
                    logger.info(f"Progrès: {processed_count}/{len(all_teachers)} traités ({(processed_count/len(all_teachers)*100):.1f}%)")
        
        # Rapport final détaillé
        logger.info(f"\n{'='*70}")
        logger.info("RAPPORT FINAL D'ENRICHISSEMENT DBLP - TOUS LES ENSEIGNANTS")
        logger.info(f"{'='*70}")
        logger.info(f"Total traités: {processed_count}")
        logger.info(f"Enrichis avec succès: {enriched_count}")
        logger.info(f"Déjà enrichis (ignorés): {skipped_count}")
        logger.info(f"Erreurs: {error_count}")
        logger.info(f"Taux de succès: {(enriched_count/(processed_count-skipped_count)*100) if (processed_count-skipped_count) > 0 else 0:.1f}%")
        
        logger.info(f"\nSTATISTIQUES PAR CATÉGORIE:")
        for category, stats in stats_by_category.items():
            logger.info(f"   {category}:")
            logger.info(f"      Total: {stats['total']}")
            logger.info(f"      Enrichis: {stats['enriched']}")
            logger.info(f"      Déjà présents: {stats['skipped']}")
            logger.info(f"      Erreurs: {stats['errors']}")
            if stats['total'] > stats['skipped']:
                success_rate = (stats['enriched']/(stats['total']-stats['skipped'])*100)
                logger.info(f"      Taux de succès: {success_rate:.1f}%")
        
        logger.info(f"{'='*70}")
        
    def close_connection(self):
        """Ferme la connexion MongoDB."""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("Connexion MongoDB fermée")

def main():
    """Fonction principale."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enrichit les données de tous les enseignants avec DBLP depuis MongoDB.')
    parser.add_argument('--mongo-url', type=str, default='mongodb://localhost:27017/',
                        help='URL de connexion MongoDB')
    parser.add_argument('--db-name', type=str, default='listic_personnes',
                        help='Nom de la base de données MongoDB')
    parser.add_argument('--workers', '-w', type=int, default=3,
                        help='Nombre maximum de workers concurrents')
    parser.add_argument('--delay', '-d', type=float, default=1.5,
                        help='Délai entre les requêtes (secondes)')
    
    args = parser.parse_args()
    
    # Créer l'enrichisseur
    enricher = DBLPMongoEnricher(max_workers=args.workers, delay=args.delay)
    
    try:
        # Se connecter à MongoDB
        if not enricher.connect_to_mongodb(args.mongo_url, args.db_name):
            sys.exit(1)
        
        # Enrichir tous les enseignants
        enricher.enrich_all_teachers()
        
    finally:
        # Fermer la connexion
        enricher.close_connection()

if __name__ == "__main__":
    main()