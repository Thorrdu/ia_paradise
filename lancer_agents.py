#!/usr/bin/env python
"""
Script de lancement du système d'agents ParadisIA V2

Ce script initialise et lance le système d'agents pour le ParadisIA V2.
"""

import os
import sys
import logging
from pathlib import Path

# Ajouter le répertoire parent au path pour l'importation des modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from agents.main import main
except ImportError as e:
    print(f"Erreur lors de l'importation des modules: {e}")
    print("Vérifiez que vous exécutez ce script depuis le répertoire principal du projet.")
    sys.exit(1)

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀 Paradis IA V2 - Système d'Agents Intelligents 🧠    ║
║                                                           ║
║   * Agents Spécialisés                                    ║
║   * Communication Inter-IA                                ║
║   * Monitoring et Optimisation                            ║
║                                                           ║
║   Pour quitter: Ctrl+C                                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Vérifier les dépendances requises
    try:
        import psutil
        print("✅ Module psutil trouvé")
    except ImportError:
        print("❌ Module psutil manquant. Installation...")
        os.system(f"{sys.executable} -m pip install psutil")
        print("✅ Module psutil installé")
    
    # Créer les répertoires nécessaires
    for directory in ["logs", "config"]:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Répertoire {directory} prêt")
    
    print("\n🚀 Démarrage du système d'agents...\n")
    
    # Lancer le système d'agents
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du système d'agents. À bientôt!")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        logging.exception("Erreur critique lors de l'exécution:")
        sys.exit(1) 