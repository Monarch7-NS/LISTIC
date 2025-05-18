# 🎓 LISTIC Data Mining Project

Ce projet complet permet l'extraction, l'enrichissement et la gestion automatisée de toutes les données du laboratoire LISTIC (Université Savoie Mont Blanc) depuis leur site web vers des fichiers JSON et des bases de données MongoDB.

## 📁 Structure du projet

```
📦 LISTIC_PROJECT/
├── 📋 README.md
├── 🎓 LISTIC_PERSO/           # Personnel et enseignants
│   ├── 🐍 Scripts de scraping
│   ├── 🚀 main_scraper.py     # Script principal
│   ├── 🗄️ import_enseignants_mongodb.py
│   └── 📂 data/Enseignants.json
│
├── 📚 LISTIC_PROJECT/         # Projets de recherche
│   ├── 🐍 projet_data.py
│   ├── 🐍 listic_scraper_unified1.py
│   └── 📄 all_tables.json
│
├── 💼 LISTIC_OFFRES/          # Offres d'emploi
│   ├── 🐍 listic_offres.py
│   └── 📂 data/Offres_Emploi.json
│
├── 📖 DBLP/                   # Enrichissement publications DBLP
│   ├── 🐍 dblp_enricher_fixed.py
│   └── 📊 dblp_enrichment.log
│
├── 📑 HAL/                    # Enrichissement publications HAL
│   ├── 🐍 hal_mongo_enricher_v2.py
│   ├── 🔍 detailed_mongo_diagnostic.py
│   └── 📊 hal_enrichment.log
│
└── 📅 CORF/                   # Conférences
    └── 📄 listic_conferences_json.json
```

## 🎯 Fonctionnalités principales

### 1️⃣ **Extraction du personnel LISTIC** (`LISTIC_PERSO/`)
- **Enseignants-chercheurs** avec contacts et informations complètes
- **Doctorants** (internes et externes) avec thèmes de recherche
- **Personnel administratif et technique**
- **Collaborateurs bénévoles et chercheurs associés**
- **Professeurs émérites**

### 2️⃣ **Extraction des projets** (`LISTIC_PROJECT/`)
- **Projets internationaux**
- **Projets nationaux**
- **Projets régionaux**
- **Projets d'incubation**

### 3️⃣ **Extraction des offres d'emploi** (`LISTIC_OFFRES/`)
- **Postes d'enseignant-chercheur**
- **Offres de post-doc**
- **Offres de thèses et stages**
- **Postes d'ingénieur**

### 4️⃣ **Enrichissement avec publications** (`DBLP/` & `HAL/`)
- **DBLP** : publications informatiques, co-auteurs, venues
- **HAL** : publications françaises, mots-clés, domaines

## 🚀 Installation et prérequis

### Dépendances Python
```bash
pip install requests beautifulsoup4 lxml pymongo pandas PyPDF2
```

### MongoDB (optionnel pour enrichissement)
- Installer MongoDB localement ou utiliser MongoDB Atlas
- URL par défaut : `mongodb://localhost:27017/`

## 📘 Guide d'utilisation

### 🔄 **Workflow complet recommandé**

#### Étape 1 : Extraction du personnel
```bash
cd LISTIC_PERSO
python main_scraper.py
# Génère: data/Enseignants.json
# Option: Import automatique vers MongoDB
```

#### Étape 2 : Extraction des projets
```bash
cd LISTIC_PROJECT
python projet_data.py
# Génère: all_tables.json
# Import automatique vers MongoDB (base: listic_projets)
```

#### Étape 3 : Extraction des offres d'emploi
```bash
cd LISTIC_OFFRES
python listic_offres.py
# Génère: data/Offres_Emploi.json
# Option: Import vers MongoDB (base: listic_offres_data)
```

#### Étape 4 : Enrichissement avec DBLP
```bash
cd DBLP
python dblp_enricher_fixed.py
# Enrichit les enseignants avec leurs publications DBLP
# Base MongoDB: listic_personnes
```

#### Étape 5 : Enrichissement avec HAL
```bash
cd HAL
python hal_mongo_enricher_v2.py  
# Enrichit les enseignants avec leurs publications HAL
# Base MongoDB: listic_personnes
```

### 🛠️ **Utilisation avancée**

#### Configuration MongoDB personnalisée
```bash
# Changer la base de données
python script.py --db-name votre_base

# Changer l'URL MongoDB
python script.py --mongo-url mongodb://votre-serveur:27017/

# Ajuster les performances
python script.py --workers 5 --delay 2.0
```

#### Diagnostic MongoDB
```bash
cd HAL
python detailed_mongo_diagnostic.py
# Affiche toutes les bases et collections disponibles
```

