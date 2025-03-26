from typing import Dict, Any, Optional
import json
import os
from langchain_ollama import OllamaLLM
from langchain.tools import BaseTool

class ModelCommunicator:
    def __init__(self):
        # Initialisation des différents modèles avec leurs spécialités
        self.models = {
            "general": OllamaLLM(model="mixtral-optimized", temperature=0.1),
            "code": OllamaLLM(model="deepseek-coder:33b-instruct-q5_K_M", temperature=0.1),
            "system": OllamaLLM(model="dolphin-mixtral", temperature=0.1)
        }
        
        # ... reste du code inchangé ...

class FileSystemTool(BaseTool):
    name: str = "file_system_tool"
    description: str = "Gère les opérations sur les fichiers (création, lecture, modification)"
    return_direct: bool = True
    
    def _run(self, action: str, path: str, content: Optional[str] = None) -> str:
        try:
            if action == "create":
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"Fichier {path} créé avec succès"
            elif action == "read":
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif action == "append":
                with open(path, 'a', encoding='utf-8') as f:
                    f.write(content)
                return f"Contenu ajouté à {path} avec succès"
            else:
                return f"Action {action} non reconnue"
        except Exception as e:
            return f"Erreur : {str(e)}"
    
    def _arun(self, action: str, path: str, content: Optional[str] = None) -> str:
        return self._run(action, path, content)