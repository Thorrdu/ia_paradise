#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Serveur web Flask pour l'interface de gestion de Paradis IA.
"""

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory

# Configuration du logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'web_server.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('web_server')

# Création de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Mode limité (sans les modules Paradis IA)
LIMITED_MODE = False

# Variables globales
communication_manager = None
system_agent = None
web_agent = None
agents_registry = {}

# Initialisation des répertoires
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Ajouter le répertoire parent au path pour les imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import des modules du projet Paradis IA
try:
    from agents.communication_inter_ia import CommunicationManager, Message, Priority, TaskStatus, Task
    from agents.system_agent import SystemAgent
    from agents.web_communication_agent import WebCommunicationAgent
except ImportError as e:
    logger.warning(f"Fonctionnement en mode limité: {e}")
    logger.warning("L'interface web fonctionnera avec des données simulées")
    LIMITED_MODE = True
    
    # Définition des classes simulées pour le mode limité
    class Priority:
        LOW = "LOW"
        MEDIUM = "MEDIUM"
        HIGH = "HIGH"
        URGENT = "URGENT"
    
    class TaskStatus:
        PENDING = "PENDING"
        IN_PROGRESS = "IN_PROGRESS"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"
        DELEGATED = "DELEGATED"
    
    class Message:
        def __init__(self, sender, recipient, content, priority, metadata=None):
            self.sender = sender
            self.recipient = recipient
            self.content = content
            self.priority = priority
            self.metadata = metadata or {}
    
    class Task:
        def __init__(self, description, assigned_agent, status, priority, created_at=None, deadline=None):
            self.description = description
            self.assigned_agent = assigned_agent
            self.status = status
            self.priority = priority
            self.created_at = created_at or datetime.now()
            self.deadline = deadline


def initialize_system():
    """Initialise le système d'agents et le gestionnaire de communication."""
    global communication_manager, system_agent, web_agent, LIMITED_MODE
    
    if LIMITED_MODE:
        logger.info("Initialisation en mode limité (démonstration)")
        
        # Créer des données de démonstration
        global agents_registry
        agents_registry = {
            "PHPDevAgent": ["php_development", "code_generation", "code_review", "bug_fixing"],
            "SystemAgent": ["system_monitoring", "resource_management", "process_control"],
            "WebAgent": ["web_server", "api_gateway", "webhook_handler"],
            "MonitoringAgent": ["monitoring", "alerts", "performance_tracking"]
        }
        
        # Lancer le thread de mise à jour simulée
        threading.Thread(target=simulated_updates, daemon=True).start()
        
        return True
    
    try:
        logger.info("Initialisation du système de communication...")
        communication_manager = CommunicationManager()
        
        # Création de l'agent système
        logger.info("Création de l'agent système...")
        system_agent = SystemAgent("SystemAgent", communication_manager)
        
        # Création de l'agent web
        logger.info("Création de l'agent web...")
        web_agent = WebCommunicationAgent("WebAgent", communication_manager)
        
        # Chargement des états précédents si disponibles
        state_file = Path('data/communication_state.json')
        if state_file.exists():
            try:
                logger.info("Chargement de l'état précédent...")
                communication_manager.load_state(str(state_file))
                logger.info("État chargé avec succès.")
            except Exception as e:
                logger.error(f"Erreur lors du chargement de l'état: {e}")
        
        # Lancer les threads de monitoring
        threading.Thread(target=monitor_system, daemon=True).start()
        threading.Thread(target=save_state_periodically, daemon=True).start()
        
        logger.info("Système initialisé avec succès")
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du système: {e}")
        logger.warning("Passage en mode limité (démonstration)")
        LIMITED_MODE = True
        
        # Initialiser les données simulées
        initialize_system()
        
        return True


# Fonction de simulation pour le mode limité
simulated_tasks = {}
simulated_messages = {}
simulated_stats = {
    "agents_count": 4,
    "tasks_count": 5,
    "active_tasks_count": 3,
    "messages_count": 12,
    "cpu_percent": 35,
    "memory_percent": 42,
    "disk_percent": 68,
    "uptime": "2h 15m"
}