## 📊 Structures des données par module

### 🎓 **LISTIC_PERSO - Personnel** (`Enseignants.json`)

#### Structure générale :
```json
{
  "enseignants_chercheurs": [...],
  "émérite": [...],
  "doctorants": [...],
  "doctorants_externe": [...],
  "administratif_et_technique": [...],
  "collaborateurs_benevoles": [...],
  "chercheurs_associes": [...]
}
```

#### Enseignant-chercheur type :
```json
{
  "name": "Alexandre BENOIT",
  "email": "alexandre.benoit@univ-smb.fr",
  "phone": "+33(0)450096578",
  "office": "A227",
  "address": "LISTIC - Polytech Annecy-Chambéry...",
  "url_listic": "https://www.univ-smb.fr/listic/...",
  "fax": "+33(0)450096559",
  "category": "enseignants_chercheurs",
  "_unique_id": "md5_hash",
  "last_updated": "2025-01-18T10:30:00"
}
```

#### Doctorant type :
```json
{
  "name": "Zaid ALLAL",
  "url_listic": "https://www.univ-smb.fr/listic/...",
  "email": "zaid.allal@univ-smb.fr",
  "email perso": "zaid.allal@gmail.com", 
  "LinkedIn": "https://www.linkedin.com/in/...",
  "phone": "+33123456789",
  "WhatsApp": "+212987654321",
  "office": "A123",
  "address": "LISTIC...",
  "Theme": "Intelligence Artificielle",
  "Sujet": "Machine Learning pour...",
  "Résumé": "Cette thèse porte sur...",
  "category": "doctorants"
}
```

#### Personnel administratif type :
```json
{
  "name": "Florent BALDINI",
  "title": "Ingénieur d'études",
  "email": null,
  "phone": null,
  "office": null,
  "address": null,
  "url_listic": null,
  "category": "administratif_et_technique"
}
```

### 📚 **LISTIC_PROJECT - Projets** (`all_tables.json`)

#### Structure générale :
```json
{
  "Internationaux": [...],
  "Nationaux": [...], 
  "Regionaux": [...],
  "Incubation": [...]
}
```

#### Projet international type :
```json
{
  "NOM": "SNOW - Multi-sensor observation of snow",
  "MOTS CLÉS": "Télédétection, Neige, Fusion de données",
  "PARTENAIRES": "CESBIO, IGN, Météo-France",
  "FINANCEURS": "ESA, CNES",
  "PÉRIODE": "2020-2023",
  "_unique_id": "md5_hash"
}
```

#### Projet d'incubation type :
```json
{
  "NOM": "STARTUP Innovation Tech",
  "MOTS CLÉS": "Intelligence artificielle, Startup",
  "FINANCEURS": "Région Auvergne-Rhône-Alpes",
  "PÉRIODE": "2024-2025",
  "_unique_id": "md5_hash"
}
```

### 💼 **LISTIC_OFFRES - Emploi** (`Offres_Emploi.json`)

#### Structure générale :
```json
{
  "metadata": {
    "date_extraction": "2025-01-18T10:30:00",
    "date_maj_site": "15/01/2025",
    "source_url": "https://www.univ-smb.fr/listic/informations/emplois/",
    "nombre_total_offres": 25,
    "categories": {
      "stages": 16,
      "theses": 1,
      "post_doc": 1,
      "theses_passees": 7
    }
  },
  "postes_enseignant_chercheur": [...],
  "stages": [...],
  "theses": [...],
  "post_doc": [...],
  "theses_passees": [...]
}
```

#### Offre de stage type :
```json
{
  "titre": "Stage M2 - Vision par ordinateur",
  "url": "https://www.univ-smb.fr/listic/.../stage.pdf",
  "url_listic": "https://www.univ-smb.fr/listic/.../stage.pdf",
  "ferme": false,
  "contact": "Prof. Martin (martin@univ-smb.fr)",
  "theme": "Computer Vision, Machine Learning",
  "description": "Développement d'algorithmes de...",
  "competences_requises": "Python, OpenCV, TensorFlow",
  "date_extraction": "2025-01-18T10:30:00",
  "_unique_id": "md5_hash",
  "category": "stages"
}
```

#### Offre de thèse type :
```json
{
  "titre": "Thèse - Apprentissage automatique distribué",
  "url": "https://www.univ-smb.fr/listic/.../these.pdf",
  "url_listic": "https://www.univ-smb.fr/listic/.../these.pdf", 
  "ferme": false,
  "lieu": "Annecy",
  "email": "directeur.these@univ-smb.fr",
  "theme": "Machine Learning, Distributed Computing",
  "competences_requises": "PhD en informatique, Python, Kubernetes",
  "date_extraction": "2025-01-18T10:30:00",
  "_unique_id": "md5_hash",
  "category": "theses"
}
```

