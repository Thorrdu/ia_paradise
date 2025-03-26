from crewai import Agent, Task, Crew, Process
from langchain.tools import BaseTool
from langchain.llms import Ollama
import subprocess
import os
import json
import psutil
import torch

# Configuration de l'agent avec accélération GPU
ollama_llm = Ollama(
    model="mixtral",
    temperature=0.1,
    num_gpu=1,  # Utiliser le GPU
    num_thread=8  # Utiliser 8 threads CPU
)

# Outil pour exécuter des commandes système
class CommandTool(BaseTool):
    name = "command_tool"
    description = "Exécute des commandes système"
    
    def _run(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def _arun(self, command):
        return self._run(command)

# Outil pour gérer les fichiers
class FileTool(BaseTool):
    name = "file_tool"
    description = "Gère les fichiers (lecture, écriture, liste)"
    
    def _run(self, action, path, content=None):
        try:
            if action == "list":
                files = os.listdir(path)
                return '\n'.join(files)
            elif action == "read":
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif action == "write":
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"Fichier {path} écrit avec succès"
            else:
                return f"Action {action} non reconnue"
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def _arun(self, action, path, content=None):
        return self._run(action, path, content)

# Outil pour surveiller les ressources système
class SystemMonitorTool(BaseTool):
    name = "system_monitor_tool"
    description = "Surveille les ressources système (CPU, RAM, GPU)"
    
    def _run(self, query_type="all"):
        try:
            if query_type == "cpu" or query_type == "all":
                cpu_usage = psutil.cpu_percent(interval=1)
                cpu_info = {"usage": cpu_usage, "cores": psutil.cpu_count()}
                
            if query_type == "ram" or query_type == "all":
                ram = psutil.virtual_memory()
                ram_info = {
                    "total": f"{ram.total / (1024**3):.2f} GB",
                    "available": f"{ram.available / (1024**3):.2f} GB",
                    "percent": ram.percent
                }
                
            if query_type == "gpu" or query_type == "all":
                if torch.cuda.is_available():
                    gpu_info = {
                        "name": torch.cuda.get_device_name(0),
                        "available": True,
                        "memory_allocated": f"{torch.cuda.memory_allocated(0) / (1024**3):.2f} GB",
                        "memory_reserved": f"{torch.cuda.memory_reserved(0) / (1024**3):.2f} GB"
                    }
                else:
                    gpu_info = {"available": False}
            
            result = {}
            if query_type == "cpu" or query_type == "all":
                result["cpu"] = cpu_info
            if query_type == "ram" or query_type == "all":
                result["ram"] = ram_info
            if query_type == "gpu" or query_type == "all":
                result["gpu"] = gpu_info
                
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def _arun(self, query_type="all"):
        return self._run(query_type)

if __name__ == "__main__":
    print("🤖 Démarrage de l'Assistant IA...")
    
    # Vérifier si Ollama est installé et en cours d'exécution
    try:
        ollama_version = subprocess.run(["ollama", "version"], capture_output=True, text=True)
        print(f"✅ Ollama détecté: {ollama_version.stdout.strip()}")
    except:
        print("❌ Ollama n'est pas installé ou n'est pas dans le PATH")
        print("Veuillez installer Ollama depuis: https://ollama.com/download/windows")
        exit(1)
    
    # Vérifier si le modèle mixtral est disponible
    try:
        models = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "mixtral" not in models.stdout:
            print("⬇️ Le modèle mixtral n'est pas disponible. Téléchargement en cours...")
            subprocess.run(["ollama", "pull", "mixtral"], check=True)
        print("✅ Modèle mixtral disponible")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification/téléchargement du modèle: {str(e)}")
        exit(1)
    
    # Création de l'agent assistant système
    assistant = Agent(
        role="Assistant Système Avancé",
        goal="Aider à gérer l'ordinateur et automatiser des tâches complexes",
        backstory="Je suis un assistant IA puissant conçu pour l'automatisation et la gestion des tâches système sur un ordinateur haute performance.",
        verbose=True,
        tools=[CommandTool(), FileTool(), SystemMonitorTool()],
        llm=ollama_llm
    )
    
    # Menu interactif
    print("\n=== 🤖 ASSISTANT IA - MENU DES TÂCHES ===")
    print("1. Analyser les performances du système")
    print("2. Nettoyer les fichiers temporaires")
    print("3. Vérifier les mises à jour logicielles")
    print("4. Analyser l'utilisation du disque")
    print("5. Mode conversation libre")
    print("======================================")
    
    choice = input("Choisissez une option (1-5): ")
    
    if choice == "1":
        task = Task(
            description="Analyser les performances actuelles du système et générer un rapport complet incluant CPU, RAM, GPU, et recommandations d'optimisation.",
            expected_output="Rapport de performance du système",
            agent=assistant
        )
    elif choice == "2":
        task = Task(
            description="Identifier et nettoyer les fichiers temporaires qui prennent de l'espace inutilement sur le système.",
            expected_output="Rapport sur les fichiers nettoyés et l'espace libéré",
            agent=assistant
        )
    elif choice == "3":
        task = Task(
            description="Vérifier les mises à jour disponibles pour le système d'exploitation et les logiciels principaux installés.",
            expected_output="Liste des mises à jour disponibles",
            agent=assistant
        )
    elif choice == "4":
        task = Task(
            description="Analyser l'utilisation du disque et identifier les dossiers et fichiers qui occupent le plus d'espace.",
            expected_output="Rapport sur l'utilisation du disque",
            agent=assistant
        )
    elif choice == "5":
        user_query = input("\nQue souhaitez-vous demander à l'Assistant IA? ")
        task = Task(
            description=f"Répondre à la demande de l'utilisateur: {user_query}",
            expected_output="Réponse à la demande de l'utilisateur",
            agent=assistant
        )
    else:
        print("❌ Option invalide, utilisation de l'option 1 par défaut.")
        task = Task(
            description="Analyser les performances actuelles du système et générer un rapport.",
            expected_output="Rapport de performance du système",
            agent=assistant
        )
    
    # Création de l'équipe (Crew)
    crew = Crew(
        agents=[assistant],
        tasks=[task],
        verbose=2,
        process=Process.sequential  # Exécution séquentielle des tâches
    )
    
    # Exécution de l'équipe
    print("\n🚀 Exécution de la tâche... (cela peut prendre quelques minutes)")
    result = crew.kickoff()
    
    print("\n=== 📋 RÉSULTAT DE LA TÂCHE ===")
    print(result)
    print("===============================")
    
    input("\nAppuyez sur Entrée pour quitter...") 