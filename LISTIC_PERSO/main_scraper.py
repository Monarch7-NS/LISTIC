#!/usr/bin/env python3
"""
Script principal pour exécuter tous les scrapers LISTIC dans l'ordre correct
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Liste des scripts à exécuter dans l'ordre
SCRIPTS = [
    "enseignants_hercheurs1.py",
    "doctorants2.py", 
    "administratifs_techniques3.py",
    "collaborateurs_benevoles_chercheurs_associes4.py"
]

def run_script(script_path):
    """
    Exécute un script Python et retourne le code de retour
    """
    print(f"\n{'='*60}")
    print(f"🚀 Exécution de: {script_path}")
    print(f"{'='*60}")
    
    try:
        # Exécuter le script dans le même environnement Python
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, 
                              text=True)
        
        # Afficher la sortie standard
        if result.stdout:
            print("📄 Sortie:")
            print(result.stdout)
        
        # Afficher les erreurs
        if result.stderr:
            print("⚠️ Erreurs/Avertissements:")
            print(result.stderr)
        
        # Vérifier le code de retour
        if result.returncode == 0:
            print(f"✅ {script_path} exécuté avec succès!")
            return True
        else:
            print(f"❌ {script_path} a échoué avec le code de retour: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de {script_path}: {e}")
        return False

def check_script_exists(script_path):
    """
    Vérifie si un script existe
    """
    if not os.path.exists(script_path):
        print(f"❌ Le fichier {script_path} n'existe pas!")
        return False
    return True

def create_data_directory():
    """
    Crée le répertoire data s'il n'existe pas
    """
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir()
        print(f"📁 Répertoire 'data' créé")
    else:
        print(f"📁 Répertoire 'data' existe déjà")

def main():
    """
    Fonction principale
    """
    print("🔄 Démarrage du scraping LISTIC")
    print(f"📅 Heure de début: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Créer le répertoire data
    create_data_directory()
    
    # Statistiques
    success_count = 0
    total_scripts = len(SCRIPTS)
    failed_scripts = []
    
    # Obtenir le répertoire du script principal
    script_dir = Path(__file__).parent
    
    # Exécuter chaque script dans l'ordre
    for i, script_name in enumerate(SCRIPTS, 1):
        script_path = script_dir / script_name
        
        print(f"\n📋 Script {i}/{total_scripts}: {script_name}")
        
        # Vérifier si le script existe
        if not check_script_exists(script_path):
            failed_scripts.append(script_name)
            continue
        
        # Exécuter le script
        if run_script(script_path):
            success_count += 1
            time.sleep(2)  # Pause courte entre les scripts
        else:
            failed_scripts.append(script_name)
            
            # Demander si on continue en cas d'échec
            response = input(f"\n⚠️ Voulez-vous continuer avec les scripts restants? (o/n): ")
            if response.lower() not in ['o', 'oui', 'y', 'yes']:
                print("🛑 Arrêt demandé par l'utilisateur")
                break
    
    # Résumé final
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ FINAL")
    print(f"{'='*60}")
    print(f"✅ Scripts réussis: {success_count}/{total_scripts}")
    print(f"❌ Scripts échoués: {len(failed_scripts)}")
    
    if failed_scripts:
        print(f"📝 Scripts ayant échoué: {', '.join(failed_scripts)}")
    
    print(f"🕐 Heure de fin: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifier si le fichier final existe
    final_file = Path("data/Enseignants.json")
    if final_file.exists():
        file_size = final_file.stat().st_size
        print(f"📄 Fichier final généré: {final_file} ({file_size} bytes)")
    else:
        print("⚠️ Le fichier final Enseignants.json n'a pas été trouvé")
    
    print("\n🎉 Scraping terminé!")
    
    # Proposer l'import automatique vers MongoDB
    if final_file.exists():
        response = input("\n🗄️ Voulez-vous importer les données dans MongoDB? (o/n): ")
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            import_script = script_dir / "import_enseignants_mongodb.py"
            if import_script.exists():
                print(f"\n🚀 Lancement de l'import MongoDB...")
                if run_script(import_script):
                    print(f"✅ Import MongoDB terminé avec succès!")
                else:
                    print(f"❌ Erreur lors de l'import MongoDB")
            else:
                print(f"⚠️ Script d'import MongoDB non trouvé: {import_script}")
                print("Assurez-vous que 'import_enseignants_mongodb.py' est dans le même répertoire.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Interruption par l'utilisateur (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)