def create_simulated_data():
    """Crée des données simulées pour le mode démonstration."""
    global simulated_tasks, simulated_messages
    
    # Créer des tâches de démonstration
    simulated_tasks = {
        "task-001": {
            "id": "task-001",
            "description": "Générer un contrôleur PHP pour l'API utilisateurs",
            "status": TaskStatus.COMPLETED,
            "assigned_agent": "PHPDevAgent",
            "priority": Priority.HIGH,
            "created_at": datetime.now() - timedelta(hours=2),
            "deadline": None
        },
        "task-002": {
            "id": "task-002",
            "description": "Optimiser l'utilisation mémoire du système",
            "status": TaskStatus.IN_PROGRESS,
            "assigned_agent": "SystemAgent",
            "priority": Priority.MEDIUM,
            "created_at": datetime.now() - timedelta(hours=1),
            "deadline": None
        },
        "task-003": {
            "id": "task-003",
            "description": "Configurer les webhooks pour GitHub",
            "status": TaskStatus.PENDING,
            "assigned_agent": "WebAgent",
            "priority": Priority.LOW,
            "created_at": datetime.now() - timedelta(minutes=30),
            "deadline": None
        },
        "task-004": {
            "id": "task-004",
            "description": "Surveiller les performances GPU",
            "status": TaskStatus.PENDING,
            "assigned_agent": "MonitoringAgent",
            "priority": Priority.MEDIUM,
            "created_at": datetime.now() - timedelta(minutes=15),
            "deadline": None
        },
        "task-005": {
            "id": "task-005",
            "description": "Analyser les logs d'erreurs PHP",
            "status": TaskStatus.DELEGATED,
            "assigned_agent": "PHPDevAgent",
            "priority": Priority.URGENT,
            "created_at": datetime.now() - timedelta(minutes=5),
            "deadline": datetime.now() + timedelta(hours=2)
        }
    }
    
    # Créer des messages de démonstration
    for agent in agents_registry:
        simulated_messages[agent] = []
    
    simulated_messages["PHPDevAgent"] = [
        Message("SystemAgent", "PHPDevAgent", "Nécessité d'optimiser le code PHP", Priority.MEDIUM),
        Message("WebAgent", "PHPDevAgent", "Besoin d'une API pour les utilisateurs", Priority.HIGH),
    ]
    
    simulated_messages["SystemAgent"] = [
        Message("PHPDevAgent", "SystemAgent", "Problème de mémoire détecté", Priority.HIGH),
        Message("MonitoringAgent", "SystemAgent", "Alerte: utilisation CPU élevée", Priority.URGENT),
    ]
    
    simulated_messages["WebAgent"] = [
        Message("SystemAgent", "WebAgent", "Configuration des webhooks requise", Priority.LOW),
    ]
    
    simulated_messages["MonitoringAgent"] = [
        Message("SystemAgent", "MonitoringAgent", "Demande de surveillance GPU", Priority.MEDIUM),
    ]


def simulated_updates():
    """Simule des mises à jour périodiques pour le mode limité."""
    global simulated_stats, simulated_tasks
    
    # Initialiser les données simulées
    create_simulated_data()
    
    # Boucle de mise à jour
    while True:
        # Varier aléatoirement les statistiques
        import random
        simulated_stats["cpu_percent"] = max(5, min(95, simulated_stats["cpu_percent"] + random.randint(-5, 5)))
        simulated_stats["memory_percent"] = max(10, min(90, simulated_stats["memory_percent"] + random.randint(-3, 3)))
        simulated_stats["disk_percent"] = max(20, min(95, simulated_stats["disk_percent"] + random.randint(-1, 1)))
        
        # Mettre à jour périodiquement le statut des tâches
        for task_id, task in simulated_tasks.items():
            if task["status"] == TaskStatus.IN_PROGRESS and random.random() < 0.2:
                task["status"] = TaskStatus.COMPLETED
            elif task["status"] == TaskStatus.PENDING and random.random() < 0.1:
                task["status"] = TaskStatus.IN_PROGRESS
        
        # Attendre avant la prochaine mise à jour
        time.sleep(10)


def monitor_system():
    """Surveille périodiquement le système et collecte des statistiques."""
    while True:
        try:
            # Vérifier l'état des agents
            update_agents_registry()
            
            # Attendre avant la prochaine vérification
            time.sleep(30)
        except Exception as e:
            logger.error(f"Erreur dans le thread de monitoring: {e}")
            time.sleep(60)  # Attendre plus longtemps en cas d'erreur


def save_state_periodically():
    """Sauvegarde périodiquement l'état du système."""
    while True:
        try:
            if communication_manager:
                logger.info("Sauvegarde de l'état du système...")
                communication_manager.save_state('data/communication_state.json')
            time.sleep(300)  # Toutes les 5 minutes
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'état: {e}")
            time.sleep(60)


