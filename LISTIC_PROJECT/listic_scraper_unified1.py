import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time
import sys
import hashlib
from datetime import datetime
from pymongo import MongoClient

# Configurer l'encodage pour éviter les erreurs avec les caractères spéciaux
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        
try:
    from PyPDF2 import PdfReader
except ImportError:
    print("ATTENTION: La bibliothèque PyPDF2 n'est pas installée. Veuillez l'installer avec 'pip install PyPDF2'")
    print("Le script va continuer mais ne pourra pas extraire le texte des PDFs.")
    PdfReader = None

def generate_unique_id_offre(offre_data):
    """
    Génère un ID unique basé sur le contenu d'une offre pour éviter les doublons
    """
    # Exclure certains champs qui peuvent changer (comme les timestamps) de l'ID unique
    data_for_id = {k: v for k, v in offre_data.items() if k not in ['date_extraction', '_id', '_unique_id']}
    content = json.dumps(data_for_id, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def save_category_to_mongodb_offres(collection, data_list, category_name):
    """
    Sauvegarde une catégorie d'offres dans MongoDB en évitant les doublons
    """
    if not data_list:
        print(f"⚠️ Aucune donnée trouvée pour la catégorie '{category_name}'")
        return
    
    saved_count = 0
    updated_count = 0
    skipped_count = 0
    
    for offre in data_list:
        # Générer un ID unique pour cette offre
        unique_id = generate_unique_id_offre(offre)
        offre['_unique_id'] = unique_id
        offre['category'] = category_name
        offre['last_updated'] = datetime.now().isoformat()
        
        try:
            # Utiliser replace_one avec upsert pour éviter les doublons
            result = collection.replace_one(
                {'_unique_id': unique_id},  # Filtre pour trouver le document
                offre,                      # Document à insérer/remplacer
                upsert=True                # Créer si n'existe pas
            )
            
            if result.upserted_id:
                saved_count += 1
            elif result.modified_count > 0:
                updated_count += 1
            else:
                skipped_count += 1
                
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde de {offre.get('titre', 'Inconnu')}: {e}")
    
    print(f"📊 '{category_name}': {saved_count} nouveaux, {updated_count} mis à jour, {skipped_count} inchangés")

def save_complete_structure_offres(db, all_data):
    """
    Sauvegarde la structure complète des offres dans une collection séparée
    """
    complete_data = {
        "_id": "all_offres_emploi",
        "data": all_data,
        "last_updated": datetime.now().isoformat(),
        "total_categories": len([k for k in all_data.keys() if k != 'metadata']),
        "statistics": {
            category: len(data) if isinstance(data, list) else 1 
            for category, data in all_data.items() if category != 'metadata'
        }
    }
    
    try:
        db["complete_structure_offres"].replace_one(
            {"_id": "all_offres_emploi"},
            complete_data,
            upsert=True
        )
        print("✅ Structure complète des offres sauvegardée dans 'complete_structure_offres'")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde de la structure complète: {e}")

def save_to_mongodb_offres(structure_finale):
    """
    Sauvegarde toutes les données d'offres dans MongoDB
    """
    print(f"\n{'='*60}")
    print("🗄️ SAUVEGARDE DANS MONGODB")
    print(f"{'='*60}")
    
    # Connexion à MongoDB
    try:
        # Remplacez par votre chaîne de connexion MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["listic_offres"]  # Nouvelle base pour les offres
        print("✅ Connexion à MongoDB établie")
    except Exception as e:
        print(f"❌ Erreur de connexion à MongoDB: {e}")
        print("Vérifiez que MongoDB est démarré et accessible.")
        return
    
    # Définir les catégories et leurs collections correspondantes
    categories_mapping = {
        "postes_enseignant_chercheur": "postes_enseignant_chercheur",
        "postes_enseignant_chercheur_contractuel": "postes_enseignant_chercheur_contractuel",
        "postes_ingenieur": "postes_ingenieur",
        "post_doc": "post_doc",
        "theses": "theses",
        "theses_passees": "theses_passees",
        "stages": "stages"
    }
    
    print(f"\n📋 IMPORT DES OFFRES PAR CATÉGORIE")
    
    # Traiter chaque catégorie
    for category_key, collection_name in categories_mapping.items():
        if category_key in structure_finale:
            data_list = structure_finale[category_key]
            print(f"\n🔄 Traitement de '{category_key}' -> Collection '{collection_name}'")
            
            collection = db[collection_name]
            save_category_to_mongodb_offres(collection, data_list, category_key)
        else:
            print(f"⚠️ Catégorie '{category_key}' non trouvée dans les données")
    
    # Sauvegarder la structure complète
    print(f"\n💾 SAUVEGARDE DE LA STRUCTURE COMPLÈTE")
    save_complete_structure_offres(db, structure_finale)
    
    # Statistiques finales MongoDB
    print(f"\n📊 STATISTIQUES MONGODB")
    total_docs = 0
    
    # Compter les documents dans chaque collection
    for category_key, collection_name in categories_mapping.items():
        try:
            count = db[collection_name].count_documents({})
            total_docs += count
            print(f"📋 {collection_name}: {count} documents")
        except:
            print(f"📋 {collection_name}: Erreur lors du comptage")
    
    print(f"📊 Total documents MongoDB: {total_docs}")
    
    # Fermer la connexion
    client.close()
    print("✅ Import MongoDB terminé!")

def scraper_offres_listic_unified():
    """
    Version unifiée qui extrait toutes les offres d'emploi du site LISTIC
    et les sauvegarde dans un seul fichier JSON structuré.
    """
    print("\n=== EXTRACTION DES OFFRES D'EMPLOI LISTIC (VERSION UNIFIÉE) ===")
    print("Date: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print("====================================\n")
    
    # Créer dossier pour les résultats avec des chemins absolus
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dossier_resultats = os.path.join(script_dir, "data")
    dossier_temp = os.path.join(dossier_resultats, "temp_offres")
    
    print(f"Création du dossier principal: {dossier_resultats}")
    os.makedirs(dossier_resultats, exist_ok=True)
    
    print(f"Création du dossier temporaire: {dossier_temp}")
    os.makedirs(dossier_temp, exist_ok=True)
    
    # URL du site à scraper
    url = 'https://www.univ-smb.fr/listic/informations/emplois/'
    print(f"Téléchargement de la page: {url}")
    
    # Récupérer le contenu de la page
    try:
        response = requests.get(url)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print(f"ERREUR lors du téléchargement de la page: {e}")
        return None
    
    # Charger le HTML dans BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extraire la date de mise à jour si disponible
    content_text = soup.get_text()
    date_maj = ""
    date_match = re.search(r'maj\s*:\s*(\d{2}/\d{2}/\d{4})', content_text)
    if date_match:
        date_maj = date_match.group(1)
        print(f"Date de mise à jour du site: {date_maj}")
    
    # Structure pour stocker les données (même format que projets/personnes)
    categories = {
        "postes_enseignant_chercheur": [],
        "postes_enseignant_chercheur_contractuel": [],
        "postes_ingenieur": [],
        "post_doc": [],
        "theses": [],
        "theses_passees": [],
        "stages": []
    }
    
    # Associer les titres de section aux clés de catégories
    section_to_key = {
        "POSTES D'ENSEIGNANT-CHERCHEUR": "postes_enseignant_chercheur",
        "POSTES D'ENSEIGNANT-CHERCHEUR CONTRACTUEL": "postes_enseignant_chercheur_contractuel",
        "POSTES D'INGENIEUR": "postes_ingenieur",
        "OFFRES DE POST-DOC": "post_doc",
        "OFFRES DE THÈSES": "theses",
        "OFFRES DE THÈSES PASSÉES": "theses_passees",
        "OFFRES DE STAGES": "stages"
    }
    
    # Fonction pour générer un nom de fichier sécurisé
    def safe_filename(text, max_length=50):
        if not text:
            return "sans_titre"
        
        text = str(text)
        safe_text = re.sub(r'[^\w\s-]', '_', text)
        safe_text = re.sub(r'\s+', '_', safe_text)
        safe_text = re.sub(r'_{2,}', '_', safe_text)
        if len(safe_text) > max_length:
            safe_text = safe_text[:max_length]
        safe_text = safe_text.encode('ascii', 'replace').decode('ascii').replace('?', '_')
        return safe_text
    
    # Analyser tous les liens de la page
    print("\nAnalyse des liens de la page...")
    
    for link in soup.find_all('a'):
        href = link.get('href')
        title = link.get_text().strip()
        
        if href and title and href.endswith('.pdf'):
            # Déterminer la catégorie basée sur l'URL
            category_key = None
            if '/enseignant-chercheur/' in href:
                category_key = "postes_enseignant_chercheur"
            elif '/post-doc/' in href:
                category_key = "post_doc"
            elif '/these/' in href:
                # Pour les thèses, vérifier si c'est une thèse passée ou actuelle
                parent_text = ""
                for parent in link.parents:
                    parent_text += parent.get_text().lower()
                
                if 'passées' in parent_text and 'thèses passées' in parent_text:
                    category_key = "theses_passees"
                else:
                    category_key = "theses"
            elif '/stage/' in href:
                category_key = "stages"
            elif '/ingenieur/' in href:
                category_key = "postes_ingenieur"
            else:
                # Si on ne peut pas déterminer la catégorie par l'URL
                for section_title, cat_key in section_to_key.items():
                    prev_text = ""
                    prev_elem = link
                    while prev_elem.previous_element and prev_text.count('\n') < 20:
                        prev_elem = prev_elem.previous_element
                        if hasattr(prev_elem, 'get_text'):
                            prev_text = prev_elem.get_text() + prev_text
                        elif isinstance(prev_elem, str):
                            prev_text = prev_elem + prev_text
                    
                    if section_title.lower() in prev_text.lower():
                        category_key = cat_key
                        break
            
            # Si on n'a pas encore déterminé la catégorie, vérifier les mots-clés dans le titre
            if not category_key:
                title_lower = title.lower()
                if "enseignant" in title_lower or "chercheur" in title_lower:
                    category_key = "postes_enseignant_chercheur"
                elif "post-doc" in title_lower or "postdoc" in title_lower:
                    category_key = "post_doc"
                elif "thèse" in title_lower or "these" in title_lower:
                    category_key = "theses"
                elif "stage" in title_lower:
                    category_key = "stages"
                elif "ingénieur" in title_lower or "ingenieur" in title_lower:
                    category_key = "postes_ingenieur"
                else:
                    category_key = "theses"  # Par défaut
            
            # Vérifier si cette offre est fermée
            is_closed = False
            if 'fermé' in title.lower() or 'ferme' in title.lower():
                is_closed = True
            else:
                parent_text = link.parent.get_text().lower() if link.parent else ""
                if 'fermé' in parent_text or 'ferme' in parent_text:
                    is_closed = True
            
            # Nettoyer le titre
            clean_title = re.sub(r'\s*fermé\s*!?', '', title, flags=re.IGNORECASE).strip()
            
            # Ajouter l'offre à la liste des offres de cette catégorie
            if category_key:
                categories[category_key].append({
                    "titre": clean_title,
                    "url": href,
                    "ferme": is_closed,
                    "url_listic": href  # Pour cohérence avec les autres scripts
                })
                
                # Afficher un message
                safe_title = clean_title.encode('ascii', 'replace').decode('ascii')
                print(f"  Offre trouvée ({category_key}): {safe_title}")
    
    # Compter le nombre total d'offres
    nb_offres = sum(len(offres) for offres in categories.values())
    print(f"\nNombre total d'offres trouvées: {nb_offres}")
    
    # Afficher le nombre d'offres par catégorie
    for cat, offres in categories.items():
        print(f"  {cat}: {len(offres)} offres")
    
    # Fonction pour extraire les informations d'un PDF
    def extraire_infos_pdf(pdf_url, titre):
        try:
            # Générer un nom de fichier temporaire
            nom_fichier = safe_filename(titre)
            chemin_pdf_temp = os.path.join(dossier_temp, f"{nom_fichier}.pdf")
            
            # Télécharger le PDF
            print(f"  Téléchargement temporaire du PDF: {pdf_url}")
            pdf_response = requests.get(pdf_url)
            pdf_response.raise_for_status()
            
            # Sauvegarder le PDF temporairement
            with open(chemin_pdf_temp, 'wb') as pdf_file:
                pdf_file.write(pdf_response.content)
            
            infos = {}
            
            # Extraire le texte si PyPDF2 est disponible
            if PdfReader:
                pdf_reader = PdfReader(chemin_pdf_temp)
                texte_complet = ""
                
                # Extraire le texte de chaque page
                for page in pdf_reader.pages:
                    page_text = page.extract_text() or ""
                    texte_complet += page_text + "\n"
                
                # Fonction pour trouver des correspondances dans le texte
                def trouver_correspondances(texte, patterns):
                    resultats = []
                    for pattern in patterns:
                        matches = re.finditer(pattern, texte, re.IGNORECASE | re.MULTILINE)
                        for match in matches:
                            if match.group(1).strip():
                                resultats.append(match.group(1).strip())
                    return resultats
                
                # Extraire différentes informations
                
                # Dates
                date_patterns = [
                    r'Date\s*(?:de publication|de début|limite|de candidature)?\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(?:Date|Publié le|Début|Publié|Candidater avant)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(?:Date|Publié le|Début|Publié|Candidater avant|avant le)\s*:?\s*(\d{1,2}\s+\w+\s+\d{2,4})',
                ]
                dates = trouver_correspondances(texte_complet, date_patterns)
                if dates:
                    infos["dates"] = "; ".join(dates)
                
                # Lieu
                lieu_patterns = [
                    r'Lieu\s*:?\s*([^\n\r\.]{3,50})',
                    r'Localisation\s*:?\s*([^\n\r\.]{3,50})',
                    r'Site\s*:?\s*([^\n\r\.]{3,50})',
                    r'Campus\s*:?\s*([^\n\r\.]{3,50})',
                ]
                lieux = trouver_correspondances(texte_complet, lieu_patterns)
                if lieux:
                    infos["lieu"] = "; ".join(lieux)
                
                # Durée / Contrat
                duree_patterns = [
                    r'Durée\s*:?\s*([^\n\r\.]{3,50})',
                    r'Type de contrat\s*:?\s*([^\n\r\.]{3,50})',
                    r'Contrat\s*:?\s*([^\n\r\.]{3,50})',
                    r'CDD\s*de\s*([^\n\r\.]{3,50})',
                ]
                durees = trouver_correspondances(texte_complet, duree_patterns)
                if durees:
                    infos["duree_contrat"] = "; ".join(durees)
                
                # Salaire
                salaire_patterns = [
                    r'Salaire\s*:?\s*([^\n\r\.]{3,80})',
                    r'Rémunération\s*:?\s*([^\n\r\.]{3,80})',
                    r'Montant\s*:?\s*([^\n\r\.]{3,80})',
                    r'rémunéré(?:e)?\s*(?:à hauteur de)?\s*([^\n\r\.]{3,80})',
                ]
                salaires = trouver_correspondances(texte_complet, salaire_patterns)
                if salaires:
                    infos["salaire"] = "; ".join(salaires)
                
                # Contacts
                contact_patterns = [
                    r'Contact\s*:?\s*([^\n\r\.]{3,100})',
                    r'(?:Contactez|Contacter|Pour postuler)\s*:?\s*([^\n\r\.]{3,100})',
                    r'(?:Envoyer|Adresser)\s*(?:votre|vos|les|un|une)?\s*(?:candidature|CV|lettre).*à\s*:?\s*([^\n\r\.]{3,100})',
                ]
                contacts = trouver_correspondances(texte_complet, contact_patterns)
                if contacts:
                    infos["contact"] = "; ".join(contacts)
                
                # Emails
                email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
                emails = re.findall(email_pattern, texte_complet)
                if emails:
                    infos["email"] = "; ".join(list(set(emails)))  # Éliminer les doublons
                
                # Mots-clés/Thèmes
                mots_cles_patterns = [
                    r'(?:Mots-clés|Keywords|Key words|Thématiques)\s*:?\s*([^\n\r]{5,100})',
                    r'(?:Thème|Theme|Sujet|Subject)\s*:?\s*([^\n\r]{5,100})',
                ]
                mots_cles = trouver_correspondances(texte_complet, mots_cles_patterns)
                if mots_cles:
                    infos["theme"] = "; ".join(mots_cles)
                
                # Description
                description_patterns = [
                    r'(?:Description|Résumé|Abstract|Descriptif|Présentation)\s*:?\s*([^\n\r]{20,500})',
                    r'(?:Contexte|Context)\s*:?\s*([^\n\r]{20,500})',
                ]
                descriptions = trouver_correspondances(texte_complet, description_patterns)
                if descriptions:
                    infos["description"] = "; ".join(descriptions)
                
                # Compétences
                competences_patterns = [
                    r'(?:Profil|Compétences|Qualifications|Qualification|Skills)\s*(?:recherché|requises|required)?\s*:?\s*([^\n\r]{10,500})',
                    r'(?:Candidat|Candidate)\s*:?\s*([^\n\r]{10,500})',
                ]
                competences = trouver_correspondances(texte_complet, competences_patterns)
                if competences:
                    infos["competences_requises"] = "; ".join(competences)
            
            # Supprimer le fichier PDF temporaire
            try:
                os.remove(chemin_pdf_temp)
            except:
                pass
            
            return infos
        
        except Exception as e:
            print(f"  ERREUR lors du traitement du PDF: {str(e)}")
            return {"erreur": str(e)}
    
    # Traiter chaque offre et enrichir les données
    print("\nExtraction des détails des PDFs...")
    
    # Parcourir chaque catégorie et chaque offre
    for categorie, offres in categories.items():
        for offre in offres:
            print(f"\nTraitement de l'offre: {offre['titre']}")
            
            if offre['url'].endswith('.pdf'):
                # Extraire les informations du PDF
                infos = extraire_infos_pdf(offre['url'], offre['titre'])
                
                # Ajouter les informations extraites à l'offre
                for cle, valeur in infos.items():
                    offre[cle] = valeur
            else:
                print(f"  L'URL ne pointe pas vers un PDF: {offre['url']}")
                offre["erreur"] = "L'URL ne pointe pas vers un PDF"
            
            # Ajouter des métadonnées
            offre["date_extraction"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Pause pour éviter de surcharger le serveur
            time.sleep(1)
    
    # Préparer la structure finale (même format que projets/personnes)
    structure_finale = {
        "metadata": {
            "date_extraction": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "date_maj_site": date_maj,
            "source_url": url,
            "nombre_total_offres": nb_offres,
            "categories": {
                categorie: len(offres) for categorie, offres in categories.items()
            }
        }
    }
    
    # Ajouter toutes les catégories à la structure finale
    structure_finale.update(categories)
    
    # Chemin du fichier JSON final
    json_file_path = os.path.join(dossier_resultats, "Offres_Emploi.json")
    
    # Sauvegarder dans le fichier JSON
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(structure_finale, json_file, ensure_ascii=False, indent=4)
    
    # Supprimer le dossier temporaire
    try:
        os.rmdir(dossier_temp)
    except:
        print(f"Impossible de supprimer le dossier temporaire")
    
    # Afficher le résumé
    print(f"\n{'='*60}")
    print("EXTRACTION TERMINÉE AVEC SUCCÈS!")
    print(f"{'='*60}")
    print(f"Nombre total d'offres trouvées: {nb_offres}")
    print(f"Fichier généré: {json_file_path}")
    print(f"Taille du fichier: {os.path.getsize(json_file_path)} bytes")
    
    # Afficher la structure des données
    print(f"\nStructure des données:")
    print(f"- metadata (informations générales)")
    for categorie, offres in categories.items():
        print(f"- {categorie}: {len(offres)} offres")
    
    # Proposer la sauvegarde MongoDB
    try:
        response = input("\n🗄️ Voulez-vous sauvegarder les données dans MongoDB? (o/n): ")
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            save_to_mongodb_offres(structure_finale)
    except:
        # En cas d'erreur (par exemple si le script est exécuté sans interaction)
        print("\n🗄️ Sauvegarde automatique dans MongoDB...")
        save_to_mongodb_offres(structure_finale)
    
    return {
        "json_file": json_file_path,
        "nombre_offres": nb_offres,
        "structure": structure_finale
    }

if __name__ == "__main__":
    scraper_offres_listic_unified()