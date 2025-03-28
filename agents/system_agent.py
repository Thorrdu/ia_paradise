"""
Agent système pour la gestion des tâches système
"""

from crewai import Agent
from .tools import create_system_tool

def create_system_agent() -> Agent:
    """Crée et retourne l'agent système."""
    
    return Agent(
        role='Agent Système',
        goal='Gérer les tâches système et exécuter les commandes Windows',
        backstory="""Je suis un agent spécialisé dans l'exécution de tâches système sous Windows.
        Je peux exécuter des commandes, obtenir des informations système et gérer les processus.""",
        verbose=True,
        allow_delegation=False,
        tools=[create_system_tool()]
    ) 