def update_agents_registry():
    """Met à jour le registre des agents."""
    global agents_registry
    
    if LIMITED_MODE:
        return  # Déjà initialisé en mode limité
    
    if not communication_manager:
        return
    
    try:
        # Récupérer la liste des agents enregistrés
        agents_registry = communication_manager.agents_registry
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du registre des agents: {e}")


@app.route('/')
def index():
    """Route principale qui affiche l'interface web."""
    return render_template('index.html')


@app.route('/static/<path:path>')
def serve_static(path):
    """Sert les fichiers statiques."""
    return send_from_directory('static', path)


@app.route('/api/agents')
def get_agents():
    """Renvoie la liste des agents enregistrés."""
    if LIMITED_MODE:
        # Données simulées en mode limité
        agents = []
        for agent_name, capabilities in agents_registry.items():
            agents.append({
                "name": agent_name,
                "capabilities": capabilities
            })
        return jsonify(agents)
        
    if not communication_manager:
        return jsonify({"error": "Le système n'est pas initialisé"}), 500
    
    agents = []
    for agent_name, capabilities in agents_registry.items():
        agents.append({
            "name": agent_name,
            "capabilities": capabilities
        })
    
    return jsonify(agents)


@app.route('/api/tasks')
def get_tasks():
    """Renvoie la liste des tâches en cours."""
    if LIMITED_MODE:
        # Données simulées en mode limité
        tasks = []
        for task_id, task in simulated_tasks.items():
            tasks.append({
                "id": task["id"],
                "description": task["description"],
                "status": task["status"],
                "assigned_to": task["assigned_agent"],
                "priority": task["priority"],
                "created_at": task["created_at"].isoformat(),
                "deadline": task["deadline"].isoformat() if task["deadline"] else None
            })
        
        # Trier par date de création (plus récent en premier)
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return jsonify(tasks)
    
    if not communication_manager:
        return jsonify({"error": "Le système n'est pas initialisé"}), 500
    
    tasks = []
    for task_id, task in communication_manager.tasks.items():
        tasks.append({
            "id": task_id,
            "description": task.description,
            "status": task.status.name if isinstance(task.status, TaskStatus) else task.status,
            "assigned_to": task.assigned_agent,
            "priority": task.priority.name if hasattr(task.priority, 'name') else task.priority,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "deadline": task.deadline.isoformat() if task.deadline else None
        })
    
    # Trier par date de création (plus récent en premier)
    tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return jsonify(tasks)


