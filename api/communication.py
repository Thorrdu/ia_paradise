"""
Module de communication entre agents pour Paradis IA
Fournit une interface standardisée pour l'échange de messages entre agents
"""

import os
import json
import time
import uuid
import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Union

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
    """Représente un message échangé entre agents"""
    
    def __init__(
        self,
        sender: str,
        recipient: str,
        content: str,
        priority: Priority = Priority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None
    ):
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.priority = priority if isinstance(priority, Priority) else Priority(priority)
        self.metadata = metadata or {}
        self.message_id = message_id or str(uuid.uuid4())
        self.timestamp = datetime.datetime.now().isoformat()
        self.read = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire pour sérialisation"""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content,
            "priority": self.priority.value,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "read": self.read
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Message':
        """Crée un message à partir d'un dictionnaire"""
        message = Message(
            sender=data.get("sender", ""),
            recipient=data.get("recipient", ""),
            content=data.get("content", ""),
            priority=data.get("priority", Priority.MEDIUM.value),
            metadata=data.get("metadata", {}),
            message_id=data.get("message_id")
        )
        message.timestamp = data.get("timestamp", message.timestamp)
        message.read = data.get("read", False)
        return message
    
    def mark_as_read(self) -> None:
        """Marque le message comme lu"""
        self.read = True

class Task:
    """Représente une tâche à accomplir par un agent"""
    
    def __init__(
        self,
        description: str,
        assigned_to: str,
        created_by: str,
        priority: Priority = Priority.MEDIUM,
        status: TaskStatus = TaskStatus.PENDING,
        deadline: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ):
        self.task_id = task_id or f"task-{str(uuid.uuid4())[:5]}"
        self.description = description
        self.assigned_to = assigned_to
        self.created_by = created_by
        self.priority = priority if isinstance(priority, Priority) else Priority(priority)
        self.status = status if isinstance(status, TaskStatus) else TaskStatus(status)
        self.created_at = datetime.datetime.now().isoformat()
        self.deadline = deadline
        self.metadata = metadata or {}
        self.messages: List[Message] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la tâche en dictionnaire pour sérialisation"""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at,
            "deadline": self.deadline,
            "metadata": self.metadata,
            "messages": [msg.to_dict() for msg in self.messages]
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Task':
        """Crée une tâche à partir d'un dictionnaire"""
        task = Task(
            description=data.get("description", ""),
            assigned_to=data.get("assigned_to", ""),
            created_by=data.get("created_by", ""),
            priority=data.get("priority", Priority.MEDIUM.value),
            status=data.get("status", TaskStatus.PENDING.value),
            deadline=data.get("deadline"),
            metadata=data.get("metadata", {}),
            task_id=data.get("task_id")
        )
        task.created_at = data.get("created_at", task.created_at)
        task.messages = [Message.from_dict(msg) for msg in data.get("messages", [])]
        return task
    
    def add_message(self, message: Message) -> None:
        """Ajoute un message à la tâche"""
        self.messages.append(message)
    
    def update_status(self, status: TaskStatus) -> None:
        """Met à jour le statut de la tâche"""
        self.status = status if isinstance(status, TaskStatus) else TaskStatus(status)

