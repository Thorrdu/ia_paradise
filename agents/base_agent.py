"""
Classe de base pour tous les agents dans Paradis IA
Fournit des fonctionnalités communes et une interface standardisée
"""

import os
import time
import json
import threading
import logging
from typing import Dict, List, Any, Optional, Callable, Union

# Importer nos modules personnalisés
from api.llm.model_interface import ModelInterface, create_model_interface
from api.communication import (
    CommunicationManager, Message, Task, 
    Priority, TaskStatus
)
from memory.vector_db.simple_vector_store import SimpleVectorStore

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/agents.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class BaseAgent:
    """
    Classe de base pour tous les agents dans Paradis IA
    
    Cette classe fournit:
    - Une interface avec le modèle LLM
    - Un système de communication inter-agents
    - Un stockage vectoriel pour les connaissances
    - Des utilitaires de gestion des tâches
    """
    
    def __init__(
        self,
        name: str,
        model_name: str = "mixtral",
        provider: str = "ollama",
        system_prompt: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        communication_manager: Optional[CommunicationManager] = None,
        vector_store_name: Optional[str] = None,
        auto_initialize: bool = True
    ):
        """
        Initialise un nouvel agent
        
        Args:
            name: Nom unique de l'agent
            model_name: Nom du modèle LLM à utiliser
            provider: Fournisseur du modèle (ollama, openai, etc.)
            system_prompt: Message système par défaut pour le modèle
            capabilities: Liste des capacités de l'agent
            communication_manager: Gestionnaire de communication partagé
            vector_store_name: Nom du stockage vectoriel de l'agent
            auto_initialize: Si True, initialise automatiquement l'agent
        """
        self.name = name
        self.model_name = model_name
        self.provider = provider
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        self.capabilities = capabilities or self._get_default_capabilities()
        
        # Logger spécifique à l'agent
        self.logger = logging.getLogger(f"agent.{name}")
        
        # Initialiser le modèle LLM
        try:
            self.llm = create_model_interface(
                model_name=model_name,
                provider=provider,
                system_prompt=self.system_prompt
            )
            self.logger.info(f"Modèle {model_name} initialisé avec succès")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation du modèle: {e}")
            self.llm = None
        
        # Initialiser le gestionnaire de communication
        if communication_manager:
            self.comm_manager = communication_manager
        else:
            try:
                self.comm_manager = CommunicationManager()
                self.logger.info("Gestionnaire de communication initialisé")
            except Exception as e:
                self.logger.error(f"Erreur lors de l'initialisation du gestionnaire de communication: {e}")
                self.comm_manager = None
        
        # Initialiser le stockage vectoriel
        vector_store_name = vector_store_name or f"{name}_knowledge"
        try:
            self.vector_store = SimpleVectorStore(vector_store_name)
            self.logger.info(f"Stockage vectoriel {vector_store_name} initialisé")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation du stockage vectoriel: {e}")
            self.vector_store = None
        
        # Compteur d'activité et statut de l'agent
        self.is_running = False
        self.message_count = 0
        self.task_count = 0
        
        # Thread de traitement des messages
        self.message_processing_thread = None
        
        # Si auto_initialize est True, enregistrer l'agent et démarrer le traitement
        if auto_initialize:
            self.initialize()
    
    def _get_default_system_prompt(self) -> str:
        """
        Retourne le message système par défaut pour cet agent
        À surcharger dans les classes dérivées
        """
        return (
            f"Tu es {self.name}, un agent IA faisant partie du système Paradis IA. "
            f"Tu dois répondre de manière concise et précise aux requêtes qui te sont soumises. "
            f"Utilise les outils à ta disposition pour accomplir tes tâches."
        )
    
    def _get_default_capabilities(self) -> List[str]:
        """
        Retourne les capacités par défaut de cet agent
        À surcharger dans les classes dérivées
        """
        return ["communication", "basic_reasoning"]
    
    def initialize(self) -> bool:
        """
        Initialise l'agent: enregistrement, connexion au modèle, etc.
        
        Returns:
            True si l'initialisation a réussi, False sinon
        """
        # Vérifier que les composants requis sont disponibles
        if not self.llm:
            self.logger.error("Impossible d'initialiser l'agent: modèle LLM non disponible")
            return False
        
        if not self.comm_manager:
            self.logger.error("Impossible d'initialiser l'agent: gestionnaire de communication non disponible")
            return False
        
        # Enregistrer l'agent auprès du gestionnaire de communication
        try:
            self.comm_manager.register_agent(
                agent_name=self.name,
                capabilities=self.capabilities,
                metadata={
                    "model": self.model_name,
                    "provider": self.provider
                }
            )
            self.logger.info(f"Agent {self.name} enregistré avec succès")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement de l'agent: {e}")
            return False
        
        return True
    
    def start(self) -> bool:
        """
        Démarre l'agent et le traitement des messages
        
        Returns:
            True si le démarrage a réussi, False sinon
        """
        if self.is_running:
            self.logger.warning("L'agent est déjà en cours d'exécution")
            return True
        
        # Vérifier que l'agent est initialisé
        if not self.llm or not self.comm_manager:
            self.logger.error("Impossible de démarrer l'agent: non initialisé")
            return False
        
        # Démarrer le thread de traitement des messages
        try:
            self.is_running = True
            self.message_processing_thread = threading.Thread(
                target=self._message_processing_loop,
                daemon=True
            )
            self.message_processing_thread.start()
            self.logger.info(f"Agent {self.name} démarré")
            return True
        except Exception as e:
            self.is_running = False
            self.logger.error(f"Erreur lors du démarrage de l'agent: {e}")
            return False
    
    def stop(self) -> None:
        """Arrête l'agent et le traitement des messages"""
        self.is_running = False
        self.logger.info(f"Agent {self.name} arrêté")
    
    def _message_processing_loop(self) -> None:
        """
        Boucle principale de traitement des messages
        Cette méthode s'exécute dans un thread séparé
        """
        self.logger.info(f"Démarrage de la boucle de traitement des messages pour {self.name}")
        
        while self.is_running:
            try:
                # Récupérer les messages non lus
                messages = self.comm_manager.get_messages_for_agent(
                    agent_name=self.name,
                    unread_only=True,
                    limit=10
                )
                
                # Traiter chaque message
                for message_data in messages:
                    message_id = message_data.get("message_id")
                    
                    # Traiter le message
                    self.logger.info(f"Traitement du message {message_id}")
                    self._process_message(message_data)
                    
                    # Marquer le message comme lu
                    self.comm_manager.mark_message_as_read(message_id)
                    
                    # Incrémenter le compteur
                    self.message_count += 1
                
                # Vérifier les tâches assignées
                tasks = self.comm_manager.get_tasks(
                    assigned_to=self.name,
                    status=TaskStatus.PENDING
                )
                
                # Traiter chaque tâche
                for task_data in tasks:
                    task_id = task_data.get("task_id")
                    
                    # Marquer la tâche comme étant en cours
                    self.comm_manager.update_task_status(task_id, TaskStatus.IN_PROGRESS)
                    
                    # Traiter la tâche
                    self.logger.info(f"Traitement de la tâche {task_id}")
                    self._process_task(task_data)
                    
                    # Incrémenter le compteur
                    self.task_count += 1
                
                # Pause pour éviter de surcharger le système
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Erreur dans la boucle de traitement: {e}")
                time.sleep(5)  # Pause plus longue en cas d'erreur
    
    def _process_message(self, message_data: Dict[str, Any]) -> None:
        """
        Traite un message reçu
        À surcharger dans les classes dérivées pour un comportement personnalisé
        
        Args:
            message_data: Données du message à traiter
        """
        try:
            sender = message_data.get("sender", "")
            content = message_data.get("content", "")
            
            # Générer une réponse avec le modèle LLM
            prompt = f"Tu as reçu un message de {sender}: {content}\n\nRéponds de manière appropriée:"
            response = self.llm.generate(prompt)
            
            # Extraire la réponse
            response_text = response.get("response", "Désolé, je ne peux pas traiter ce message pour le moment.")
            
            # Envoyer la réponse
            self.send_message(
                recipient=sender,
                content=response_text,
                priority=message_data.get("priority", Priority.MEDIUM.value)
            )
            
            self.logger.info(f"Réponse envoyée à {sender}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement du message: {e}")
    
    def _process_task(self, task_data: Dict[str, Any]) -> None:
        """
        Traite une tâche assignée
        À surcharger dans les classes dérivées pour un comportement personnalisé
        
        Args:
            task_data: Données de la tâche à traiter
        """
        try:
            task_id = task_data.get("task_id", "")
            description = task_data.get("description", "")
            created_by = task_data.get("created_by", "")
            
            # Générer une réponse avec le modèle LLM
            prompt = (
                f"Tu dois accomplir la tâche suivante: {description}\n"
                f"Cette tâche a été créée par {created_by}.\n\n"
                f"Comment vas-tu procéder? Génère une réponse détaillant ton plan d'action."
            )
            response = self.llm.generate(prompt)
            
            # Extraire la réponse
            response_text = response.get("response", "Je vais analyser cette tâche et y travailler.")
            
            # Envoyer un message pour informer du traitement
            self.send_message(
                recipient=created_by,
                content=f"Je travaille sur la tâche {task_id}. {response_text}",
                priority=task_data.get("priority", Priority.MEDIUM.value),
                metadata={"task_id": task_id}
            )
            
            # Marquer la tâche comme terminée
            # Dans une implémentation réelle, cela dépendrait du résultat du traitement
            self.comm_manager.update_task_status(task_id, TaskStatus.COMPLETED)
            
            self.logger.info(f"Tâche {task_id} traitée")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de la tâche: {e}")
            try:
                # Marquer la tâche comme échouée
                self.comm_manager.update_task_status(task_id, TaskStatus.FAILED)
            except:
                pass
    
    def send_message(
        self,
        recipient: str,
        content: str,
        priority: Union[Priority, str] = Priority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
        create_task: bool = False
    ) -> Dict[str, Any]:
        """
        Envoie un message à un autre agent
        
        Args:
            recipient: Nom de l'agent destinataire
            content: Contenu du message
            priority: Priorité du message
            metadata: Métadonnées additionnelles
            create_task: Si True, crée une tâche associée au message
            
        Returns:
            Dictionnaire contenant les identifiants du message et éventuellement de la tâche
        """
        try:
            result = self.comm_manager.send_message(
                sender=self.name,
                recipient=recipient,
                content=content,
                priority=priority,
                metadata=metadata,
                create_task=create_task
            )
            
            self.logger.info(f"Message envoyé à {recipient}" + (
                f" avec tâche {result.get('task_id')}" if create_task else ""
            ))
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message: {e}")
            return {"error": str(e)}
    
    def add_knowledge(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Ajoute une connaissance au stockage vectoriel de l'agent
        
        Args:
            content: Contenu textuel à stocker
            metadata: Métadonnées associées au contenu
            
        Returns:
            Identifiant de la connaissance ajoutée
        """
        try:
            # Générer l'embedding avec le modèle LLM
            embedding = self.llm.embedding(content)
            
            if not embedding:
                self.logger.error("Impossible de générer l'embedding")
                return -1
            
            # Ajouter au stockage vectoriel
            doc_id = self.vector_store.add(
                document=content,
                embedding=embedding,
                metadata=metadata or {}
            )
            
            self.logger.info(f"Connaissance ajoutée avec ID {doc_id}")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout de connaissance: {e}")
            return -1
    
    def search_knowledge(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Recherche des connaissances similaires à une requête
        
        Args:
            query: Texte de la requête
            top_k: Nombre maximum de résultats
            score_threshold: Score minimum pour les résultats
            
        Returns:
            Liste des documents correspondants avec leurs scores
        """
        try:
            # Générer l'embedding de la requête
            query_embedding = self.llm.embedding(query)
            
            if not query_embedding:
                self.logger.error("Impossible de générer l'embedding pour la requête")
                return []
            
            # Effectuer la recherche
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                score_threshold=score_threshold
            )
            
            self.logger.info(f"Recherche effectuée: {len(results)} résultats trouvés")
            return results
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche de connaissances: {e}")
            return []
    
    def create_task(
        self,
        description: str,
        assigned_to: str,
        priority: Union[Priority, str] = Priority.MEDIUM,
        deadline: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Task]:
        """
        Crée une nouvelle tâche et l'assigne à un agent
        
        Args:
            description: Description de la tâche
            assigned_to: Nom de l'agent assigné
            priority: Priorité de la tâche
            deadline: Date limite optionnelle (format ISO)
            metadata: Métadonnées additionnelles
            
        Returns:
            Tâche créée ou None en cas d'erreur
        """
        try:
            task = self.comm_manager.create_task(
                description=description,
                assigned_to=assigned_to,
                created_by=self.name,
                priority=priority,
                deadline=deadline,
                metadata=metadata
            )
            
            self.logger.info(f"Tâche créée et assignée à {assigned_to}: {task.task_id}")
            return task
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la création de la tâche: {e}")
            return None
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Génère une réponse à partir d'un prompt en utilisant le modèle LLM
        
        Args:
            prompt: Le prompt à envoyer au modèle
            system_prompt: Message système optionnel
            temperature: Température optionnelle
            max_tokens: Nombre maximal de tokens optionnel
            
        Returns:
            Texte généré par le modèle
        """
        try:
            response = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.get("response", "")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de réponse: {e}")
            return f"Erreur: {str(e)}"
    
    def get_status(self) -> Dict[str, Any]:
        """
        Retourne l'état actuel de l'agent
        
        Returns:
            Dictionnaire contenant les informations sur l'état de l'agent
        """
        return {
            "name": self.name,
            "model": self.model_name,
            "provider": self.provider,
            "running": self.is_running,
            "message_count": self.message_count,
            "task_count": self.task_count,
            "capabilities": self.capabilities,
            "knowledge_count": len(self.vector_store.documents) if self.vector_store else 0
        } 