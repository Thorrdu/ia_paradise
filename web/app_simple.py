#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Serveur web simplifié pour l'interface utilisateur de Paradis IA
"""

import os
import sys
import logging
import json
import time
import datetime
import psutil

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("web/logs/web_server_simple.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("web_server_simple")

# Importation de Flask
try:
    from flask import Flask, jsonify, request, render_template, send_from_directory
    from flask_cors import CORS
except ImportError as e:
    logger.error(f"Impossible d'importer Flask: {e}")
    logger.error("Installez Flask avec: py -m pip install flask flask-cors")
    sys.exit(1)

# Création de l'application Flask
app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web/static"),
            template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web/templates"))
CORS(app)

# Simulation des données
simulated_agents = [
    {
        "name": "PHPDevAgent",
        "status": "ready",
        "capabilities": ["php_development", "debugging", "optimization"],
        "last_seen": datetime.datetime.now().isoformat()
    },
    {
        "name": "SystemAgent",
        "status": "ready", 
        "capabilities": ["system_management", "monitoring"],
        "last_seen": datetime.datetime.now().isoformat()
    },
    {
        "name": "WebInterface",
        "status": "ready",
        "capabilities": ["user_interaction", "api"],
        "last_seen": datetime.datetime.now().isoformat()
    }
]

simulated_tasks = [
    {
        "task_id": "task-001",
        "description": "Analyser les logs d'erreurs PHP",
        "assigned_to": "PHPDevAgent",
        "created_by": "WebInterface",
        "priority": "HIGH",
        "status": "PENDING",
        "created_at": (datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat()
    },
    {
        "task_id": "task-002",
        "description": "Surveiller l'utilisation système",
        "assigned_to": "SystemAgent",
        "created_by": "WebInterface",
        "priority": "MEDIUM",
        "status": "IN_PROGRESS",
        "created_at": (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat()
    }
]

simulated_messages = [
    {
        "message_id": "msg-001",
        "sender": "WebInterface",
        "recipient": "PHPDevAgent",
        "content": "Analyse les erreurs dans le fichier log.php",
        "priority": "HIGH",
        "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=30)).isoformat()
    },
    {
        "message_id": "msg-002",
        "sender": "PHPDevAgent",
        "recipient": "WebInterface",
        "content": "J'ai identifié une erreur de syntaxe à la ligne 42. Il manque un point-virgule.",
        "priority": "MEDIUM",
        "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=15)).isoformat()
    }
]

# Routes
@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Retourne la liste des agents"""
    return jsonify(simulated_agents)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Retourne la liste des tâches"""
    return jsonify(simulated_tasks)

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Retourne les détails d'une tâche spécifique"""
    task = next((t for t in simulated_tasks if t["task_id"] == task_id), None)
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Crée une nouvelle tâche"""
    data = request.json
    
    if not data or not all(k in data for k in ["description", "assigned_to"]):
        return jsonify({"error": "Invalid request"}), 400
    
    new_task = {
        "task_id": f"task-{int(time.time())}",
        "description": data["description"],
        "assigned_to": data["assigned_to"],
        "created_by": data.get("created_by", "WebInterface"),
        "priority": data.get("priority", "MEDIUM"),
        "status": "PENDING",
        "created_at": datetime.datetime.now().isoformat()
    }
    
    simulated_tasks.append(new_task)
    
    # Simuler un message de confirmation
    new_message = {
        "message_id": f"msg-{int(time.time())}",
        "sender": "SystemAgent",
        "recipient": "WebInterface",
        "content": f"Tâche créée et assignée à {data['assigned_to']}: {data['description'][:50]}...",
        "priority": "MEDIUM",
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    simulated_messages.append(new_message)
    
    return jsonify(new_task)

@app.route('/api/message', methods=['POST'])
def send_message():
    """Simule l'envoi d'un message"""
    data = request.json
    if not data or not all(k in data for k in ["recipient", "content"]):
        return jsonify({"error": "Invalid request"}), 400
    
    new_message = {
        "message_id": f"msg-{int(time.time())}",
        "sender": "WebInterface",
        "recipient": data["recipient"],
        "content": data["content"],
        "priority": data.get("priority", "MEDIUM"),
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    simulated_messages.append(new_message)
    
    # Simuler une réponse après 2 secondes
    time.sleep(2)
    
    response_content = f"Message reçu, je vais traiter votre demande concernant: {data['content'][:50]}..."
    response_message = {
        "message_id": f"msg-{int(time.time())}",
        "sender": data["recipient"],
        "recipient": "WebInterface",
        "content": response_content,
        "priority": "MEDIUM",
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    simulated_messages.append(response_message)
    
    return jsonify(new_message)

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Retourne la liste des messages"""
    return jsonify(simulated_messages)

@app.route('/api/system/stats', methods=['GET'])
def get_system_stats():
    """Retourne les statistiques système"""
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    stats = {
        "cpu": {
            "percent": cpu_percent,
            "cores": psutil.cpu_count()
        },
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent
        },
        "gpu": {
            "available": True,
            "name": "NVIDIA GeForce RTX 4060",
            "percent": 45,  # Valeur simulée
            "memory": {
                "total": 8589934592,  # 8 GB
                "used": 3758096384,   # ~3.5 GB
                "percent": 43.75
            }
        },
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    return jsonify(stats)

@app.route('/api/system/mode', methods=['GET'])
def get_system_mode():
    """Retourne le mode du système (limité ou complet)"""
    return jsonify({
        "mode": "LIMITED",
        "features_available": [
            "web_interface",
            "simulated_agents",
            "simulated_tasks",
            "simulated_messages"
        ],
        "features_disabled": [
            "real_llm_integration",
            "agent_creation",
            "vector_storage",
            "model_fine_tuning"
        ]
    })

@app.route('/api/monitoring', methods=['GET'])
def get_monitoring():
    """Alias pour /api/system/stats pour compatibilité"""
    return get_system_stats()

@app.route('/static/<path:path>')
def serve_static(path):
    """Sert les fichiers statiques"""
    try:
        # Chemin absolu vers le dossier static
        static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web/static")
        logger.info(f"Servir fichier statique: {path} depuis {static_dir}")
        return send_from_directory(static_dir, path)
    except Exception as e:
        logger.error(f"Erreur lors du chargement du fichier statique {path}: {e}")
        return f"Fichier non trouvé: {path}", 404

if __name__ == '__main__':
    logger.info("Démarrage du serveur web simplifié")
    try:
        # Créer le dossier de logs s'il n'existe pas
        os.makedirs("web/logs", exist_ok=True)
        # Démarrer le serveur
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du serveur: {e}") 