class CommunicationManager:
    """
    Gère la communication entre agents
    Stocke et achemine les messages et tâches
    """
    
    def __init__(self, data_dir: str = "./memory/data"):
        self.data_dir = data_dir
        self.messages_file = os.path.join(data_dir, "messages.json")
        self.tasks_file = os.path.join(data_dir, "tasks.json")
        self.agents_file = os.path.join(data_dir, "agents.json")
        
        # Stockage en mémoire
        self.messages: List[Message] = []
        self.tasks: List[Task] = []
        self.agents: Dict[str, Dict[str, Any]] = {}
        
        # Créer le répertoire s'il n'existe pas
        os.makedirs(data_dir, exist_ok=True)
        
        # Charger les données existantes
        self._load_data()
    
    def _load_data(self) -> None:
        """Charge les données depuis le disque"""
        try:
            # Charger les messages
            if os.path.exists(self.messages_file):
                with open(self.messages_file, 'r', encoding='utf-8') as f:
                    messages_data = json.load(f)
                    self.messages = [Message.from_dict(msg) for msg in messages_data]
            
            # Charger les tâches
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    tasks_data = json.load(f)
                    self.tasks = [Task.from_dict(task) for task in tasks_data]
            
            # Charger les agents
            if os.path.exists(self.agents_file):
                with open(self.agents_file, 'r', encoding='utf-8') as f:
                    self.agents = json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des données de communication: {e}")
            # Initialiser avec des listes vides en cas d'erreur
            self.messages = []
            self.tasks = []
            self.agents = {}
    
    def _save_data(self) -> None:
        """Sauvegarde les données sur le disque"""
        try:
            # Sauvegarder les messages
            with open(self.messages_file, 'w', encoding='utf-8') as f:
                json.dump([msg.to_dict() for msg in self.messages], f, ensure_ascii=False, indent=2)
            
            # Sauvegarder les tâches
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump([task.to_dict() for task in self.tasks], f, ensure_ascii=False, indent=2)
            
            # Sauvegarder les agents
            with open(self.agents_file, 'w', encoding='utf-8') as f:
                json.dump(self.agents, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données de communication: {e}")
    
    def register_agent(
        self, 
        agent_name: str, 
        capabilities: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Enregistre un nouvel agent dans le système
        
        Args:
            agent_name: Nom unique de l'agent
            capabilities: Liste des capacités de l'agent
            metadata: Métadonnées additionnelles sur l'agent
        """
        if agent_name in self.agents:
            # Mettre à jour l'agent existant
            self.agents[agent_name].update({
                "capabilities": capabilities,
                "metadata": metadata or {},
                "last_seen": datetime.datetime.now().isoformat()
            })
        else:
            # Créer un nouvel agent
            self.agents[agent_name] = {
                "name": agent_name,
                "capabilities": capabilities,
                "metadata": metadata or {},
                "created_at": datetime.datetime.now().isoformat(),
                "last_seen": datetime.datetime.now().isoformat()
            }
        
        self._save_data()
    
    def send_message(
        self,
        sender: str,
        recipient: str,
        content: str,
        priority: Union[Priority, str] = Priority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
        create_task: bool = False
    ) -> Dict[str, Any]:
        """
        Envoie un message d'un agent à un autre
        
        Args:
            sender: Nom de l'agent émetteur
            recipient: Nom de l'agent destinataire
            content: Contenu du message
            priority: Priorité du message
            metadata: Métadonnées additionnelles
            create_task: Si True, crée une tâche associée au message
            
        Returns:
            Dictionnaire contenant les identifiants du message et éventuellement de la tâche
        """
        # Vérifier que les agents existent
        if sender not in self.agents:
            raise ValueError(f"Agent émetteur inconnu: {sender}")
        if recipient not in self.agents:
            raise ValueError(f"Agent destinataire inconnu: {recipient}")
        
        # Créer et stocker le message
        message = Message(
            sender=sender,
            recipient=recipient,
            content=content,
            priority=priority,
            metadata=metadata
        )
        
        self.messages.append(message)
        
        # Créer une tâche si demandé
        task_id = None
        if create_task:
            task = Task(
                description=content,
                assigned_to=recipient,
                created_by=sender,
                priority=priority,
                metadata=metadata
            )
            task.add_message(message)
            self.tasks.append(task)
            task_id = task.task_id
        
        # Mettre à jour le timestamp de dernière activité
        self.agents[sender]["last_seen"] = datetime.datetime.now().isoformat()
        
        # Sauvegarder les changements
        self._save_data()
        
        return {
            "message_id": message.message_id,
            "task_id": task_id
        }
    
    def get_messages_for_agent(
        self,
        agent_name: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Récupère les messages pour un agent spécifique
        
        Args:
            agent_name: Nom de l'agent
            unread_only: Si True, récupère uniquement les messages non lus
            limit: Nombre maximum de messages à récupérer
            
        Returns:
            Liste des messages pour l'agent
        """
        # Vérifier que l'agent existe
        if agent_name not in self.agents:
            raise ValueError(f"Agent inconnu: {agent_name}")
        
        # Filtrer les messages pour cet agent
        agent_messages = []
        for message in reversed(self.messages):  # Du plus récent au plus ancien
            if message.recipient == agent_name:
                if not unread_only or not message.read:
                    agent_messages.append(message.to_dict())
                    
                    if len(agent_messages) >= limit:
                        break
        
        return agent_messages
    
    def mark_message_as_read(self, message_id: str) -> bool:
        """
        Marque un message comme lu
        
        Args:
            message_id: Identifiant du message
            
        Returns:
            True si le message a été trouvé et marqué comme lu, False sinon
        """
        for message in self.messages:
            if message.message_id == message_id:
                message.mark_as_read()
                self._save_data()
                return True
        
        return False
    
    def create_task(
        self,
        description: str,
        assigned_to: str,
        created_by: str,
        priority: Union[Priority, str] = Priority.MEDIUM,
        deadline: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        Crée une nouvelle tâche
        
        Args:
            description: Description de la tâche
            assigned_to: Agent assigné à la tâche
            created_by: Agent créateur de la tâche
            priority: Priorité de la tâche
            deadline: Date limite optionnelle (format ISO)
            metadata: Métadonnées additionnelles
            
        Returns:
            La tâche créée
        """
        # Vérifier que les agents existent
        if assigned_to not in self.agents:
            raise ValueError(f"Agent assigné inconnu: {assigned_to}")
        if created_by not in self.agents:
            raise ValueError(f"Agent créateur inconnu: {created_by}")
        
        # Créer la tâche
        task = Task(
            description=description,
            assigned_to=assigned_to,
            created_by=created_by,
            priority=priority,
            deadline=deadline,
            metadata=metadata
        )
        
        # Ajouter à la liste des tâches
        self.tasks.append(task)
        
        # Créer un message pour informer l'agent assigné
        message = Message(
            sender=created_by,
            recipient=assigned_to,
            content=f"Nouvelle tâche assignée: {description}",
            priority=priority,
            metadata={"task_id": task.task_id}
        )
        
        # Ajouter le message à la tâche et à la liste des messages
        task.add_message(message)
        self.messages.append(message)
        
        # Mettre à jour les timestamps de dernière activité
        self.agents[created_by]["last_seen"] = datetime.datetime.now().isoformat()
        
        # Sauvegarder les changements
        self._save_data()
        
        return task
    
    def update_task_status(self, task_id: str, status: Union[TaskStatus, str]) -> bool:
        """
        Met à jour le statut d'une tâche
        
        Args:
            task_id: Identifiant de la tâche
            status: Nouveau statut
            
        Returns:
            True si la tâche a été trouvée et mise à jour, False sinon
        """
        for task in self.tasks:
            if task.task_id == task_id:
                task.update_status(status)
                self._save_data()
                return True
        
        return False
    
    def get_tasks(
        self,
        assigned_to: Optional[str] = None,
        status: Optional[Union[TaskStatus, str]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Récupère les tâches selon les critères spécifiés
        
        Args:
            assigned_to: Filtrer par agent assigné
            status: Filtrer par statut
            limit: Nombre maximum de tâches à récupérer
            
        Returns:
            Liste des tâches correspondant aux critères
        """
        # Convertir le statut en objet TaskStatus si nécessaire
        if status and not isinstance(status, TaskStatus):
            status = TaskStatus(status)
        
        # Filtrer les tâches
        filtered_tasks = []
        for task in reversed(self.tasks):  # Du plus récent au plus ancien
            if assigned_to and task.assigned_to != assigned_to:
                continue
            
            if status and task.status != status:
                continue
            
            filtered_tasks.append(task.to_dict())
            
            if len(filtered_tasks) >= limit:
                break
        
        return filtered_tasks
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste de tous les agents enregistrés
        
        Returns:
            Liste des agents
        """
        return list(self.agents.values())
    
    def get_recent_activities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les activités récentes (messages et modifications de tâches)
        
        Args:
            limit: Nombre maximum d'activités à récupérer
            
        Returns:
            Liste des activités récentes
        """
        activities = []
        
        # Ajouter les messages récents
        for message in reversed(self.messages):
            activities.append({
                "type": "message",
                "timestamp": message.timestamp,
                "description": f"Message de {message.sender} à {message.recipient}",
                "details": message.content[:100] + "..." if len(message.content) > 100 else message.content,
                "priority": message.priority.value
            })
            
            if len(activities) >= limit:
                break
        
        # Trier par timestamp décroissant
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Limiter au nombre demandé
        return activities[:limit] 