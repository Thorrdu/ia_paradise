from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from .communication_inter_ia import (
    CommunicationManager, Message, MessagePriority,
    Task, TaskStatus
)
import json

class BaseAgent:
    def __init__(self, name: str, communication_manager: CommunicationManager):
        self.name = name
        self.communication_manager = communication_manager
        self.logger = logging.getLogger(f'{self.__class__.__name__}_{name}')
        self.current_tasks: Dict[str, Task] = {}
        self.memory: Dict[str, Any] = {}
        self.state: Dict[str, Any] = {
            'last_action': None,
            'last_action_time': None,
            'consecutive_failures': 0,
            'success_rate': 1.0
        }
        
        # Configuration du logger
        self.logger.setLevel(logging.INFO)

    def register(self, capabilities: List[str]) -> None:
        """Enregistre l'agent avec ses capacités."""
        self.communication_manager.register_agent(self.name, capabilities)
        self.logger.info(f"Agent {self.name} enregistré avec les capacités: {capabilities}")

    def process_messages(self) -> None:
        """Traite tous les messages en attente."""
        messages = self.communication_manager.get_messages(self.name)
        for message in messages:
            self.handle_message(message)

    def handle_message(self, message: Message) -> None:
        """Traite un message reçu."""
        self.logger.info(f"Traitement du message de {message.sender}: {message.content}")
        
        # Mise à jour de l'état
        self.state['last_action_time'] = datetime.now()
        
        try:
            # Traitement du message
            response = self._process_message_content(message)
            
            # Envoi de la réponse
            self._send_response(
                message.sender,
                response,
                MessagePriority.HIGH if message.priority == MessagePriority.URGENT else MessagePriority.MEDIUM,
                requires_acknowledgment=True
            )
            
            # Mise à jour des statistiques
            self.state['consecutive_failures'] = 0
            self.state['success_rate'] = min(1.0, self.state['success_rate'] + 0.1)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement du message: {str(e)}")
            self.state['consecutive_failures'] += 1
            self.state['success_rate'] = max(0.0, self.state['success_rate'] - 0.1)
            
            # Notification d'erreur
            self._send_response(
                message.sender,
                f"Erreur lors du traitement de votre demande: {str(e)}",
                MessagePriority.HIGH,
                requires_acknowledgment=True
            )

    def _process_message_content(self, message: Message) -> str:
        """Traite le contenu d'un message."""
        content = message.content.lower()
        metadata = message.metadata or {}
        
        # Gestion des requêtes de statut
        if content == "status" and metadata.get("request"):
            return self._handle_status_request(metadata["request"])
            
        # Traitement normal des messages
        return self._handle_normal_message(message)
        
    def _handle_status_request(self, request_type: str) -> str:
        """Gère les requêtes de statut."""
        try:
            if request_type == "memory_usage":
                return self._get_memory_usage()
            elif request_type == "cpu_usage":
                return self._get_cpu_usage()
            elif request_type == "task_count":
                return str(len(self.current_tasks))
            elif request_type == "state":
                return self._get_state()
            else:
                return "Type de requête non supporté"
        except Exception as e:
            self.logger.error(f"Erreur lors de la gestion de la requête de statut {request_type}: {str(e)}")
            return "Erreur lors de la récupération du statut"
            
    def _get_memory_usage(self) -> str:
        """Récupère l'utilisation mémoire de l'agent."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return str(memory_info.rss / 1024 / 1024)  # Conversion en MB
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération de l'utilisation mémoire: {str(e)}")
            return "0.0"
            
    def _get_cpu_usage(self) -> str:
        """Récupère l'utilisation CPU de l'agent."""
        try:
            import psutil
            process = psutil.Process()
            return str(process.cpu_percent())
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération de l'utilisation CPU: {str(e)}")
            return "0.0"
            
    def _get_state(self) -> str:
        """Récupère l'état actuel de l'agent."""
        return json.dumps({
            "name": self.name,
            "task_count": len(self.current_tasks),
            "memory_usage": self._get_memory_usage(),
            "cpu_usage": self._get_cpu_usage(),
            "capabilities": self.capabilities,
            "last_action": self._get_last_action()
        })

    def _handle_normal_message(self, message: Message) -> str:
        """Traite un message normal."""
        # Implementation of _handle_normal_message method
        raise NotImplementedError("Les classes dérivées doivent implémenter _handle_normal_message")

    def _get_last_action(self) -> str:
        """Récupère le dernier action de l'agent."""
        # Implementation of _get_last_action method
        raise NotImplementedError("Les classes dérivées doivent implémenter _get_last_action")

    def _send_response(self, recipient: str, content: str, 
                      priority: MessagePriority = MessagePriority.MEDIUM,
                      requires_acknowledgment: bool = False) -> None:
        """Envoie une réponse à un autre agent."""
        message = Message(
            sender=self.name,
            recipient=recipient,
            content=content,
            priority=priority,
            timestamp=datetime.now(),
            requires_acknowledgment=requires_acknowledgment
        )
        self.communication_manager.send_message(message)

    def create_task(self, description: str, priority: MessagePriority = MessagePriority.MEDIUM,
                   deadline: Optional[datetime] = None,
                   dependencies: List[str] = None) -> str:
        """Crée une nouvelle tâche."""
        task_id = self.communication_manager.create_task(
            description=description,
            assigned_to=self.name,
            priority=priority,
            deadline=deadline,
            dependencies=dependencies
        )
        self.current_tasks[task_id] = self.communication_manager.tasks[task_id]
        return task_id

    def update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """Met à jour le statut d'une tâche."""
        if task_id in self.current_tasks:
            self.communication_manager.update_task_status(task_id, status)
            self.current_tasks[task_id].status = status

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Récupère le statut d'une tâche."""
        return self.communication_manager.get_task_status(task_id)

    def get_delegation_history(self) -> List[str]:
        """Récupère l'historique des délégations de l'agent."""
        return self.communication_manager.get_delegation_history(self.name)

    def get_current_load(self) -> int:
        """Récupère la charge actuelle de l'agent."""
        return self.communication_manager.get_agent_load(self.name)

    def save_memory(self, key: str, value: Any) -> None:
        """Sauvegarde une information dans la mémoire de l'agent."""
        self.memory[key] = {
            'value': value,
            'timestamp': datetime.now()
        }

    def get_memory(self, key: str) -> Optional[Any]:
        """Récupère une information de la mémoire de l'agent."""
        if key in self.memory:
            return self.memory[key]['value']
        return None

    def clear_memory(self, key: Optional[str] = None) -> None:
        """Efface la mémoire de l'agent."""
        if key:
            self.memory.pop(key, None)
        else:
            self.memory.clear()

    def get_state(self) -> Dict[str, Any]:
        """Récupère l'état actuel de l'agent."""
        return {
            **self.state,
            'current_tasks': len(self.current_tasks),
            'memory_size': len(self.memory),
            'load': self.get_current_load()
        } 