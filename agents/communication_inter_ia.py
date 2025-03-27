from typing import Dict, List, Optional, Set, Any
import json
import logging
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import os
from threading import Lock

# Configuration du logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/inter_ia_communication.log'),
        logging.StreamHandler()
    ]
)

class MessagePriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DELEGATED = "delegated"

@dataclass
class Task:
    id: str
    description: str
    assigned_to: str
    status: TaskStatus
    created_at: datetime
    deadline: Optional[datetime] = None
    dependencies: List[str] = None
    priority: MessagePriority = MessagePriority.MEDIUM

@dataclass
class Message:
    sender: str
    recipient: str
    content: str
    priority: MessagePriority
    timestamp: datetime
    metadata: Optional[Dict] = None
    task_id: Optional[str] = None
    requires_acknowledgment: bool = False
    acknowledgment_received: bool = False

class ConflictResolutionStrategy(Enum):
    PRIORITY_BASED = "priority_based"
    TIMESTAMP_BASED = "timestamp_based"
    ROUND_ROBIN = "round_robin"

class CommunicationManager:
    def __init__(self):
        self.message_queue: List[Message] = []
        self.registered_agents: Dict[str, List[str]] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_counter = 0
        self.logger = logging.getLogger('CommunicationManager')
        self.lock = Lock()  # Pour la gestion des conflits
        self.conflict_resolution_strategy = ConflictResolutionStrategy.PRIORITY_BASED
        self.acknowledgment_timeout = 30  # secondes
        self.delegation_history: Dict[str, List[str]] = {}
        self.agent_loads: Dict[str, int] = {}

    def register_agent(self, agent_name: str, capabilities: List[str]) -> None:
        """Enregistre un nouvel agent avec ses capacités."""
        with self.lock:
            self.registered_agents[agent_name] = capabilities
            self.agent_loads[agent_name] = 0
            self.delegation_history[agent_name] = []
            self.logger.info(f"Agent {agent_name} enregistré avec les capacités: {capabilities}")

    def send_message(self, message: Message) -> bool:
        """Envoie un message à un agent spécifique avec gestion des conflits."""
        with self.lock:
            if message.recipient not in self.registered_agents:
                self.logger.error(f"Agent {message.recipient} non trouvé")
                return False

            # Vérification des conflits potentiels
            if self._check_for_conflicts(message):
                self._resolve_conflicts(message)

            self.message_queue.append(message)
            self.message_queue.sort(key=lambda x: (x.priority.value, x.timestamp))
            self.logger.info(f"Message envoyé de {message.sender} à {message.recipient}")
            return True

    def _check_for_conflicts(self, message: Message) -> bool:
        """Vérifie s'il y a des conflits potentiels avec le message."""
        # Vérification des messages en attente pour le même destinataire
        pending_messages = [msg for msg in self.message_queue if msg.recipient == message.recipient]
        
        # Vérification des priorités et des dépendances
        for pending_msg in pending_messages:
            if (pending_msg.priority == message.priority and 
                pending_msg.task_id and message.task_id and 
                pending_msg.task_id != message.task_id):
                return True
        return False

    def _resolve_conflicts(self, message: Message) -> None:
        """Résout les conflits selon la stratégie choisie."""
        if self.conflict_resolution_strategy == ConflictResolutionStrategy.PRIORITY_BASED:
            self._resolve_by_priority(message)
        elif self.conflict_resolution_strategy == ConflictResolutionStrategy.TIMESTAMP_BASED:
            self._resolve_by_timestamp(message)
        else:  # ROUND_ROBIN
            self._resolve_by_round_robin(message)

    def _resolve_by_priority(self, message: Message) -> None:
        """Résout les conflits en se basant sur la priorité."""
        self.message_queue = [msg for msg in self.message_queue 
                            if msg.recipient != message.recipient or 
                            msg.priority.value > message.priority.value]
        self.logger.info(f"Résolution de conflit par priorité pour {message.recipient}")

    def _resolve_by_timestamp(self, message: Message) -> None:
        """Résout les conflits en se basant sur l'horodatage."""
        self.message_queue = [msg for msg in self.message_queue 
                            if msg.recipient != message.recipient or 
                            msg.timestamp > message.timestamp]
        self.logger.info(f"Résolution de conflit par horodatage pour {message.recipient}")

    def _resolve_by_round_robin(self, message: Message) -> None:
        """Résout les conflits en utilisant un système de tourniquet."""
        if message.recipient in self.agent_loads:
            self.agent_loads[message.recipient] += 1
            if self.agent_loads[message.recipient] > 5:  # Limite de charge
                self._delegate_task(message)
                self.agent_loads[message.recipient] = 0
        self.logger.info(f"Résolution de conflit par tourniquet pour {message.recipient}")

    def _delegate_task(self, message: Message) -> None:
        """Délègue une tâche à un autre agent disponible."""
        available_agents = [agent for agent, load in self.agent_loads.items() 
                          if load < 5 and agent != message.recipient]
        
        if available_agents:
            # Trouver l'agent avec la charge la plus faible
            new_recipient = min(available_agents, key=lambda x: self.agent_loads[x])
            message.recipient = new_recipient
            self.delegation_history[message.recipient].append(new_recipient)
            self.logger.info(f"Tâche déléguée de {message.recipient} à {new_recipient}")

    def create_task(self, description: str, assigned_to: str, 
                   priority: MessagePriority = MessagePriority.MEDIUM,
                   deadline: Optional[datetime] = None,
                   dependencies: List[str] = None) -> str:
        """Crée une nouvelle tâche avec gestion des dépendances."""
        with self.lock:
            self.task_counter += 1
            task_id = f"task_{self.task_counter}"
            
            task = Task(
                id=task_id,
                description=description,
                assigned_to=assigned_to,
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
                deadline=deadline,
                dependencies=dependencies or [],
                priority=priority
            )
            
            self.tasks[task_id] = task
            self.logger.info(f"Nouvelle tâche créée: {task_id} pour {assigned_to}")
            return task_id

    def update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """Met à jour le statut d'une tâche."""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].status = status
                self.logger.info(f"Statut de la tâche {task_id} mis à jour: {status}")

    def get_messages(self, agent_name: str, limit: int = None) -> List[Message]:
        """Récupère les messages pour un agent spécifique."""
        with self.lock:
            messages = [msg for msg in self.message_queue if msg.recipient == agent_name]
            
            # Supprimer les messages de la file d'attente
            for msg in messages:
                self.message_queue.remove(msg)
                
                # Envoyer un accusé de réception si nécessaire
                if msg.requires_acknowledgment:
                    self._send_acknowledgment(msg)
            
            # Limiter le nombre de messages si demandé
            if limit is not None and limit > 0:
                return messages[:limit]
                
            return messages

    def _send_acknowledgment(self, message: Message) -> None:
        """Envoie un accusé de réception pour un message."""
        ack_message = Message(
            sender=message.recipient,
            recipient=message.sender,
            content=f"Message reçu: {message.content[:50]}...",
            priority=MessagePriority.LOW,
            timestamp=datetime.now(),
            metadata={"ack_for": message.content}
        )
        self.send_message(ack_message)

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Récupère le statut d'une tâche."""
        return self.tasks.get(task_id, None)

    def get_delegation_history(self, agent_name: str) -> List[str]:
        """Récupère l'historique des délégations d'un agent."""
        return self.delegation_history.get(agent_name, [])

    def get_agent_load(self, agent_name: str) -> int:
        """Récupère la charge actuelle d'un agent."""
        return self.agent_loads.get(agent_name, 0)

    def save_state(self, filepath: str) -> None:
        """Sauvegarde l'état actuel du gestionnaire de communication."""
        with self.lock:
            state = {
                'registered_agents': self.registered_agents,
                'tasks': {
                    task_id: {
                        'id': task.id,
                        'description': task.description,
                        'assigned_to': task.assigned_to,
                        'status': task.status.value,
                        'created_at': task.created_at.isoformat(),
                        'deadline': task.deadline.isoformat() if task.deadline else None,
                        'dependencies': task.dependencies,
                        'priority': task.priority.value
                    }
                    for task_id, task in self.tasks.items()
                },
                'message_queue': [
                    {
                        'sender': msg.sender,
                        'recipient': msg.recipient,
                        'content': msg.content,
                        'priority': msg.priority.value,
                        'timestamp': msg.timestamp.isoformat(),
                        'metadata': msg.metadata,
                        'task_id': msg.task_id,
                        'requires_acknowledgment': msg.requires_acknowledgment,
                        'acknowledgment_received': msg.acknowledgment_received
                    }
                    for msg in self.message_queue
                ],
                'delegation_history': self.delegation_history,
                'agent_loads': self.agent_loads
            }
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)

    def load_state(self, filepath: str) -> None:
        """Charge l'état du gestionnaire de communication depuis un fichier."""
        with self.lock:
            with open(filepath, 'r') as f:
                state = json.load(f)
                self.registered_agents = state['registered_agents']
                self.tasks = {
                    task_id: Task(
                        id=task_data['id'],
                        description=task_data['description'],
                        assigned_to=task_data['assigned_to'],
                        status=TaskStatus(task_data['status']),
                        created_at=datetime.fromisoformat(task_data['created_at']),
                        deadline=datetime.fromisoformat(task_data['deadline']) if task_data['deadline'] else None,
                        dependencies=task_data['dependencies'],
                        priority=MessagePriority(task_data['priority'])
                    )
                    for task_id, task_data in state['tasks'].items()
                }
                self.message_queue = [
                    Message(
                        sender=msg['sender'],
                        recipient=msg['recipient'],
                        content=msg['content'],
                        priority=MessagePriority(msg['priority']),
                        timestamp=datetime.fromisoformat(msg['timestamp']),
                        metadata=msg.get('metadata'),
                        task_id=msg.get('task_id'),
                        requires_acknowledgment=msg.get('requires_acknowledgment', False),
                        acknowledgment_received=msg.get('acknowledgment_received', False)
                    )
                    for msg in state['message_queue']
                ]
                self.delegation_history = state['delegation_history']
                self.agent_loads = state['agent_loads']

    def create_message(self, sender: str, recipient: str, content: str, 
                     priority: MessagePriority = MessagePriority.MEDIUM,
                     metadata: Dict[str, Any] = None,
                     requires_acknowledgment: bool = False) -> Message:
        """Crée un nouveau message."""
        return Message(
            sender=sender,
            recipient=recipient,
            content=content,
            priority=priority,
            metadata=metadata,
            timestamp=datetime.now(),
            requires_acknowledgment=requires_acknowledgment
        ) 