### 📖 **DBLP - Publications informatiques** (enrichissement MongoDB)

#### Structure ajoutée aux enseignants :
```json
{
  "name": "Alexandre BENOIT",
  "email": "alexandre.benoit@univ-smb.fr",
  // ... autres champs ...
  "dblp_data": {
    "dblp_url": "https://dblp.org/pid/12/3456",
    "publications": [
      {
        "title": "Deep Learning for Computer Vision",
        "year": "2023",
        "venue": "CVPR",
        "coauthors": ["John DOE", "Jane SMITH"],
        "url": "https://dblp.org/rec/conf/cvpr/..."
      }
    ],
    "publication_count": 45,
    "coauthors": ["John DOE", "Jane SMITH", "Bob MARTIN"],
    "venues": ["CVPR", "ICCV", "ECCV", "IEEE Trans Image Process"],
    "years": ["2018", "2019", "2020", "2021", "2022", "2023"],
    "last_updated": "2025-01-18T10:30:00"
  },
  "last_dblp_update": "2025-01-18T10:30:00"
}
```

### 📑 **HAL - Publications françaises** (enrichissement MongoDB)

#### Structure ajoutée aux enseignants :
```json
{
  "name": "Alexandre BENOIT",
  "email": "alexandre.benoit@univ-smb.fr",
  // ... autres champs ...
  "hal_data": {
    "hal_publications": [
      {
        "hal_id": "hal-01234567",
        "citation": "Benoit, A., Doe, J. 'Vision par ordinateur...' 2023",
        "authors": "Alexandre Benoit; John Doe; Jane Smith",
        "year": "2023",
        "abstract": "Cette publication présente une nouvelle approche...",
        "keywords": "vision par ordinateur; apprentissage automatique",
        "domain": "info.ai; cs.cv",
        "url": "https://hal.archives-ouvertes.fr/hal-01234567"
      }
    ],
    "publication_count": 32,
    "all_authors": ["Alexandre Benoit", "John Doe", "Jane Smith"],
    "years": ["2019", "2020", "2021", "2022", "2023"],
    "keywords": ["vision par ordinateur", "apprentissage automatique", "traitement d'images"],
    "domains": ["info.ai", "cs.cv", "info.ti"],
    "last_updated": "2025-01-18T10:30:00"
  },
  "last_hal_update": "2025-01-18T10:30:00"
}
```

### 📅 **CORF - Conférences** (`listic_conferences_json.json`)

#### Structure anticipée :
```json
{
  "conferences": [
    {
      "nom": "CVPR 2024",
      "date": "2024-06-17",
      "lieu": "Seattle, USA",
      "url": "https://cvpr2024.thecvf.com/",
      "domaine": "Computer Vision",
      "deadline": "2023-11-17",
      "type": "Internationale"
    }
  ],
  "metadata": {
    "date_extraction": "2025-01-18T10:30:00",
    "nombre_conferences": 156
  }
}
```

## 🔑 Champs communs à tous les modules

### Métadonnées de traçabilité :
- **`_unique_id`** : Hash MD5 pour éviter les doublons
- **`category`** : Catégorie/type de l'élément
- **`last_updated`** : Timestamp de dernière mise à jour
- **`date_extraction`** : Date d'extraction depuis le site web

### Champs de contact standardisés :
- **`email`** : Adresse email institutionnelle
- **`phone`** : Numéro de téléphone (format français)
- **`office`** : Bureau (format "A123")
- **`address`** : Adresse complète du laboratoire
- **`url_listic`** : URL de la page personnelle LISTIC

### Bases de données créées :
- **`listic_personnes`** : Personnel enrichi avec DBLP/HAL
  - Collections : `enseignants_chercheurs`, `doctorants`, `emerites`, `administratifs_techniques`, `collaborateurs_benevoles`, `chercheurs_associes`, `doctorants_externes`
- **`listic_projets`** : Projets de recherche
  - Collections : `Internationaux`, `Nationaux`, `Regionaux`, `Incubation`
- **`listic_offres_data`** : Offres d'emploi
  - Collections : `stages`, `theses`, `post_doc`, `postes_enseignant_chercheur`, `theses_passees`

