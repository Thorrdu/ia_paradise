from typing import Dict, List, Optional, Any
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify
from threading import Thread
from .base_agent import BaseAgent
from .communication_inter_ia import Message, MessagePriority, TaskStatus

class WebCommunicationAgent(BaseAgent):
    def __init__(self, name: str, communication_manager, host='0.0.0.0', port=5000):
        super().__init__(name, communication_manager)
        self.capabilities = [
            'web_server',
            'api_gateway',
            'webhook_handler',
            'http_client',
            'socket_communication'
        ]
        self.register(self.capabilities)
        
        # Configuration du serveur web
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.configure_routes()
        self.server_thread = None
        
        # Stockage des webhooks enregistrés
        self.webhooks: Dict[str, Dict[str, Any]] = {}
        
        # Statistiques des requêtes
        self.request_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': []
        }
        
        # État actuel
        self.state['last_action'] = "Initialisation de l'agent web"
    
    def _handle_normal_message(self, message: Message) -> str:
        """Traite le contenu d'un message spécifique à la communication web."""
        content = message.content.lower()
        metadata = message.metadata or {}
        
        # Gestion du ping pour la mesure du temps de réponse
        if content == "ping":
            return "pong"
        
        # Mise à jour de l'état
        self.state['last_action'] = f"Traitement de: {content[:50]}..."
            
        # Traitement des différents types de messages
        if "start_server" in content:
            return self._handle_start_server(metadata.get('host', self.host), 
                                            metadata.get('port', self.port))
        elif "stop_server" in content:
            return self._handle_stop_server()
        elif "api" in content and "add" in content:
            return self._handle_add_api_endpoint(metadata)
        elif "webhook" in content and "register" in content:
            return self._handle_register_webhook(metadata)
        elif "http" in content and "request" in content:
            return self._handle_http_request(metadata)
        elif "socket" in content:
            return self._handle_socket_communication(metadata)
        elif "stats" in content:
            return self._handle_get_stats()
        else:
            return "Je ne comprends pas la demande. Veuillez préciser si vous souhaitez démarrer/arrêter le serveur, ajouter un point d'API, enregistrer un webhook, effectuer une requête HTTP, gérer une communication socket ou obtenir des statistiques."
    
    def _get_last_action(self) -> str:
        """Récupère la dernière action de l'agent."""
        return self.state.get('last_action', 'Aucune action récente')
    
    def configure_routes(self):
        """Configure les routes de base pour le serveur Flask."""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({
                'status': 'ok',
                'agent': self.name,
                'capabilities': self.capabilities,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/agents', methods=['GET'])
        def list_agents():
            agents = []
            for agent_name, capabilities in self.communication_manager.registered_agents.items():
                agents.append({
                    'name': agent_name,
                    'capabilities': capabilities
                })
            return jsonify(agents)
        
        @self.app.route('/api/message', methods=['POST'])
        def send_message():
            try:
                data = request.json
                if not data or not all(k in data for k in ['sender', 'recipient', 'content']):
                    return jsonify({'error': 'Missing required fields'}), 400
                
                # Création et envoi du message
                message = self.communication_manager.create_message(
                    sender=data['sender'],
                    recipient=data['recipient'],
                    content=data['content'],
                    priority=MessagePriority[data.get('priority', 'MEDIUM')],
                    metadata=data.get('metadata', {}),
                    requires_acknowledgment=data.get('requires_acknowledgment', False)
                )
                self.communication_manager.send_message(message)
                
                # Création d'une tâche associée si spécifiée
                task_id = None
                if data.get('create_task', False):
                    task_id = self.communication_manager.create_task(
                        description=data.get('task_description', data['content']),
                        assigned_to=data['recipient'],
                        priority=MessagePriority[data.get('priority', 'MEDIUM')]
                    )
                
                return jsonify({
                    'status': 'message_sent', 
                    'task_id': task_id
                })
                
            except Exception as e:
                self.logger.error(f"Erreur lors de l'envoi du message via API: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/tasks', methods=['GET'])
        def list_tasks():
            tasks = []
            for task_id, task in self.communication_manager.tasks.items():
                tasks.append({
                    'id': task_id,
                    'description': task.description,
                    'status': task.status.name,
                    'assigned_to': task.assigned_to,
                    'priority': task.priority.name,
                    'created_at': task.created_at.isoformat() if task.created_at else None,
                    'deadline': task.deadline.isoformat() if task.deadline else None
                })
            return jsonify(tasks)
        
        @self.app.route('/api/tasks/<task_id>', methods=['PUT'])
        def update_task(task_id):
            try:
                data = request.json
                if not data or 'status' not in data:
                    return jsonify({'error': 'Missing status field'}), 400
                
                status = TaskStatus[data['status']]
                self.communication_manager.update_task_status(task_id, status)
                
                return jsonify({
                    'status': 'task_updated',
                    'task_id': task_id,
                    'new_status': status.name
                })
                
            except Exception as e:
                self.logger.error(f"Erreur lors de la mise à jour de la tâche via API: {str(e)}")
                return jsonify({'error': str(e)}), 500
    
    def _handle_start_server(self, host=None, port=None) -> str:
        """Démarre le serveur web dans un thread séparé."""
        if self.server_thread and self.server_thread.is_alive():
            return f"Le serveur est déjà en cours d'exécution sur {self.host}:{self.port}"
        
        if host:
            self.host = host
        if port:
            self.port = port
        
        # Création d'une tâche pour le démarrage du serveur
        task_id = self.create_task(
            description=f"Démarrage du serveur web sur {self.host}:{self.port}",
            priority=MessagePriority.HIGH
        )
        
        try:
            def run_server():
                self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
                
            self.server_thread = Thread(target=run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return f"Serveur web démarré sur http://{self.host}:{self.port}"
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors du démarrage du serveur: {str(e)}")
    
    def _handle_stop_server(self) -> str:
        """Arrête le serveur web."""
        if not self.server_thread or not self.server_thread.is_alive():
            return "Le serveur n'est pas en cours d'exécution"
        
        # Création d'une tâche pour l'arrêt du serveur
        task_id = self.create_task(
            description="Arrêt du serveur web",
            priority=MessagePriority.HIGH
        )
        
        try:
            # Pour Flask, nous devons utiliser une requête pour arrêter le serveur
            import requests
            try:
                requests.get(f"http://{self.host}:{self.port}/shutdown")
            except:
                pass
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return "Serveur web arrêté"
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors de l'arrêt du serveur: {str(e)}")
    
    def _handle_add_api_endpoint(self, metadata: Dict[str, Any]) -> str:
        """Ajoute un point d'API dynamiquement."""
        path = metadata.get('path')
        methods = metadata.get('methods', ['GET'])
        agent_name = metadata.get('agent_name')
        action = metadata.get('action')
        
        if not path or not agent_name or not action:
            return "Informations manquantes pour ajouter un point d'API. Veuillez spécifier path, agent_name et action."
        
        # Création d'une tâche pour l'ajout du point d'API
        task_id = self.create_task(
            description=f"Ajout du point d'API {path} pour {agent_name}",
            priority=MessagePriority.MEDIUM
        )
        
        try:
            # Définition dynamique de la route
            def dynamic_route():
                start_time = datetime.now()
                try:
                    self.request_stats['total_requests'] += 1
                    
                    # Préparation des données de la requête
                    req_data = {
                        'query_params': dict(request.args),
                        'body': request.json if request.is_json else {},
                        'headers': dict(request.headers),
                        'method': request.method,
                        'path': request.path,
                        'remote_addr': request.remote_addr
                    }
                    
                    # Envoi du message à l'agent concerné
                    message = self.communication_manager.create_message(
                        sender=self.name,
                        recipient=agent_name,
                        content=f"API Request: {action}",
                        priority=MessagePriority.HIGH,
                        metadata={
                            'action': action,
                            'request_data': req_data
                        },
                        timestamp=datetime.now()
                    )
                    self.communication_manager.send_message(message)
                    
                    # Attente de la réponse (simplifié, dans un cas réel on utiliserait des callbacks/promises)
                    # Note: ceci est bloquant et ne convient pas pour une application production
                    # Dans un système réel, on utiliserait un système de WebSockets ou SSE
                    import time
                    for _ in range(50):  # attente maximale de 5 secondes
                        time.sleep(0.1)
                        responses = self.communication_manager.get_messages(self.name, 1)
                        if responses and responses[0].sender == agent_name:
                            response = responses[0]
                            
                            end_time = datetime.now()
                            response_time = (end_time - start_time).total_seconds()
                            self.request_stats['response_times'].append(response_time)
                            self.request_stats['successful_requests'] += 1
                            
                            return jsonify({
                                'status': 'success',
                                'data': response.content,
                                'metadata': response.metadata,
                                'response_time': response_time
                            })
                    
                    # Aucune réponse reçue
                    self.request_stats['failed_requests'] += 1
                    return jsonify({
                        'status': 'error',
                        'message': 'Timeout waiting for agent response'
                    }), 504
                    
                except Exception as e:
                    self.request_stats['failed_requests'] += 1
                    self.logger.error(f"Erreur lors du traitement de la requête API: {str(e)}")
                    return jsonify({
                        'status': 'error',
                        'message': str(e)
                    }), 500
            
            # Enregistrement de la route dans Flask
            self.app.add_url_rule(path, f"dynamic_{path.replace('/', '_')}", dynamic_route, methods=methods)
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return f"Point d'API ajouté: {path} pour {agent_name}.{action} (méthodes: {', '.join(methods)})"
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors de l'ajout du point d'API: {str(e)}")
    
    def _handle_register_webhook(self, metadata: Dict[str, Any]) -> str:
        """Enregistre un webhook."""
        hook_name = metadata.get('name')
        hook_url = metadata.get('url')
        hook_events = metadata.get('events', ['all'])
        
        if not hook_name or not hook_url:
            return "Informations manquantes pour enregistrer un webhook. Veuillez spécifier name et url."
        
        # Création d'une tâche pour l'enregistrement du webhook
        task_id = self.create_task(
            description=f"Enregistrement du webhook {hook_name}",
            priority=MessagePriority.MEDIUM
        )
        
        try:
            self.webhooks[hook_name] = {
                'url': hook_url,
                'events': hook_events,
                'created_at': datetime.now().isoformat(),
                'last_triggered': None,
                'trigger_count': 0
            }
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return f"Webhook {hook_name} enregistré pour les événements: {', '.join(hook_events)}"
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors de l'enregistrement du webhook: {str(e)}")
    
    def _handle_http_request(self, metadata: Dict[str, Any]) -> str:
        """Effectue une requête HTTP vers une URL externe."""
        url = metadata.get('url')
        method = metadata.get('method', 'GET')
        headers = metadata.get('headers', {})
        data = metadata.get('data')
        json_data = metadata.get('json')
        
        if not url:
            return "URL manquante pour la requête HTTP."
        
        # Création d'une tâche pour la requête HTTP
        task_id = self.create_task(
            description=f"Requête HTTP {method} vers {url}",
            priority=MessagePriority.MEDIUM
        )
        
        try:
            import requests
            
            kwargs = {
                'headers': headers,
                'timeout': metadata.get('timeout', 30)
            }
            
            if data:
                kwargs['data'] = data
            if json_data:
                kwargs['json'] = json_data
            
            response = requests.request(method, url, **kwargs)
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return json.dumps({
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text,
                'elapsed': response.elapsed.total_seconds()
            })
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors de la requête HTTP: {str(e)}")
    
    def _handle_socket_communication(self, metadata: Dict[str, Any]) -> str:
        """Gère la communication par socket (simplifié)."""
        return "La fonctionnalité de communication par socket n'est pas encore implémentée."
    
    def _handle_get_stats(self) -> str:
        """Récupère les statistiques des requêtes."""
        stats = dict(self.request_stats)
        
        # Calcul du temps de réponse moyen
        if stats['response_times']:
            stats['avg_response_time'] = sum(stats['response_times']) / len(stats['response_times'])
        else:
            stats['avg_response_time'] = 0
        
        # Calcul du taux de succès
        total = stats['total_requests']
        if total > 0:
            stats['success_rate'] = (stats['successful_requests'] / total) * 100
        else:
            stats['success_rate'] = 0
            
        return json.dumps(stats)
    
    def trigger_webhook(self, event: str, data: Dict[str, Any]) -> None:
        """Déclenche les webhooks enregistrés pour un événement donné."""
        import requests
        
        for hook_name, hook_info in self.webhooks.items():
            if 'all' in hook_info['events'] or event in hook_info['events']:
                try:
                    # Préparation des données à envoyer
                    webhook_data = {
                        'event': event,
                        'timestamp': datetime.now().isoformat(),
                        'agent': self.name,
                        'data': data
                    }
                    
                    # Envoi de la requête
                    response = requests.post(
                        hook_info['url'],
                        json=webhook_data,
                        headers={'Content-Type': 'application/json'},
                        timeout=5
                    )
                    
                    # Mise à jour des informations du webhook
                    hook_info['last_triggered'] = datetime.now().isoformat()
                    hook_info['trigger_count'] += 1
                    hook_info['last_status_code'] = response.status_code
                    
                    self.logger.info(f"Webhook {hook_name} déclenché pour l'événement {event}: {response.status_code}")
                    
                except Exception as e:
                    self.logger.error(f"Erreur lors du déclenchement du webhook {hook_name}: {str(e)}")
    
    def shutdown(self) -> None:
        """Arrête proprement l'agent et le serveur web."""
        if self.server_thread and self.server_thread.is_alive():
            self._handle_stop_server()
        
        # Sauvegarde des webhooks
        try:
            os.makedirs('config', exist_ok=True)
            with open('config/webhooks.json', 'w') as f:
                json.dump(self.webhooks, f, indent=2)
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des webhooks: {str(e)}")
            
        self.logger.info(f"Agent {self.name} arrêté") 