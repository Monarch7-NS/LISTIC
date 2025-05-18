#!/usr/bin/env python3
"""
HAL MongoDB Integration Script

Ce script enrichit les données des enseignants stockées dans MongoDB 
avec leurs publications depuis HAL (archives-ouvertes.fr).
"""

import requests
import os
import html
import re
import json
import logging
import time
from pymongo import MongoClient
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hal_enrichment.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HALMongoEnricher:
    """Classe pour enrichir les données des enseignants avec HAL depuis MongoDB."""
    
    def __init__(self, max_workers=2, delay=2.0):
        """
        Initialise l'enrichisseur HAL.
        
        Args:
            max_workers (int): Nombre maximum de workers pour le multithreading
            delay (float): Délai entre les requêtes pour respecter HAL
        """
        self.max_workers = max_workers
        self.delay = delay
        self.hal_api_base = "https://api.archives-ouvertes.fr/search/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; HALScraper/1.0)'
        }
        self.db = None
        self.collection = None
        
    def connect_to_mongodb(self, connection_string="mongodb://localhost:27017/", db_name="listic_personnes"):
        """
        Se connecte à MongoDB et initialise les collections.
        
        Args:
            connection_string (str): Chaîne de connexion MongoDB
            db_name (str): Nom de la base de données (listic_personnes par défaut)
        """
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[db_name]
            
            # Collections d'enseignants dans listic_personnes
            self.collections_to_process = [
                "enseignants_chercheurs",
                "emerites", 
                "doctorants",
                "doctorants_externes",
                "administratifs_techniques",
                "collaborateurs_benevoles",
                "chercheurs_associes"
            ]
            
            # Vérifier quelles collections existent et contiennent des données
            available_collections = self.db.list_collection_names()
            logger.info(f"Collections disponibles dans {db_name}: {available_collections}")
            
            self.valid_collections = []
            total_documents = 0
            
            for col_name in self.collections_to_process:
                if col_name in available_collections:
                    collection = self.db[col_name]
                    count = collection.count_documents({})
                    if count > 0:
                        self.valid_collections.append(col_name)
                        total_documents += count
                        logger.info(f"Collection {col_name}: {count} documents")
                    else:
                        logger.info(f"Collection {col_name}: vide")
                else:
                    logger.info(f"Collection {col_name}: non trouvée")
            
            if not self.valid_collections:
                logger.error("Aucune collection valide trouvée!")
                return False
            
            logger.info(f"Connexion MongoDB établie - Base: {db_name}, Total documents: {total_documents}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur de connexion à MongoDB: {e}")
            return False
    
    def search_hal(self, query):
        """
        Recherche les publications HAL pour un nom donné (version améliorée).
        
        Args:
            query (str): Nom de l'enseignant à rechercher
            
        Returns:
            list: Liste des publications HAL trouvées
        """
        # Recherche plus précise par nom d'auteur complet
        url = f'{self.hal_api_base}'
        params = {
            "q": f'authFullName_t:"{query}"',  # Recherche spécifique par nom d'auteur
            "wt": "json",
            "fl": "docid,label_s,uri_s,abstract_s,abstractFr_s,description_s,abstract_en_s,abstract_fr_s,authFullName_s,producedDate_tdate,publicationDate_tdate,submittedDate_tdate,keyword_s,domain_s",
            "rows": 100  # Plus de résultats
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get('response', {}).get('docs', [])
        except requests.RequestException as e:
            logger.error(f"Requête HAL échouée pour {query}: {e}")
            return []
        except ValueError:
            logger.error(f"Réponse JSON HAL invalide pour {query}")
            return []
    
    def clean_html_entities(self, text):
        """Nettoie les entités HTML d'un texte."""
        if isinstance(text, list):
            text = ", ".join(text)
        return html.unescape(text) if text else 'Non disponible'
    
    def extract_article_info(self, label):
        """
        Extrait les informations d'un article depuis son label HAL.
        
        Args:
            label (str): Label de l'article HAL
            
        Returns:
            tuple: (auteurs, année, citation)
        """
        authors_match = re.match(r'^(.*?)(?=\.\s)', label)
        citation_match = re.search(r'(\d{4})', label)
        
        authors = authors_match.group(1) if authors_match else 'Non disponible'
        year = citation_match.group(1) if citation_match else 'Non disponible'
        citation = self.clean_html_entities(label)
        
        return authors, year, citation
    
    def extract_abstract(self, article):
        """
        Extrait le résumé d'un article HAL.
        
        Args:
            article (dict): Article HAL
            
        Returns:
            str: Résumé de l'article
        """
        for key in ['abstract_s', 'abstractFr_s', 'description_s', 'abstract_en_s', 'abstract_fr_s']:
            if key in article and article[key]:
                return self.clean_html_entities(article[key])
        return 'Non disponible'
    
    def process_hal_articles(self, articles):
        """
        Traite une liste d'articles HAL et les structure (version améliorée).
        
        Args:
            articles (list): Liste d'articles HAL bruts
            
        Returns:
            list: Liste d'articles structurés
        """
        processed_articles = []
        
        for article in articles:
            # ID et titre
            doc_id = article.get('docid', 'Non disponible')
            citation_raw = article.get('label_s', 'Non disponible')
            
            # Auteurs complets
            authors = article.get('authFullName_s', [])
            if isinstance(authors, list):
                authors_str = "; ".join(authors)
            else:
                authors_str = str(authors) if authors else 'Non disponible'
            
            # Extraction année améliorée
            year = 'Non disponible'
            for date_field in ['publicationDate_tdate', 'producedDate_tdate', 'submittedDate_tdate']:
                if article.get(date_field):
                    year = article[date_field][:4]
                    break
            
            # Résumé avec priorité au français
            abstract = self.extract_abstract(article)
            
            # Mots-clés et domaine
            keywords = article.get('keyword_s', [])
            if isinstance(keywords, list):
                keywords_str = "; ".join(keywords)
            else:
                keywords_str = str(keywords) if keywords else 'Non disponible'
            
            domain = article.get('domain_s', [])
            if isinstance(domain, list):
                domain_str = "; ".join(domain)
            else:
                domain_str = str(domain) if domain else 'Non disponible'
            
            # URL
            link = article.get('uri_s', 'Non disponible')
            
            processed_articles.append({
                "hal_id": doc_id,
                "citation": citation_raw,
                "authors": authors_str,
                "year": year,
                "abstract": abstract,
                "keywords": keywords_str,
                "domain": domain_str,
                "url": link
            })
        
        return processed_articles
    
    def search_teacher_on_hal(self, teacher_doc):
        """
        Recherche un enseignant sur HAL et extrait ses publications.
        
        Args:
            teacher_doc (dict): Document MongoDB de l'enseignant
            
        Returns:
            dict: Données HAL (None si non trouvées)
        """
        name = teacher_doc.get('name', '')
        category = teacher_doc.get('category', 'unknown')
        logger.info(f"Recherche HAL pour: {name} ({category})")
        
        # Vérifier si les données HAL existent déjà
        if teacher_doc.get('hal_data'):
            logger.info(f"Données HAL déjà présentes pour {name}, ignoré")
            return None
        
        try:
            # Rechercher sur HAL
            articles = self.search_hal(name)
            
            if not articles:
                logger.warning(f"Aucune publication HAL trouvée pour {name}")
                return None
            
            # Traiter les articles
            processed_articles = self.process_hal_articles(articles)
            
            # Créer la structure des données HAL (version enrichie)
            hal_data = {
                "hal_publications": processed_articles,
                "publication_count": len(processed_articles),
                "all_authors": list(set([article['authors'] for article in processed_articles if article['authors'] != 'Non disponible'])),
                "years": sorted(list(set([article['year'] for article in processed_articles if article['year'] != 'Non disponible']))),
                "keywords": list(set([kw.strip() for article in processed_articles if article.get('keywords', 'Non disponible') != 'Non disponible' for kw in article['keywords'].split(';')])),
                "domains": list(set([dom.strip() for article in processed_articles if article.get('domain', 'Non disponible') != 'Non disponible' for dom in article['domain'].split(';')])),
                "last_updated": datetime.now().isoformat()
            }
            
            logger.info(f"HAL: {name} ({category}) - {hal_data['publication_count']} publications trouvées")
            return hal_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche HAL pour {name}: {e}")
            return None
    
    def update_teacher_with_hal_data(self, teacher_doc, hal_data):
        """
        Met à jour le document de l'enseignant avec les données HAL.
        
        Args:
            teacher_doc (dict): Document MongoDB de l'enseignant
            hal_data (dict): Données HAL à ajouter
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
                "hal_data": hal_data,
                "last_hal_update": datetime.now().isoformat()
            }
            
            result = collection.update_one(
                {"_id": teacher_doc["_id"]},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"MongoDB: Données HAL mises à jour pour {teacher_doc.get('name')} dans {collection_name}")
            else:
                logger.warning(f"MongoDB: Aucune modification pour {teacher_doc.get('name')}")
                
        except Exception as e:
            logger.error(f"Erreur MongoDB pour {teacher_doc.get('name')}: {e}")
    
    def process_teacher(self, teacher_doc):
        """
        Traite un enseignant : recherche HAL + mise à jour MongoDB.
        
        Args:
            teacher_doc (dict): Document MongoDB de l'enseignant
        """
        # Rechercher sur HAL
        hal_data = self.search_teacher_on_hal(teacher_doc)
        
        if hal_data:
            # Mettre à jour MongoDB avec les nouvelles données
            self.update_teacher_with_hal_data(teacher_doc, hal_data)
        
        # Respecter le délai
        time.sleep(self.delay)
    
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
    
    def enrich_all_teachers(self):
        """
        Enrichit tous les enseignants avec les données HAL.
        """
        all_teachers = self.get_all_teachers_from_mongodb()
        
        if not all_teachers:
            logger.error("Aucun enseignant à enrichir")
            return
        
        logger.info(f"Début de l'enrichissement HAL pour {len(all_teachers)} enseignants")
        
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
            
            # Traiter les résultats
            for future in as_completed(future_to_teacher):
                teacher = future_to_teacher[future]
                processed_count += 1
                category = teacher.get('category', 'unknown')
                
                # Initialiser les stats pour cette catégorie
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
                        
                        if updated_teacher and updated_teacher.get("hal_data"):
                            enriched_count += 1
                            stats_by_category[category]['enriched'] += 1
                        elif updated_teacher and "hal_data" in updated_teacher:
                            skipped_count += 1
                            stats_by_category[category]['skipped'] += 1
                    
                except Exception as e:
                    error_count += 1
                    stats_by_category[category]['errors'] += 1
                    logger.error(f"Erreur lors du traitement de {teacher.get('name')}: {e}")
                
                # Afficher le progrès
                if processed_count % 10 == 0:
                    logger.info(f"Progrès: {processed_count}/{len(all_teachers)} traités ({(processed_count/len(all_teachers)*100):.1f}%)")
        
        # Rapport final
        logger.info(f"\n{'='*70}")
        logger.info("RAPPORT FINAL D'ENRICHISSEMENT HAL")
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
    
    parser = argparse.ArgumentParser(description='Enrichit les données des enseignants avec HAL depuis MongoDB.')
    parser.add_argument('--mongo-url', type=str, default='mongodb://localhost:27017/',
                        help='URL de connexion MongoDB')
    parser.add_argument('--db-name', type=str, default='listic_personnes',
                        help='Nom de la base de données MongoDB')
    parser.add_argument('--workers', '-w', type=int, default=2,
                        help='Nombre maximum de workers concurrents')
    parser.add_argument('--delay', '-d', type=float, default=2.0,
                        help='Délai entre les requêtes (secondes)')
    
    args = parser.parse_args()
    
    # Créer l'enrichisseur
    enricher = HALMongoEnricher(max_workers=args.workers, delay=args.delay)
    
    try:
        # Se connecter à MongoDB
        if not enricher.connect_to_mongodb(args.mongo_url, args.db_name):
            return
        
        # Enrichir tous les enseignants
        enricher.enrich_all_teachers()
        
    finally:
        # Fermer la connexion
        enricher.close_connection()

if __name__ == "__main__":
    main()