### Structure d'un enseignant enrichi :
```json
{
  "_id": "ObjectId(...)",
  "name": "Prof. Martin",
  "email": "martin@univ-smb.fr",
  "phone": "+33(0)450096578",
  "office": "A227",
  "category": "enseignants_chercheurs",
  "dblp_data": {
    "publications": [...],
    "coauthors": [...],
    "publication_count": 42,
    "years": ["2020", "2021", "2022"]
  },
  "hal_data": {
    "hal_publications": [...],
    "keywords": [...],
    "domains": [...],
    "publication_count": 35
  },
  "last_dblp_update": "2025-01-18T10:30:00",
  "last_hal_update": "2025-01-18T10:30:00"
}
```

## ✨ Fonctionnalités avancées

### 🔄 **Gestion des doublons**
- Tous les scripts évitent automatiquement la duplication
- **IDs uniques** basés sur le contenu
- **Mise à jour intelligente** des données modifiées

### 📊 **Statistiques et logs**
- **Logs détaillés** pour chaque script
- **Rapports d'exécution** avec statistiques
- **Gestion d'erreurs** robuste

### 🚫 **Extraction respectueuse**
- **Délais** entre requêtes pour éviter la surcharge
- **Multithreading** contrôlé
- **Gestion des timeouts**

## 🛠️ Résolution de problèmes

### Problèmes courants

#### MongoDB non accessible
```bash
# Vérifier que MongoDB fonctionne
mongod --version
sudo systemctl start mongod  # Linux
net start mongodb            # Windows
```

#### Erreurs d'encodage (Windows)
- Les scripts gèrent automatiquement l'UTF-8
- Logs sans émojis pour compatibilité Windows

#### Connexion internet instable
- Augmenter les délais : `--delay 3.0`
- Réduire les workers : `--workers 2`

### Statistiques MongoDB
```bash
mongosh
> show dbs
> use listic_personnes
> db.enseignants_chercheurs.count()
> use listic_projets  
> db.Internationaux.count()
```

## 📈 Utilisation des données

### Exemples d'analyses possibles :
- **Réseaux de collaboration** via co-auteurs DBLP/HAL
- **Évolution des thématiques** via mots-clés HAL
- **Productivité par équipe** via nombre de publications
- **Cartographie des projets** par financement/partenaire
- **Analyse du marché de l'emploi** via offres d'emploi

### Export des données :
```bash
# Export JSON depuis MongoDB
mongoexport --db=listic_personnes --collection=enseignants_chercheurs --out=export.json
mongoexport --db=listic_projets --collection=Internationaux --out=projets_internationaux.json

# Export CSV
mongoexport --db=listic_personnes --collection=enseignants_chercheurs --type=csv --fields=name,email --out=export.csv
```

## 🔄 Automatisation

### Script global (recommandé)
```bash
#!/bin/bash
# Workflow complet automatisé

echo "=== EXTRACTION LISTIC COMPLÈTE ==="

# 1. Personnel
cd LISTIC_PERSO && python main_scraper.py

# 2. Projets  
cd ../LISTIC_PROJECT && python projet_data.py

# 3. Offres
cd ../LISTIC_OFFRES && python listic_offres.py

# 4. Enrichissement DBLP
cd ../DBLP && python dblp_enricher_fixed.py

# 5. Enrichissement HAL
cd ../HAL && python hal_mongo_enricher_v2.py

echo "=== EXTRACTION TERMINÉE ==="
```

### Planification automatique (cron)
```bash
# Exécution hebdomadaire le dimanche à 2h
0 2 * * 0 /path/to/listic_project/run_all.sh
```

## 🤝 Contribution

### Structure pour nouveaux scripts :
1. **Créer un dossier** pour la nouvelle source (ex: `GOOGLE_SCHOLAR/`)
2. **Suivre la convention** de nommage : `script_principal.py`
3. **Intégrer MongoDB** avec gestion anti-doublons
4. **Ajouter logs** et gestion d'erreurs
5. **Documenter** dans ce README

### Bonnes pratiques :
- Respecter les délais entre requêtes
- Gérer les erreurs proprement  
- Logger les statistiques d'exécution
- Éviter la duplication des données

## 📄 Licence

Ce projet est destiné à un usage académique et de recherche pour le laboratoire LISTIC.

## 📞 Support

Pour toute question ou problème :
1. Vérifier les logs dans chaque dossier
2. Utiliser le script de diagnostic MongoDB
3. Consulter la documentation des APIs (DBLP, HAL)

---

## 🎉 Résultat final

Ce projet vous permet d'obtenir une **base de données complète et enrichie** de tout l'écosystème LISTIC :
- **Personnel** avec publications académiques
- **Projets** de recherche actifs
- **Offres** d'emploi actualisées
- **Données** structurées et interrogeables

*Dernière mise à jour : Mai 2025*