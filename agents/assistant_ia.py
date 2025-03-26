from crewai import Agent, Task, Crew, Process
from langchain.tools import BaseTool
from langchain.llms import Ollama
import subprocess
import os
import json
import psutil
import torch
import requests
import socket
import argparse

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

# Outil pour la navigation web
class WebBrowserTool(BaseTool):
    name = "web_browser_tool"
    description = "Navigue sur le web et récupère des informations"
    
    def _run(self, url, action="get"):
        try:
            if action == "get":
                response = requests.get(url, timeout=10)
                return response.text
            else:
                return f"Action {action} non supportée"
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def _arun(self, url, action="get"):
        return self._run(url, action)

# Outil pour les connexions socket directes
class SocketTool(BaseTool):
    name = "socket_tool"
    description = "Établit des connexions socket directes"
    
    def _run(self, host, port, data=None):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                if data:
                    s.sendall(data.encode())
                return s.recv(1024).decode()
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def _arun(self, host, port, data=None):
        return self._run(host, port, data)

# Outil pour les requêtes API
class APIGatewayTool(BaseTool):
    name = "api_gateway_tool"
    description = "Effectue des requêtes API sécurisées"
    
    def _run(self, url, method="GET", data=None, headers=None):
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                timeout=10
            )
            return response.json()
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def _arun(self, url, method="GET", data=None, headers=None):
        return self._run(url, method, data, headers)

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

def main():
    parser = argparse.ArgumentParser(description='Assistant IA avec mode collaboration')
    parser.add_argument('--mode', choices=['system', 'collaboration'], default='system',
                      help='Mode de fonctionnement (system ou collaboration)')
    parser.add_argument('--task', type=str, help='Tâche à exécuter en mode collaboration')
    args = parser.parse_args()

    # Création des outils
    tools = [
        CommandTool(),
        FileTool(),
        SystemMonitorTool(),
        WebBrowserTool(),
        SocketTool(),
        APIGatewayTool()
    ]

    if args.mode == 'system':
        # Mode système standard
        assistant = Agent(
            role="Assistant Système Avancé",
            goal="Aider à gérer l'ordinateur et automatiser des tâches complexes",
            backstory="Je suis un assistant IA puissant conçu pour l'automatisation et la gestion des tâches système sur un ordinateur haute performance.",
            verbose=True,
            tools=tools,
            llm=ollama_llm
        )

        task = Task(
            description="Analyser les performances actuelles du système et générer un rapport",
            expected_output="Rapport de performance du système",
            agent=assistant
        )

        crew = Crew(
            agents=[assistant],
            tasks=[task],
            verbose=2,
            process=Process.sequential
        )

        result = crew.kickoff()
        print(result)

    else:  # Mode collaboration
        # Agent principal
        main_assistant = Agent(
            role="Assistant Principal",
            goal="Coordonner les tâches et gérer la collaboration entre les agents",
            backstory="Je suis l'assistant principal qui coordonne les différents agents spécialisés.",
            verbose=True,
            tools=tools,
            llm=ollama_llm
        )

        # Agent spécialisé web
        web_assistant = Agent(
            role="Assistant Web",
            goal="Gérer les interactions web et les requêtes API",
            backstory="Je suis spécialisé dans la navigation web et les interactions API.",
            verbose=True,
            tools=[WebBrowserTool(), APIGatewayTool()],
            llm=ollama_llm
        )

        # Agent spécialisé système
        system_assistant = Agent(
            role="Assistant Système",
            goal="Gérer les tâches système et la gestion des fichiers",
            backstory="Je suis spécialisé dans la gestion du système et des fichiers.",
            verbose=True,
            tools=[CommandTool(), FileTool(), SystemMonitorTool()],
            llm=ollama_llm
        )

        # Création des tâches en fonction de la demande
        tasks = []
        if args.task:
            tasks.append(Task(
                description=args.task,
                expected_output="Résultat de la tâche demandée",
                agent=main_assistant
            ))

        # Création de l'équipe en mode collaboration
        crew = Crew(
            agents=[main_assistant, web_assistant, system_assistant],
            tasks=tasks,
            verbose=2,
            process=Process.sequential
        )

        result = crew.kickoff()
        print(result)

if __name__ == "__main__":
    main()