"""
Module principal pour la génération du rapport de performance
"""

import subprocess
import os
from datetime import datetime

def execute_command(command: str) -> str:
    """Exécute une commande système et retourne le résultat."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='cp850'  # Encodage pour Windows en français
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Erreur lors de l'exécution de la commande : {result.stderr}"
            
    except Exception as e:
        return f"Erreur : {str(e)}"

def generate_performance_report() -> None:
    """Génère un rapport complet de performance système."""
    
    # Commandes pour collecter les informations système
    commands = {
        "Informations système": "systeminfo",
        "CPU": "wmic cpu get name,numberofcores,numberoflogicalprocessors",
        "Mémoire RAM": "wmic memorychip get capacity,speed",
        "GPU": "wmic path win32_VideoController get name,adapterram",
        "Disques": "wmic diskdrive get size,freespace",
        "Processus": "wmic process get caption,processid,workingsetsize /format:value",
        "Ports réseau": "netstat -ano | findstr LISTENING"
    }
    
    # Création du rapport
    report = []
    report.append("=== Rapport de Performance Système ===")
    report.append(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Exécution des commandes et collecte des résultats
    for title, command in commands.items():
        report.append(f"=== {title} ===")
        result = execute_command(command)
        report.append(result)
        report.append("\n")
    
    # Sauvegarde du rapport
    with open("rapport_performance.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    
    print("Rapport de performance généré avec succès dans 'rapport_performance.txt'")

if __name__ == "__main__":
    generate_performance_report() 