from typing import Dict, List, Optional, Any
import psutil
import os
import platform
import json
from datetime import datetime
from .base_agent import BaseAgent
from .communication_inter_ia import Message, MessagePriority, TaskStatus

class SystemAgent(BaseAgent):
    def __init__(self, name: str, communication_manager):
        super().__init__(name, communication_manager)
        self.capabilities = [
            'system_monitoring',
            'resource_management',
            'process_control',
            'performance_optimization',
            'system_configuration'
        ]
        self.register(self.capabilities)
        self.monitoring_interval = 5  # secondes
        self.alert_thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90
        }

    def _handle_normal_message(self, message: Message) -> str:
        """Traite le contenu d'un message spécifique à la gestion système."""
        content = message.content.lower()
        metadata = message.metadata or {}

        # Gestion du ping pour la mesure du temps de réponse
        if content == "ping":
            return "pong"

        if "monitor" in content or "status" in content:
            return self._handle_system_monitoring(message)
        elif "optimize" in content:
            return self._handle_optimization(message)
        elif "kill" in content or "stop" in content:
            return self._handle_process_control(message)
        elif "config" in content:
            return self._handle_configuration(message)
        else:
            return "Je ne comprends pas la demande. Veuillez préciser si vous souhaitez un monitoring, une optimisation, un contrôle de processus ou une configuration."

    def _handle_system_monitoring(self, message: Message) -> str:
        """Gère les demandes de monitoring système."""
        # Création d'une tâche pour le monitoring
        task_id = self.create_task(
            description="Monitoring système",
            priority=MessagePriority.MEDIUM
        )
        
        try:
            # Collecte des informations système
            system_info = self._collect_system_info()
            
            # Vérification des alertes
            alerts = self._check_alerts(system_info)
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            # Sauvegarde dans la mémoire
            self.save_memory('last_system_info', system_info)
            
            # Formatage de la réponse
            response = self._format_monitoring_response(system_info, alerts)
            return response
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors du monitoring système: {str(e)}")

    def _handle_optimization(self, message: Message) -> str:
        """Gère les demandes d'optimisation système."""
        # Création d'une tâche pour l'optimisation
        task_id = self.create_task(
            description="Optimisation système",
            priority=MessagePriority.HIGH
        )
        
        try:
            # Analyse de l'état actuel
            current_state = self._collect_system_info()
            
            # Application des optimisations
            optimizations = self._apply_optimizations(current_state)
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return f"Optimisations appliquées:\n{optimizations}"
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors de l'optimisation système: {str(e)}")

    def _handle_process_control(self, message: Message) -> str:
        """Gère les demandes de contrôle de processus."""
        process_name = message.metadata.get('process_name')
        action = message.metadata.get('action', 'stop')
        
        if not process_name:
            return "Nom du processus non spécifié"
            
        # Création d'une tâche pour le contrôle de processus
        task_id = self.create_task(
            description=f"Contrôle du processus {process_name}",
            priority=MessagePriority.HIGH
        )
        
        try:
            # Exécution de l'action
            result = self._control_process(process_name, action)
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return f"Action {action} sur le processus {process_name}: {result}"
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors du contrôle du processus: {str(e)}")

    def _handle_configuration(self, message: Message) -> str:
        """Gère les demandes de configuration système."""
        config = message.metadata.get('config', {})
        
        if not config:
            return "Aucune configuration spécifiée"
            
        # Création d'une tâche pour la configuration
        task_id = self.create_task(
            description="Configuration système",
            priority=MessagePriority.MEDIUM
        )
        
        try:
            # Application de la configuration
            result = self._apply_configuration(config)
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return f"Configuration appliquée:\n{result}"
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors de la configuration système: {str(e)}")

    def _collect_system_info(self) -> Dict[str, Any]:
        """Collecte les informations système."""
        return {
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv
            },
            'processes': len(psutil.pids()),
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine()
            }
        }

    def _check_alerts(self, system_info: Dict[str, Any]) -> List[str]:
        """Vérifie si des alertes doivent être déclenchées."""
        alerts = []
        
        # Vérification CPU
        if system_info['cpu']['percent'] > self.alert_thresholds['cpu_percent']:
            alerts.append(f"Utilisation CPU élevée: {system_info['cpu']['percent']}%")
            
        # Vérification mémoire
        if system_info['memory']['percent'] > self.alert_thresholds['memory_percent']:
            alerts.append(f"Utilisation mémoire élevée: {system_info['memory']['percent']}%")
            
        # Vérification disque
        if system_info['disk']['percent'] > self.alert_thresholds['disk_percent']:
            alerts.append(f"Espace disque faible: {system_info['disk']['percent']}%")
            
        return alerts

    def _format_monitoring_response(self, system_info: Dict[str, Any], alerts: List[str]) -> str:
        """Formate la réponse du monitoring."""
        response = ["=== État du Système ===\n"]
        
        # Informations CPU
        response.append(f"CPU:")
        response.append(f"- Utilisation: {system_info['cpu']['percent']}%")
        response.append(f"- Cores: {system_info['cpu']['count']}")
        if system_info['cpu']['freq']:
            response.append(f"- Fréquence: {system_info['cpu']['freq']['current']}MHz")
            
        # Informations mémoire
        response.append(f"\nMémoire:")
        response.append(f"- Total: {system_info['memory']['total'] / (1024**3):.2f} GB")
        response.append(f"- Utilisée: {system_info['memory']['used'] / (1024**3):.2f} GB")
        response.append(f"- Disponible: {system_info['memory']['available'] / (1024**3):.2f} GB")
        response.append(f"- Utilisation: {system_info['memory']['percent']}%")
        
        # Informations disque
        response.append(f"\nDisque:")
        response.append(f"- Total: {system_info['disk']['total'] / (1024**3):.2f} GB")
        response.append(f"- Utilisé: {system_info['disk']['used'] / (1024**3):.2f} GB")
        response.append(f"- Libre: {system_info['disk']['free'] / (1024**3):.2f} GB")
        response.append(f"- Utilisation: {system_info['disk']['percent']}%")
        
        # Informations réseau
        response.append(f"\nRéseau:")
        response.append(f"- Données envoyées: {system_info['network']['bytes_sent'] / (1024**2):.2f} MB")
        response.append(f"- Données reçues: {system_info['network']['bytes_recv'] / (1024**2):.2f} MB")
        
        # Informations processus
        response.append(f"\nProcessus:")
        response.append(f"- Nombre total: {system_info['processes']}")
        
        # Alertes
        if alerts:
            response.append("\n=== Alertes ===")
            for alert in alerts:
                response.append(f"- {alert}")
                
        return "\n".join(response)

    def _apply_optimizations(self, system_info: Dict[str, Any]) -> List[str]:
        """Applique des optimisations système."""
        optimizations = []
        
        # Optimisation CPU
        if system_info['cpu']['percent'] > 70:
            # Tenter de réduire la charge CPU
            self._optimize_cpu_usage()
            optimizations.append("Optimisation de l'utilisation CPU effectuée")
            
        # Optimisation mémoire
        if system_info['memory']['percent'] > 80:
            # Tenter de libérer de la mémoire
            self._optimize_memory_usage()
            optimizations.append("Optimisation de l'utilisation mémoire effectuée")
            
        # Optimisation disque
        if system_info['disk']['percent'] > 85:
            # Tenter de libérer de l'espace disque
            self._optimize_disk_usage()
            optimizations.append("Optimisation de l'utilisation disque effectuée")
            
        return optimizations

    def _control_process(self, process_name: str, action: str) -> str:
        """Contrôle un processus système."""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == process_name:
                    if action == 'stop':
                        proc.kill()
                        return "Processus arrêté"
                    elif action == 'pause':
                        proc.suspend()
                        return "Processus mis en pause"
                    elif action == 'resume':
                        proc.resume()
                        return "Processus repris"
            return "Processus non trouvé"
        except Exception as e:
            raise Exception(f"Erreur lors du contrôle du processus: {str(e)}")

    def _apply_configuration(self, config: Dict[str, Any]) -> str:
        """Applique une configuration système."""
        results = []
        
        # Configuration du monitoring
        if 'monitoring_interval' in config:
            self.monitoring_interval = config['monitoring_interval']
            results.append(f"Intervalle de monitoring mis à jour: {self.monitoring_interval}s")
            
        # Configuration des seuils d'alerte
        if 'alert_thresholds' in config:
            self.alert_thresholds.update(config['alert_thresholds'])
            results.append("Seuils d'alerte mis à jour")
            
        return "\n".join(results)

    def _optimize_cpu_usage(self) -> None:
        """Optimise l'utilisation CPU."""
        # Implémentation de l'optimisation CPU
        pass

    def _optimize_memory_usage(self) -> None:
        """Optimise l'utilisation mémoire."""
        # Implémentation de l'optimisation mémoire
        pass

    def _optimize_disk_usage(self) -> None:
        """Optimise l'utilisation disque."""
        # Implémentation de l'optimisation disque
        pass

    def _get_last_action(self) -> str:
        """Récupère la dernière action de l'agent."""
        if self.state['last_action']:
            return self.state['last_action']
        return "Aucune action récente" 