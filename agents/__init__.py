"""
Package agents pour la gestion des agents IA
"""

from .main import create_crew, generate_performance_report
from .system_agent import create_system_agent
from .file_agent import create_file_agent

__all__ = ['create_crew', 'generate_performance_report', 'create_system_agent', 'create_file_agent']

"""
Module d'agents pour Paradis IA
Fournit les classes de base et les implémentations des agents spécialisés
""" 