@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Met à jour le statut d'une tâche."""
    if LIMITED_MODE:
        # Mode simulé
        data = request.json
        if not data or 'status' not in data:
            return jsonify({"error": "Le statut est requis"}), 400
        
        status = data['status']
        if task_id in simulated_tasks:
            simulated_tasks[task_id]["status"] = status
            logger.info(f"Tâche {task_id} mise à jour - Nouveau statut: {status}")
            return jsonify({
                "success": True,
                "message": f"Statut de la tâche {task_id} mis à jour: {status}"
            })
        else:
            return jsonify({"error": f"Tâche {task_id} non trouvée"}), 404
    
    if not communication_manager:
        return jsonify({"error": "Le système n'est pas initialisé"}), 500
    
    data = request.json
    if not data or 'status' not in data:
        return jsonify({"error": "Le statut est requis"}), 400
    
    try:
        status = data['status']
        if task_id in communication_manager.tasks:
            task = communication_manager.tasks[task_id]
            task.status = getattr(TaskStatus, status) if hasattr(TaskStatus, status) else status
            
            # Journaliser le changement
            logger.info(f"Tâche {task_id} mise à jour - Nouveau statut: {status}")
            
            return jsonify({
                "success": True,
                "message": f"Statut de la tâche {task_id} mis à jour: {status}"
            })
        else:
            return jsonify({"error": f"Tâche {task_id} non trouvée"}), 404
    
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la tâche {task_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/message', methods=['POST'])
def send_message():
    """Envoie un message à un agent."""
    if LIMITED_MODE:
        # Mode simulé
        data = request.json
        if not data or 'recipient' not in data or 'content' not in data:
            return jsonify({"error": "Destinataire et contenu requis"}), 400
        
        sender = data.get('sender', 'WebInterface')
        recipient = data['recipient']
        content = data['content']
        priority_str = data.get('priority', 'MEDIUM')
        metadata = data.get('metadata', {})
        create_task = data.get('create_task', False)
        
        # Conversion de la priorité
        priority = getattr(Priority, priority_str) if hasattr(Priority, priority_str) else Priority.MEDIUM
        
        # Créer le message
        message = Message(sender, recipient, content, priority, metadata)
        
        # Ajouter le message à la liste simulée
        if recipient in simulated_messages:
            simulated_messages[recipient].append(message)
        
        # Créer une tâche si demandé
        task_id = None
        if create_task:
            task_id = f"task-{len(simulated_tasks) + 1:03d}"
            simulated_tasks[task_id] = {
                "id": task_id,
                "description": content[:100] + ("..." if len(content) > 100 else ""),
                "status": TaskStatus.PENDING,
                "assigned_agent": recipient,
                "priority": priority,
                "created_at": datetime.now(),
                "deadline": datetime.now() + timedelta(days=1) if priority_str == 'URGENT' else None
            }
        
        return jsonify({
            "success": True,
            "message_id": f"msg-{int(time.time())}",
            "task_id": task_id
        })
    
    if not communication_manager:
        return jsonify({"error": "Le système n'est pas initialisé"}), 500
    
    data = request.json
    if not data or 'recipient' not in data or 'content' not in data:
        return jsonify({"error": "Destinataire et contenu requis"}), 400
    
    try:
        # Préparer les données du message
        sender = data.get('sender', 'WebInterface')
        recipient = data['recipient']
        content = data['content']
        priority_str = data.get('priority', 'MEDIUM')
        metadata = data.get('metadata', {})
        create_task = data.get('create_task', False)
        
        # Convertir la priorité en enum
        priority = getattr(Priority, priority_str) if hasattr(Priority, priority_str) else Priority.MEDIUM
        
        # Créer et envoyer le message
        message = Message(
            sender=sender,
            recipient=recipient,
            content=content,
            priority=priority,
            metadata=metadata
        )
        
        message_id = communication_manager.send_message(message)
        logger.info(f"Message envoyé: {sender} -> {recipient} (ID: {message_id})")
        
        # Si demandé, créer une tâche associée
        task_id = None
        if create_task:
            task = Task(
                description=content[:100] + ("..." if len(content) > 100 else ""),
                assigned_agent=recipient,
                status=TaskStatus.PENDING,
                priority=priority,
                created_at=datetime.now(),
                deadline=datetime.now() + timedelta(days=1) if 'URGENT' in priority_str else None
            )
            task_id = communication_manager.create_task(task)
            logger.info(f"Tâche créée: {task_id} pour {recipient}")
        
        return jsonify({
            "success": True,
            "message_id": message_id,
            "task_id": task_id
        })
    
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/logs')
def get_logs():
    """Récupère les entrées récentes du journal des logs."""
    try:
        log_file = os.path.join('logs', 'web_server.log')
        level_filter = request.args.get('level', 'ALL').upper()
        limit = min(int(request.args.get('limit', 100)), 1000)  # Maximum 1000 lignes
        
        if not os.path.exists(log_file):
            return jsonify([])
        
        # Lire les dernières lignes du fichier de log
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-limit:]
        
        # Filtrer par niveau si nécessaire
        if level_filter != 'ALL':
            lines = [line for line in lines if f' - {level_filter} - ' in line]
        
        return jsonify(lines)
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des logs: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/system/stats')
def get_system_stats():
    """Récupère les statistiques système."""
    if LIMITED_MODE:
        # Mode simulé
        return jsonify({
            "cpu_percent": simulated_stats["cpu_percent"],
            "memory_percent": simulated_stats["memory_percent"],
            "disk_percent": simulated_stats["disk_percent"],
            "uptime": simulated_stats["uptime"]
        })
    
    if not system_agent:
        return jsonify({"error": "L'agent système n'est pas initialisé"}), 500
    
    try:
        # Créer un message pour demander les statistiques système
        message = Message(
            sender="WebInterface",
            recipient="SystemAgent",
            content="monitor system",
            priority=Priority.HIGH,
            metadata={"action": "monitor"}
        )
        
        # Envoyer le message
        communication_manager.send_message(message)
        
        # Attendre et récupérer la réponse
        start_time = time.time()
        while time.time() - start_time < 5:  # Timeout de 5 secondes
            messages = communication_manager.get_messages("WebInterface")
            for msg in messages:
                if msg.sender == "SystemAgent" and "system_info" in msg.metadata:
                    return jsonify(msg.metadata.get("system_info", {}))
            time.sleep(0.1)
        
        # Si aucune réponse n'est reçue après le timeout
        return jsonify({
            "cpu_percent": 0,
            "memory_percent": 0,
            "disk_percent": 0,
            "uptime": "Indisponible",
            "error": "Timeout en attente de réponse"
        })
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques système: {e}")
        return jsonify({
            "cpu_percent": 0,
            "memory_percent": 0,
            "disk_percent": 0,
            "uptime": "Erreur",
            "error": str(e)
        })


