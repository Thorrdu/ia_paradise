#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de démarrage pour l'interface web de Paradis IA.
Ce script initialise l'environnement et lance le serveur web.
"""

import os
import sys
import time
import subprocess
import threading
import atexit

# Couleurs pour la console
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    YELLOW = '\033[93m'  # Ajout de YELLOW comme alias de WARNING
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Détection de l'environnement Python
PYTHON_EXECUTABLE = sys.executable
print(f"Utilisation de l'exécutable Python: {PYTHON_EXECUTABLE}")

# Commandes à exécuter en parallèle
commands = [
    {
        "name": "Serveur Web",
        "cmd": f'cd web && "{PYTHON_EXECUTABLE}" app.py',
        "wait": False,
        "color": Colors.BLUE
    }
]

# Processus en cours d'exécution
running_processes = []

def print_header():
    """Affiche l'en-tête de l'application."""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 80)
    print("                      PARADIS IA - INTERFACE WEB")
    print("=" * 80)
    print(f"{Colors.ENDC}")
    print(f"{Colors.GREEN}Démarrage des composants...{Colors.ENDC}\n")

def run_command(command):
    """Exécute une commande dans un processus séparé."""
    name = command["name"]
    cmd = command["cmd"]
    color = command.get("color", "")
    
    print(f"{color}[{name}] Démarrage... {Colors.ENDC}")
    
    try:
        # Créer un processus pour la commande
        if sys.platform == 'win32':
            # Sur Windows, utiliser shell=True
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            # Sur Unix/Linux
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
        
        # Ajouter le processus à la liste des processus en cours
        running_processes.append((name, process))
        
        # Lire et afficher la sortie du processus
        for line in iter(process.stdout.readline, ''):
            print(f"{color}[{name}] {line.rstrip()}{Colors.ENDC}")
        
        # Attendre que le processus se termine
        process.wait()
        
        print(f"{color}[{name}] Terminé avec le code de sortie {process.returncode}{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.RED}[{name}] Erreur: {str(e)}{Colors.ENDC}")

def cleanup():
    """Arrête tous les processus en cours avant de quitter."""
    print(f"\n{Colors.WARNING}Arrêt des processus en cours...{Colors.ENDC}")
    
    for name, process in running_processes:
        try:
            if process.poll() is None:  # Le processus est toujours en cours
                print(f"{Colors.WARNING}Arrêt de [{name}]...{Colors.ENDC}")
                if sys.platform == 'win32':
                    # Sur Windows, utiliser taskkill
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
                else:
                    # Sur Unix/Linux
                    process.terminate()
                    process.wait(timeout=5)
        except Exception as e:
            print(f"{Colors.RED}Erreur lors de l'arrêt de [{name}]: {str(e)}{Colors.ENDC}")
    
    print(f"{Colors.GREEN}Tous les processus ont été arrêtés.{Colors.ENDC}")

def ensure_directories():
    """Crée les répertoires nécessaires s'ils n'existent pas."""
    os.makedirs('logs', exist_ok=True)
    os.makedirs('web/logs', exist_ok=True)
    os.makedirs('web/data', exist_ok=True)
    os.makedirs('web/static', exist_ok=True)
    os.makedirs('web/templates', exist_ok=True)

def install_dependencies():
    """Installe les dépendances nécessaires."""
    dependencies = ['flask', 'pillow']
    
    for dependency in dependencies:
        try:
            print(f"{Colors.YELLOW}Vérification de {dependency}...{Colors.ENDC}")
            __import__(dependency.lower().replace('-', '_'))
            print(f"{Colors.GREEN}{dependency} est déjà installé.{Colors.ENDC}")
        except ImportError:
            print(f"{Colors.YELLOW}Installation de {dependency}...{Colors.ENDC}")
            try:
                # Utiliser le même interpréteur Python pour installer les dépendances
                subprocess.check_call([PYTHON_EXECUTABLE, '-m', 'pip', 'install', dependency])
                print(f"{Colors.GREEN}{dependency} installé avec succès.{Colors.ENDC}")
            except subprocess.CalledProcessError as e:
                print(f"{Colors.RED}Erreur lors de l'installation de {dependency}: {e}{Colors.ENDC}")
                if dependency.lower() == 'pillow':
                    print(f"{Colors.WARNING}L'interface fonctionnera sans le logo.{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}Dépendance critique manquante. Abandon.{Colors.ENDC}")
                    sys.exit(1)

def create_logo():
    """Crée le logo PNG si nécessaire."""
    if not os.path.exists('web/static/logo.png'):
        try:
            print(f"{Colors.BLUE}Génération du logo PNG...{Colors.ENDC}")
            # Utiliser le même interpréteur Python pour exécuter le script
            subprocess.check_call([PYTHON_EXECUTABLE, 'web/static/create_logo_png.py'])
            print(f"{Colors.GREEN}Logo généré avec succès.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.WARNING}Impossible de générer le logo PNG: {e}{Colors.ENDC}")
            print(f"{Colors.WARNING}L'interface fonctionnera sans logo.{Colors.ENDC}")

def create_favicon():
    """Crée le favicon si nécessaire."""
    if not os.path.exists('web/static/favicon.ico'):
        try:
            print(f"{Colors.BLUE}Génération du favicon...{Colors.ENDC}")
            
            # Vérifier si le script existe
            favicon_script = 'web/static/create_favicon.py'
            if not os.path.exists(favicon_script):
                print(f"{Colors.WARNING}Script de favicon non trouvé, création ignorée.{Colors.ENDC}")
                return False
                
            # Utiliser le même interpréteur Python pour exécuter le script
            subprocess.check_call([PYTHON_EXECUTABLE, favicon_script])
            print(f"{Colors.GREEN}Favicon généré avec succès.{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.WARNING}Impossible de générer le favicon: {e}{Colors.ENDC}")
            print(f"{Colors.WARNING}L'interface fonctionnera sans favicon.{Colors.ENDC}")
            return False
    return True

def check_templates():
    """Vérifie que tous les fichiers de templates nécessaires existent."""
    required_files = {
        'web/templates/index.html': "Template principal",
        'web/static/styles.css': "Feuille de style",
        'web/static/app.js': "Script JavaScript"
    }
    
    all_present = True
    for filepath, description in required_files.items():
        if not os.path.exists(filepath):
            print(f"{Colors.RED}Fichier requis manquant: {filepath} ({description}){Colors.ENDC}")
            all_present = False
    
    return all_present

def main():
    """Fonction principale."""
    try:
        # Configurer la fonction de nettoyage à exécuter à la sortie
        atexit.register(cleanup)
        
        # Afficher l'en-tête
        print_header()
        
        # Information sur l'environnement Python
        print(f"{Colors.GREEN}Utilisation de Python: {PYTHON_EXECUTABLE}{Colors.ENDC}")
        
        # Créer les répertoires nécessaires
        ensure_directories()
        
        # Installer les dépendances
        install_dependencies()
        
        # Générer les ressources statiques
        create_logo()
        create_favicon()
        
        # Vérifier les templates
        if not check_templates():
            print(f"{Colors.WARNING}Certains fichiers requis sont manquants. L'interface peut ne pas fonctionner correctement.{Colors.ENDC}")
        
        # Lancer les commandes
        threads = []
        for command in commands:
            thread = threading.Thread(target=run_command, args=(command,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            
            # Si spécifié, attendre que ce processus soit terminé avant de passer au suivant
            if command.get("wait", False):
                thread.join()
        
        # Afficher l'URL d'accès
        print(f"\n{Colors.GREEN}L'interface web est accessible à l'adresse : http://localhost:5000{Colors.ENDC}")
        print(f"{Colors.YELLOW}Appuyez sur Ctrl+C pour arrêter le serveur{Colors.ENDC}\n")
        
        # Attendre que tous les threads soient terminés
        for thread in threads:
            thread.join()
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interruption clavier détectée. Arrêt...{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Erreur inattendue: {str(e)}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main() 