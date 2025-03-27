#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test pour la nouvelle architecture de Paradis IA
Ce script teste les composants de base: interface LLM, communication et agents
"""

import os
import time
import logging
from typing import Dict, Any

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_architecture")

# Créer les répertoires nécessaires
os.makedirs("memory/data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Import des composants
try:
    from api.llm.model_interface import create_model_interface
    from api.communication import CommunicationManager, Priority
    from memory.vector_db.simple_vector_store import SimpleVectorStore
    from agents.base_agent import BaseAgent
    
    # Si disponible, importer aussi l'agent PHP
    try:
        from agents.php_agent import PHPDevAgent
        has_php_agent = True
    except ImportError:
        has_php_agent = False
        logger.warning("Module PHPDevAgent non disponible")
    
except ImportError as e:
    logger.error(f"Impossible d'importer un module requis: {e}")
    exit(1)

def test_model_interface() -> bool:
    """Teste l'interface du modèle LLM"""
    logger.info("Test de l'interface du modèle LLM")
    
    try:
        # Créer l'interface du modèle
        model = create_model_interface(
            model_name="mixtral",
            provider="ollama",
            system_prompt="Tu es un assistant utile et concis."
        )
        
        # Tester la génération de texte
        response = model.generate("Bonjour, comment vas-tu?")
        
        if "response" in response:
            logger.info(f"Réponse du modèle: {response['response'][:50]}...")
            return True
        else:
            logger.error(f"Réponse du modèle incorrecte: {response}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors du test de l'interface du modèle: {e}")
        return False

def test_vector_store() -> bool:
    """Teste le stockage vectoriel"""
    logger.info("Test du stockage vectoriel")
    
    try:
        # Créer un stockage vectoriel de test
        store = SimpleVectorStore("test_store")
        
        # Ajouter un document (avec un embedding simplifié)
        doc_id = store.add(
            document="Ceci est un document de test pour Paradis IA.",
            embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
            metadata={"type": "test", "author": "Paradis IA"}
        )
        
        # Rechercher un document (avec un embedding simplifié)
        results = store.search(
            query_embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
            top_k=1
        )
        
        if results and len(results) > 0:
            logger.info(f"Document trouvé: {results[0]['document'][:30]}...")
            
            # Nettoyer après le test
            store.clear()
            return True
        else:
            logger.error("Aucun document trouvé")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors du test du stockage vectoriel: {e}")
        return False

def test_communication() -> bool:
    """Teste le système de communication"""
    logger.info("Test du système de communication")
    
    try:
        # Créer un gestionnaire de communication
        comm_manager = CommunicationManager()
        
        # Enregistrer des agents de test
        comm_manager.register_agent(
            agent_name="TestAgent1",
            capabilities=["test", "communication"]
        )
        
        comm_manager.register_agent(
            agent_name="TestAgent2",
            capabilities=["test", "response"]
        )
        
        # Envoyer un message
        result = comm_manager.send_message(
            sender="TestAgent1",
            recipient="TestAgent2",
            content="Ceci est un message de test.",
            priority=Priority.MEDIUM
        )
        
        if "message_id" in result:
            logger.info(f"Message envoyé avec ID: {result['message_id']}")
            
            # Récupérer les messages
            messages = comm_manager.get_messages_for_agent("TestAgent2")
            
            if messages and len(messages) > 0:
                logger.info(f"Message reçu: {messages[0]['content']}")
                
                # Créer une tâche
                task = comm_manager.create_task(
                    description="Tâche de test",
                    assigned_to="TestAgent2",
                    created_by="TestAgent1",
                    priority=Priority.MEDIUM
                )
                
                if task and task.task_id:
                    logger.info(f"Tâche créée avec ID: {task.task_id}")
                    return True
                else:
                    logger.error("Erreur lors de la création de la tâche")
                    return False
            else:
                logger.error("Aucun message reçu")
                return False
        else:
            logger.error("Erreur lors de l'envoi du message")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors du test du système de communication: {e}")
        return False

def test_base_agent() -> bool:
    """Teste l'agent de base"""
    logger.info("Test de l'agent de base")
    
    try:
        # Créer un agent de base
        agent = BaseAgent(
            name="TestBaseAgent",
            model_name="mixtral",
            provider="ollama",
            auto_initialize=True
        )
        
        # Vérifier l'initialisation
        if agent.llm and agent.comm_manager and agent.vector_store:
            logger.info("Agent initialisé avec succès")
            
            # Vérifier le statut
            status = agent.get_status()
            logger.info(f"Statut de l'agent: {status}")
            
            return True
        else:
            logger.error("Erreur lors de l'initialisation de l'agent")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors du test de l'agent de base: {e}")
        return False

def test_php_agent() -> bool:
    """Teste l'agent PHP"""
    if not has_php_agent:
        logger.warning("Test de l'agent PHP ignoré: module non disponible")
        return False
    
    logger.info("Test de l'agent PHP")
    
    try:
        # Créer un agent PHP
        php_agent = PHPDevAgent(
            auto_initialize=True
        )
        
        # Vérifier l'initialisation
        if php_agent.llm and php_agent.comm_manager and php_agent.vector_store:
            logger.info("Agent PHP initialisé avec succès")
            
            # Tester l'analyse d'erreur PHP
            error_log = (
                "PHP Fatal error: Uncaught Error: Call to undefined function mysql_connect() "
                "in /var/www/html/example.php:25"
            )
            
            analysis = php_agent.analyze_php_error(error_log)
            
            if analysis and analysis["error_identified"]:
                logger.info(f"Analyse d'erreur PHP: {analysis['error_type']}")
                return True
            else:
                logger.error("Erreur lors de l'analyse PHP")
                return False
        else:
            logger.error("Erreur lors de l'initialisation de l'agent PHP")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors du test de l'agent PHP: {e}")
        return False

def run_tests() -> Dict[str, bool]:
    """Exécute tous les tests et retourne les résultats"""
    results = {}
    
    # Tester l'interface du modèle
    results["model_interface"] = test_model_interface()
    
    # Tester le stockage vectoriel
    results["vector_store"] = test_vector_store()
    
    # Tester le système de communication
    results["communication"] = test_communication()
    
    # Tester l'agent de base
    results["base_agent"] = test_base_agent()
    
    # Tester l'agent PHP si disponible
    if has_php_agent:
        results["php_agent"] = test_php_agent()
    
    return results

if __name__ == "__main__":
    logger.info("Démarrage des tests de la nouvelle architecture")
    
    # Exécuter les tests
    results = run_tests()
    
    # Afficher les résultats
    logger.info("\n\n=== RÉSULTATS DES TESTS ===")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "SUCCÈS" if passed else "ÉCHEC"
        logger.info(f"{test_name}: {status}")
        
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("\nTous les tests ont réussi!")
        exit(0)
    else:
        logger.error("\nCertains tests ont échoué.")
        exit(1) 