@app.route('/api/activities')
def get_activities():
    """Récupère les activités récentes."""
    if LIMITED_MODE:
        # Mode simulé
        activities = []
        
        # Messages récents
        for agent_name, messages in simulated_messages.items():
            for msg in messages:
                activities.append({
                    "type": "message",
                    "timestamp": datetime.now().isoformat(),
                    "description": f"Message de {msg.sender} à {msg.recipient}",
                    "details": msg.content[:100] + ("..." if len(msg.content) > 100 else "")
                })
        
        # Tâches récentes
        for task_id, task in simulated_tasks.items():
            activities.append({
                "type": "task",
                "timestamp": task["created_at"].isoformat(),
                "description": f"Tâche {task_id} ({task['status']})",
                "details": task["description"]
            })
        
        # Trier par timestamp
        activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Limiter à 20 activités
        return jsonify(activities[:20])
    
    if not communication_manager:
        return jsonify({"error": "Le système n'est pas initialisé"}), 500
    
    try:
        # Récupérer les 10 derniers messages émis
        activities = []
        
        # Messages récents (convertis en activités)
        for agent_name in agents_registry.keys():
            messages = communication_manager.get_messages(agent_name, max_count=5)
            for msg in messages:
                activities.append({
                    "type": "message",
                    "timestamp": datetime.now().isoformat(),  # Approximatif, car Message n'a pas de timestamp
                    "description": f"Message de {msg.sender} à {msg.recipient}",
                    "details": msg.content[:100] + ("..." if len(msg.content) > 100 else "")
                })
        
        # Tâches récentes
        for task_id, task in list(communication_manager.tasks.items())[-10:]:
            activities.append({
                "type": "task",
                "timestamp": task.created_at.isoformat() if task.created_at else datetime.now().isoformat(),
                "description": f"Tâche {task_id} ({task.status.name if isinstance(task.status, TaskStatus) else task.status})",
                "details": task.description[:100] + ("..." if len(task.description) > 100 else "")
            })
        
        # Trier par timestamp (plus récent en premier)
        activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Limiter à 20 activités
        return jsonify(activities[:20])
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des activités: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/statistics')
def get_statistics():
    """Récupère des statistiques globales sur le système."""
    if LIMITED_MODE:
        # Mode simulé
        return jsonify({
            "agents_count": simulated_stats["agents_count"],
            "tasks_count": len(simulated_tasks),
            "active_tasks_count": simulated_stats["active_tasks_count"],
            "messages_count": simulated_stats["messages_count"],
            "tasks_by_status": {
                "PENDING": 2,
                "IN_PROGRESS": 1,
                "COMPLETED": 1,
                "DELEGATED": 1
            }
        })
    
    if not communication_manager:
        return jsonify({"error": "Le système n'est pas initialisé"}), 500
    
    try:
        # Compter le nombre d'agents actifs
        agents_count = len(agents_registry)
        
        # Compter les tâches par statut
        tasks_by_status = {}
        active_tasks = 0
        for task in communication_manager.tasks.values():
            status = task.status.name if isinstance(task.status, TaskStatus) else str(task.status)
            tasks_by_status[status] = tasks_by_status.get(status, 0) + 1
            
            if status in ('PENDING', 'IN_PROGRESS'):
                active_tasks += 1
        
        # Compter le nombre de messages échangés (approximatif)
        messages_count = communication_manager.message_counter
        
        return jsonify({
            "agents_count": agents_count,
            "tasks_count": len(communication_manager.tasks),
            "active_tasks_count": active_tasks,
            "messages_count": messages_count,
            "tasks_by_status": tasks_by_status
        })
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        return jsonify({"error": str(e)}), 500


# Point d'entrée pour l'exécution directe
if __name__ == '__main__':
    # Initialiser le système
    if initialize_system():
        # Démarrer le serveur Flask
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        logger.error("Impossible de démarrer le serveur, échec de l'initialisation du système")
        sys.exit(1)