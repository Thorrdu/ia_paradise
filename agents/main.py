import os
import logging
import time
from pathlib import Path

from .communication_inter_ia import CommunicationManager, MessagePriority
from .monitoring_agent import MonitoringAgent
from .dev_php_agent import PHPDevAgent
from .system_agent import SystemAgent

# Configuration des logs
def setup_logging():
    """Configure le système de logs."""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(logs_dir / "paradis_ia.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("ParadisIA")

def main():
    """Fonction principale pour lancer le système d'agents."""
    logger = setup_logging()
    logger.info("Démarrage du système d'agents Paradis IA V2")
    
    # Création du gestionnaire de communication
    comm_manager = CommunicationManager()
    logger.info("Gestionnaire de communication initialisé")
    
    # Création des agents
    monitoring_agent = MonitoringAgent("MonitoringAgent", comm_manager)
    php_agent = PHPDevAgent("PHPDevAgent", comm_manager)
    system_agent = SystemAgent("SystemAgent", comm_manager)
    
    agents = [monitoring_agent, php_agent, system_agent]
    logger.info(f"Agents créés: {[agent.name for agent in agents]}")
    
    # Test de communication inter-agents
    logger.info("Test de communication inter-agents")
    message = comm_manager.create_message(
        sender="SystemInitializer",
        recipient="MonitoringAgent",
        content="Démarrer le monitoring initial",
        priority=MessagePriority.HIGH
    )
    comm_manager.send_message(message)
    
    # Boucle principale
    try:
        logger.info("Démarrage de la boucle principale")
        while True:
            # Traitement des messages pour chaque agent
            for agent in agents:
                agent.process_messages()
            
            # Pause pour éviter de surcharger le CPU
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Arrêt du système demandé par l'utilisateur")
        
    finally:
        # Sauvegarde de l'état du système
        state_file = "config/system_state.json"
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        comm_manager.save_state(state_file)
        logger.info(f"État du système sauvegardé dans {state_file}")
        
        logger.info("Système arrêté")

if __name__ == "__main__":
    main() 