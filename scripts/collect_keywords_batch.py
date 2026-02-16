"""
Script pour collecter des offres France Travail pour plusieurs mots-clés.
"""
import subprocess
import sys
from pathlib import Path

# Liste des mots-clés à requêter
KEYWORDS = [
    "data architect",
    "business intelligence",
    "mlops",
    "analytics engineer",
    "big data",
    "data manager",
    "cloud architect",
    "cloud engineer",
    "etl",
]


def run_collection(keyword: str) -> bool:
    """
    Lance la collecte pour un mot-clé donné.
    
    Args:
        keyword: Mot-clé à rechercher
        
    Returns:
        True si succès, False sinon
    """
    print(f"\n{'='*80}")
    print(f"🔍 Collecte pour : {keyword}")
    print(f"{'='*80}\n")
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pipelines.ingest.sources.francetravail.main",
                "--keywords",
                keyword,
            ],
            check=True,
            capture_output=False,
            text=True,
        )
        print(f"✅ Collecte réussie pour '{keyword}'")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la collecte pour '{keyword}': {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue pour '{keyword}': {e}")
        return False


def main():
    """Lance la collecte pour tous les mots-clés."""
    print("🚀 Début de la collecte par lots")
    print(f"📋 {len(KEYWORDS)} mots-clés à traiter\n")
    
    successes = 0
    failures = 0
    
    for i, keyword in enumerate(KEYWORDS, 1):
        print(f"\n[{i}/{len(KEYWORDS)}] Traitement de '{keyword}'...")
        
        if run_collection(keyword):
            successes += 1
        else:
            failures += 1
            
        # Petite pause entre les requêtes (optionnel, pour éviter rate limiting)
        if i < len(KEYWORDS):
            import time
            time.sleep(2)
    
    # Résumé final
    print(f"\n{'='*80}")
    print(f"📊 RÉSUMÉ DES COLLECTES")
    print(f"{'='*80}")
    print(f"✅ Réussies : {successes}")
    print(f"❌ Échouées : {failures}")
    print(f"📁 Total    : {len(KEYWORDS)}")
    print(f"{'='*80}\n")
    
    if failures > 0:
        print("⚠️  Certaines collectes ont échoué. Vérifiez les logs ci-dessus.")
        return 1
    else:
        print("✨ Toutes les collectes se sont terminées avec succès !")
        return 0


if __name__ == "__main__":
    sys.exit(main())
