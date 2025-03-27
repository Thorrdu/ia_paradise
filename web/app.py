#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Serveur web pour l'interface utilisateur de Paradis IA
Fournit des API REST pour interagir avec les agents et gérer les tâches
"""

import os
import sys
import logging
import datetime
import json
import threading
import time
from enum import Enum
from typing import Dict, List, Optional, Any, Union

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("web/logs/web_server.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("web_server")

# Mode limité par défaut
LIMITED_MODE = False

try:
    # Importer Flask et ses extensions
    from flask import Flask, jsonify, request, render_template, send_from_directory
    from flask_cors import CORS
    
    # Essayer d'importer nos modules personnalisés
    try:
        from api.llm.model_interface import create_model_interface, ModelConfig
        from api.communication import CommunicationManager, Priority, TaskStatus, Message, Task
        from memory.vector_db.simple_vector_store import SimpleVectorStore
        from agents.base_agent import BaseAgent
        
        # Essayer d'importer les agents spécialisés
        try:
            from agents.php_agent import PHPDevAgent
            has_php_agent = True
        except ImportError:
            has_php_agent = False
            logger.warning("Module PHPDevAgent non disponible")
        
        # Mode limité désactivé car tous les modules sont disponibles
        LIMITED_MODE = False
        logger.info("Tous les modules nécessaires sont disponibles, mode complet activé")
        
    except ImportError as e:
        logger.warning(f"Certains modules personnalisés ne sont pas disponibles: {e}")
        logger.warning("Activation du mode limité")
        LIMITED_MODE = True
        
except ImportError as e:
    logger.error(f"Impossible d'importer Flask ou ses extensions: {e}")
    logger.error("Le serveur web ne peut pas démarrer")
    sys.exit(1)

# Classes simulées pour le mode limité
if LIMITED_MODE:
    class Priority(Enum):
        """Niveaux de priorité pour les messages"""
        LOW = "LOW"
        MEDIUM = "MEDIUM"
        HIGH = "HIGH"
        URGENT = "URGENT"

    class TaskStatus(Enum):
        """Statuts possibles pour les tâches"""
        PENDING = "PENDING"
        IN_PROGRESS = "IN_PROGRESS"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"
        DELEGATED = "DELEGATED"
        
    class Message:
        """Représente un message simulé pour le mode limité"""
        def __init__(self, sender, recipient, content, priority=Priority.MEDIUM):
            self.sender = sender
            self.recipient = recipient
            self.content = content
            self.priority = priority
            self.timestamp = datetime.datetime.now().isoformat()
            self.message_id = f"msg-{int(time.time())}"
            
        def to_dict(self):
            return {
                "message_id": self.message_id,
                "sender": self.sender,
                "recipient": self.recipient,
                "content": self.content,
                "priority": self.priority.value,
                "timestamp": self.timestamp
            }
        
    class Task:
        """Représente une tâche simulée pour le mode limité"""
        def __init__(self, description, assigned_to, created_by, priority=Priority.MEDIUM):
            self.task_id = f"task-{int(time.time())}"
            self.description = description
            self.assigned_to = assigned_to
            self.created_by = created_by
            self.priority = priority
            self.status = TaskStatus.PENDING
            self.created_at = datetime.datetime.now().isoformat()
            
        def to_dict(self):
            return {
                "task_id": self.task_id,
                "description": self.description,
                "assigned_to": self.assigned_to,
                "created_by": self.created_by,
                "priority": self.priority.value,
                "status": self.status.value,
                "created_at": self.created_at
            }

# Variables globales
app = Flask(__name__)
CORS(app)

# Initialisation du système
def initialize_system():
    """Initialise le système selon le mode (normal ou limité)"""
    global comm_manager, agents, simulated_tasks, simulated_messages
    
    if not LIMITED_MODE:
        # Initialiser le gestionnaire de communication
        try:
            comm_manager = CommunicationManager()
            logger.info("Gestionnaire de communication initialisé")
            
            # Initialiser les agents
            agents = {}
            
            # Initialiser l'agent de base
            try:
                agents["BaseAgent"] = BaseAgent(
                    name="BaseAgent",
                    model_name="mixtral",
                    provider="ollama",
                    auto_initialize=True
                )
                logger.info("Agent de base initialisé")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation de l'agent de base: {e}")
            
            # Initialiser l'agent PHP si disponible
            if has_php_agent:
                try:
                    agents["PHPDevAgent"] = PHPDevAgent(
                        auto_initialize=True
                    )
                    logger.info("Agent PHP initialisé")
                except Exception as e:
                    logger.error(f"Erreur lors de l'initialisation de l'agent PHP: {e}")
            
            # Démarrer les agents
            for agent_name, agent in agents.items():
                try:
                    agent.start()
                    logger.info(f"Agent {agent_name} démarré")
                except Exception as e:
                    logger.error(f"Erreur lors du démarrage de l'agent {agent_name}: {e}")
            
            # Enregistrer les agents web et système
            comm_manager.register_agent(
                agent_name="WebInterface",
                capabilities=["user_interaction", "api"]
            )
            
            comm_manager.register_agent(
                agent_name="SystemAgent",
                capabilities=["system_management", "monitoring"]
            )
                    
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du système: {e}")
            logger.warning("Activation du mode limité en raison d'une erreur d'initialisation")
            initialize_limited_mode()
    else:
        # Initialiser le mode limité
        initialize_limited_mode()

def initialize_limited_mode():
    """Initialise le système en mode limité avec des données simulées"""
    global simulated_tasks, simulated_messages, simulated_agents
    
    logger.info("Initialisation du système en mode limité")
    
    # Créer des données simulées
    simulated_tasks = []
    simulated_messages = []
    simulated_agents = [
        {
            "name": "PHPDevAgent",
            "capabilities": ["php_development", "debugging", "optimization"],
            "last_seen": datetime.datetime.now().isoformat()
        },
        {
            "name": "SystemAgent",
            "capabilities": ["system_management", "monitoring"],
            "last_seen": datetime.datetime.now().isoformat()
        },
        {
            "name": "WebInterface",
            "capabilities": ["user_interaction", "api"],
            "last_seen": datetime.datetime.now().isoformat()
        }
    ]
    
    # Ajouter des tâches simulées
    task1 = Task(
        description="Analyser les logs d'erreurs PHP",
        assigned_to="PHPDevAgent",
        created_by="WebInterface",
        priority=Priority.URGENT
    )
    task1.status = TaskStatus.DELEGATED
    simulated_tasks.append(task1)
    
    task2 = Task(
        description="Surveiller l'utilisation système",
        assigned_to="SystemAgent",
        created_by="WebInterface",
        priority=Priority.MEDIUM
    )
    task2.status = TaskStatus.IN_PROGRESS
    simulated_tasks.append(task2)
    
    # Ajouter des messages simulés
    simulated_messages.append(
        Message(
            sender="WebInterface",
            recipient="PHPDevAgent",
            content="Analyse les erreurs dans le fichier log.php",
            priority=Priority.HIGH
        )
    )
    
    simulated_messages.append(
        Message(
            sender="PHPDevAgent",
            recipient="WebInterface",
            content="J'ai identifié plusieurs erreurs de syntaxe dans les fonctions de validation",
            priority=Priority.MEDIUM
        )
    )
    
    logger.info(f"Mode limité initialisé avec {len(simulated_tasks)} tâches et {len(simulated_messages)} messages")

# Initialiser le système
initialize_system()

# Routes API

# Routes existantes...

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Récupère la liste de tous les agents"""
    try:
        if LIMITED_MODE:
            return jsonify(simulated_agents)
        else:
            agents_data = comm_manager.get_all_agents()
            return jsonify(agents_data)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des agents: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Récupère la liste des tâches"""
    try:
        if LIMITED_MODE:
            tasks_data = [task.to_dict() for task in simulated_tasks]
            return jsonify(tasks_data)
        else:
            # Filtres optionnels
            assigned_to = request.args.get('assigned_to')
            status = request.args.get('status')
            
            tasks_data = comm_manager.get_tasks(
                assigned_to=assigned_to,
                status=status if not status else TaskStatus(status),
                limit=100
            )
            return jsonify(tasks_data)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tâches: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Récupère les détails d'une tâche spécifique"""
    try:
        if LIMITED_MODE:
            task = next((task for task in simulated_tasks if task.task_id == task_id), None)
            if task:
                return jsonify(task.to_dict())
            else:
                return jsonify({"error": "Tâche non trouvée"}), 404
        else:
            tasks = comm_manager.get_tasks(limit=100)
            task = next((task for task in tasks if task.get("task_id") == task_id), None)
            
            if task:
                return jsonify(task)
            else:
                return jsonify({"error": "Tâche non trouvée"}), 404
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la tâche {task_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Met à jour le statut d'une tâche"""
    try:
        data = request.json
        status = data.get('status')
        
        if not status:
            return jsonify({"error": "Statut non spécifié"}), 400
            
        if LIMITED_MODE:
            task = next((task for task in simulated_tasks if task.task_id == task_id), None)
            if task:
                try:
                    task.status = TaskStatus(status)
                    return jsonify({"success": True, "task_id": task_id, "status": status})
                except ValueError:
                    return jsonify({"error": "Statut invalide"}), 400
            else:
                return jsonify({"error": "Tâche non trouvée"}), 404
        else:
            result = comm_manager.update_task_status(task_id, status)
            
            if result:
                return jsonify({"success": True, "task_id": task_id, "status": status})
            else:
                return jsonify({"error": "Mise à jour impossible"}), 400
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la tâche {task_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/message', methods=['POST'])
def send_message():
    """Envoie un message à un agent"""
    try:
        data = request.json
        recipient = data.get('recipient')
        content = data.get('content')
        priority_value = data.get('priority', Priority.MEDIUM.value)
        metadata = data.get('metadata', {})
        create_task = data.get('create_task', False)
        
        if not recipient or not content:
            return jsonify({"error": "Destinataire et contenu requis"}), 400
            
        if LIMITED_MODE:
            # Mode limité - simuler l'envoi
            try:
                priority = Priority(priority_value)
            except ValueError:
                priority = Priority.MEDIUM
                
            message = Message(
                sender="WebInterface",
                recipient=recipient,
                content=content,
                priority=priority
            )
            simulated_messages.append(message)
            
            result = {"message_id": message.message_id}
            
            if create_task:
                task = Task(
                    description=content,
                    assigned_to=recipient,
                    created_by="WebInterface",
                    priority=priority
                )
                simulated_tasks.append(task)
                result["task_id"] = task.task_id
                
            return jsonify(result)
        else:
            # Mode normal - utiliser le gestionnaire de communication
            result = comm_manager.send_message(
                sender="WebInterface",
                recipient=recipient,
                content=content,
                priority=priority_value,
                metadata=metadata,
                create_task=create_task
            )
            
            return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Récupère les logs du système"""
    try:
        level = request.args.get('level', 'ALL')
        limit = int(request.args.get('limit', 100))
        
        log_file = "web/logs/web_server.log"
        
        if not os.path.exists(log_file):
            return jsonify(["Aucun log disponible"])
            
        # Filtrer par niveau de log si nécessaire
        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if level == 'ALL' or f" - {level} - " in line:
                    logs.append(line)
        
        # Prendre les dernières lignes correspondant à la limite
        logs = logs[-limit:]
        
        return jsonify(logs)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des logs: {e}")
        return jsonify(["Erreur lors de la récupération des logs"]), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Récupère les statistiques globales du système"""
    try:
        if LIMITED_MODE:
            return jsonify({
                "agents_count": len(simulated_agents),
                "active_tasks_count": len([t for t in simulated_tasks if t.status != TaskStatus.COMPLETED]),
                "messages_count": len(simulated_messages)
            })
        else:
            agents_count = len(comm_manager.get_all_agents())
            tasks = comm_manager.get_tasks(limit=1000)
            active_tasks_count = len([t for t in tasks if t.get("status") != TaskStatus.COMPLETED.value])
            
            return jsonify({
                "agents_count": agents_count,
                "active_tasks_count": active_tasks_count,
                "messages_count": len(comm_manager.messages)
            })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/activities', methods=['GET'])
def get_activities():
    """Récupère les activités récentes"""
    try:
        if LIMITED_MODE:
            # Simuler des activités
            activities = []
            
            # Activités basées sur les messages
            for msg in simulated_messages:
                activities.append({
                    "type": "message",
                    "timestamp": msg.timestamp,
                    "description": f"Message de {msg.sender} à {msg.recipient}",
                    "details": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                    "priority": msg.priority.value
                })
                
            # Trier par timestamp décroissant
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Limiter au nombre demandé
            return jsonify(activities[:10])
        else:
            activities = comm_manager.get_recent_activities(limit=10)
            return jsonify(activities)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des activités: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/system/stats', methods=['GET'])
def get_system_stats():
    """Récupère les statistiques système"""
    try:
        # Essayer d'utiliser psutil pour des statistiques réelles
        try:
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.5)
            
            # Mémoire
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disque
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Uptime
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            uptime_str = str(uptime).split('.')[0]  # Supprimer les microsecondes
            
            return jsonify({
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "uptime": uptime_str
            })
        except ImportError:
            # Simuler des statistiques si psutil n'est pas disponible
            import random
            
            return jsonify({
                "cpu_percent": random.randint(10, 70),
                "memory_percent": random.randint(30, 80),
                "disk_percent": random.randint(40, 90),
                "uptime": "1:23:45"
            })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques système: {e}")
        return jsonify({"error": str(e)}), 500

# Le reste du code existant...

# Point d'entrée principal
if __name__ == '__main__':
    # Afficher l'état du mode limité
    if LIMITED_MODE:
        logger.warning("Serveur web démarré en MODE LIMITÉ (fonctionnalités réduites)")
    else:
        logger.info("Serveur web démarré en mode complet")
    
    app.run(host='0.0.0.0', port=5000, debug=True)