"""
Agent pour la gestion des fichiers
"""

from crewai import Agent
from crewai_tools import FileReadTool, FileWriterTool

def create_file_agent() -> Agent:
    """Crée et retourne l'agent de gestion des fichiers."""
    
    return Agent(
        role='Agent Fichiers',
        goal='Gérer la lecture et l\'écriture des fichiers',
        backstory="""Je suis un agent spécialisé dans la manipulation des fichiers.
        Je peux lire et écrire des fichiers de manière sécurisée.""",
        verbose=True,
        allow_delegation=False,
        tools=[FileReadTool(), FileWriterTool()]
    ) 