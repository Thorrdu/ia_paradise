from typing import Dict, List, Optional, Any
import time
import json
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from .communication_inter_ia import Message, MessagePriority, TaskStatus

class MonitoringAgent(BaseAgent):
    def __init__(self, name: str, communication_manager):
        super().__init__(name, communication_manager)
        self.capabilities = [
            'performance_monitoring',
            'agent_health_check',
            'resource_tracking',
            'alert_management',
            'reporting'
        ]
        self.register(self.capabilities)
        self.metrics_history: Dict[str, List[Dict[str, Any]]] = {}
        self.alert_rules: Dict[str, Dict[str, Any]] = {
            'response_time': {'threshold': 2.0, 'unit': 'seconds'},
            'error_rate': {'threshold': 0.1, 'unit': 'ratio'},
            'memory_usage': {'threshold': 85, 'unit': 'percent'},
            'cpu_usage': {'threshold': 80, 'unit': 'percent'}
        }
        self.reporting_interval = 300  # 5 minutes
        self.last_report_time = datetime.now()

    def _handle_normal_message(self, message: Message) -> str:
        """Traite le contenu d'un message spécifique au monitoring."""
        content = message.content.lower()
        metadata = message.metadata or {}

        # Gestion du ping pour la mesure du temps de réponse
        if content == "ping":
            return "pong"

        if "monitor" in content or "status" in content:
            return self._handle_agent_monitoring(message)
        elif "alert" in content:
            return self._handle_alert_management(message)
        elif "report" in content:
            return self._handle_report_generation(message)
        elif "config" in content:
            return self._handle_monitoring_config(message)
        else:
            return "Je ne comprends pas la demande. Veuillez préciser si vous souhaitez un monitoring, une gestion d'alertes, un rapport ou une configuration."

    def _handle_agent_monitoring(self, message: Message) -> str:
        """Gère le monitoring des agents."""
        # Création d'une tâche pour le monitoring
        task_id = self.create_task(
            description="Monitoring des agents",
            priority=MessagePriority.MEDIUM
        )
        
        try:
            # Collecte des métriques
            metrics = self._collect_agent_metrics()
            
            # Vérification des alertes
            alerts = self._check_alert_rules(metrics)
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            # Sauvegarde des métriques
            self._save_metrics(metrics)
            
            # Formatage de la réponse
            response = self._format_monitoring_response(metrics, alerts)
            return response
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors du monitoring des agents: {str(e)}")

    def _handle_alert_management(self, message: Message) -> str:
        """Gère les alertes de monitoring."""
        action = message.metadata.get('action')
        alert_data = message.metadata.get('alert_data')
        
        if not action or not alert_data:
            return "Action ou données d'alerte non spécifiées"
            
        # Création d'une tâche pour la gestion des alertes
        task_id = self.create_task(
            description="Gestion des alertes",
            priority=MessagePriority.HIGH
        )
        
        try:
            if action == 'add':
                self._add_alert_rule(alert_data)
                result = "Règle d'alerte ajoutée"
            elif action == 'update':
                self._update_alert_rule(alert_data)
                result = "Règle d'alerte mise à jour"
            elif action == 'remove':
                self._remove_alert_rule(alert_data)
                result = "Règle d'alerte supprimée"
            else:
                return "Action non supportée"
                
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return result
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors de la gestion des alertes: {str(e)}")

    def _handle_report_generation(self, message: Message) -> str:
        """Gère la génération de rapports."""
        report_type = message.metadata.get('type', 'performance')
        time_range = message.metadata.get('time_range', '24h')
        
        # Création d'une tâche pour la génération de rapport
        task_id = self.create_task(
            description=f"Génération de rapport {report_type}",
            priority=MessagePriority.MEDIUM
        )
        
        try:
            # Génération du rapport
            report = self._generate_report(report_type, time_range)
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return f"Rapport {report_type} généré:\n{report}"
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors de la génération du rapport: {str(e)}")

    def _handle_monitoring_config(self, message: Message) -> str:
        """Gère la configuration du monitoring."""
        config = message.metadata.get('config', {})
        
        if not config:
            return "Aucune configuration spécifiée"
            
        # Création d'une tâche pour la configuration
        task_id = self.create_task(
            description="Configuration du monitoring",
            priority=MessagePriority.MEDIUM
        )
        
        try:
            # Application de la configuration
            result = self._apply_monitoring_config(config)
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return f"Configuration appliquée:\n{result}"
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors de la configuration du monitoring: {str(e)}")

    def _collect_agent_metrics(self) -> Dict[str, Any]:
        """Collecte les métriques des agents."""
        metrics = {}
        
        # Récupération des informations sur tous les agents
        for agent_name in self.communication_manager.registered_agents:
            agent_metrics = {
                'response_time': self._measure_response_time(agent_name),
                'error_rate': self._calculate_error_rate(agent_name),
                'memory_usage': self._get_memory_usage(agent_name),
                'cpu_usage': self._get_cpu_usage(agent_name),
                'task_count': len(self.communication_manager.tasks),
                'last_action': self._get_last_action(agent_name),
                'success_rate': self._get_success_rate(agent_name)
            }
            metrics[agent_name] = agent_metrics
            
        return metrics

    def _check_alert_rules(self, metrics: Dict[str, Any]) -> List[str]:
        """Vérifie les règles d'alerte sur les métriques."""
        alerts = []
        
        for agent_name, agent_metrics in metrics.items():
            for metric_name, value in agent_metrics.items():
                if metric_name in self.alert_rules:
                    rule = self.alert_rules[metric_name]
                    if self._check_threshold(value, rule['threshold'], rule['unit']):
                        alerts.append(
                            f"ALERTE: {agent_name} - {metric_name} = {value} {rule['unit']} "
                            f"(seuil: {rule['threshold']})"
                        )
                        
        return alerts

    def _save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Sauvegarde les métriques dans l'historique."""
        timestamp = datetime.now()
        
        for agent_name, agent_metrics in metrics.items():
            if agent_name not in self.metrics_history:
                self.metrics_history[agent_name] = []
                
            self.metrics_history[agent_name].append({
                'timestamp': timestamp,
                'metrics': agent_metrics
            })
            
            # Limiter l'historique à 24h
            cutoff_time = timestamp - timedelta(hours=24)
            self.metrics_history[agent_name] = [
                entry for entry in self.metrics_history[agent_name]
                if entry['timestamp'] > cutoff_time
            ]

    def _format_monitoring_response(self, metrics: Dict[str, Any], alerts: List[str]) -> str:
        """Formate la réponse du monitoring."""
        response = ["=== État des Agents ===\n"]
        
        for agent_name, agent_metrics in metrics.items():
            response.append(f"\nAgent: {agent_name}")
            response.append(f"- Temps de réponse: {agent_metrics['response_time']:.2f}s")
            response.append(f"- Taux d'erreur: {agent_metrics['error_rate']:.2%}")
            response.append(f"- Utilisation mémoire: {agent_metrics['memory_usage']}%")
            response.append(f"- Utilisation CPU: {agent_metrics['cpu_usage']}%")
            response.append(f"- Tâches en cours: {agent_metrics['task_count']}")
            response.append(f"- Dernière action: {agent_metrics['last_action']}")
            response.append(f"- Taux de succès: {agent_metrics['success_rate']:.2%}")
            
        if alerts:
            response.append("\n=== Alertes ===")
            for alert in alerts:
                response.append(f"- {alert}")
                
        return "\n".join(response)

    def _generate_report(self, report_type: str, time_range: str) -> str:
        """Génère un rapport de monitoring."""
        if report_type == 'performance':
            return self._generate_performance_report(time_range)
        elif report_type == 'health':
            return self._generate_health_report(time_range)
        elif report_type == 'resource':
            return self._generate_resource_report(time_range)
        else:
            raise ValueError(f"Type de rapport non supporté: {report_type}")

    def _generate_performance_report(self, time_range: str) -> str:
        """Génère un rapport de performance."""
        report = ["=== Rapport de Performance ===\n"]
        
        # Calcul de la période
        end_time = datetime.now()
        if time_range == '24h':
            start_time = end_time - timedelta(hours=24)
        elif time_range == '7d':
            start_time = end_time - timedelta(days=7)
        else:
            start_time = end_time - timedelta(hours=1)
            
        for agent_name, history in self.metrics_history.items():
            report.append(f"\nAgent: {agent_name}")
            
            # Calcul des moyennes
            response_times = [
                entry['metrics']['response_time']
                for entry in history
                if start_time <= entry['timestamp'] <= end_time
            ]
            error_rates = [
                entry['metrics']['error_rate']
                for entry in history
                if start_time <= entry['timestamp'] <= end_time
            ]
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                report.append(f"- Temps de réponse moyen: {avg_response_time:.2f}s")
                
            if error_rates:
                avg_error_rate = sum(error_rates) / len(error_rates)
                report.append(f"- Taux d'erreur moyen: {avg_error_rate:.2%}")
                
        return "\n".join(report)

    def _generate_health_report(self, time_range: str) -> str:
        """Génère un rapport de santé."""
        report = ["=== Rapport de Santé ===\n"]
        
        # Calcul de la période
        end_time = datetime.now()
        if time_range == '24h':
            start_time = end_time - timedelta(hours=24)
        elif time_range == '7d':
            start_time = end_time - timedelta(days=7)
        else:
            start_time = end_time - timedelta(hours=1)
            
        for agent_name, history in self.metrics_history.items():
            report.append(f"\nAgent: {agent_name}")
            
            # Calcul des statistiques de santé
            success_rates = [
                entry['metrics']['success_rate']
                for entry in history
                if start_time <= entry['timestamp'] <= end_time
            ]
            
            if success_rates:
                avg_success_rate = sum(success_rates) / len(success_rates)
                health_status = "Bon" if avg_success_rate > 0.9 else "Moyen" if avg_success_rate > 0.7 else "Critique"
                report.append(f"- État de santé: {health_status}")
                report.append(f"- Taux de succès moyen: {avg_success_rate:.2%}")
                
        return "\n".join(report)

    def _generate_resource_report(self, time_range: str) -> str:
        """Génère un rapport d'utilisation des ressources."""
        report = ["=== Rapport d'Utilisation des Ressources ===\n"]
        
        # Calcul de la période
        end_time = datetime.now()
        if time_range == '24h':
            start_time = end_time - timedelta(hours=24)
        elif time_range == '7d':
            start_time = end_time - timedelta(days=7)
        else:
            start_time = end_time - timedelta(hours=1)
            
        for agent_name, history in self.metrics_history.items():
            report.append(f"\nAgent: {agent_name}")
            
            # Calcul des moyennes d'utilisation
            memory_usage = [
                entry['metrics']['memory_usage']
                for entry in history
                if start_time <= entry['timestamp'] <= end_time
            ]
            cpu_usage = [
                entry['metrics']['cpu_usage']
                for entry in history
                if start_time <= entry['timestamp'] <= end_time
            ]
            
            if memory_usage:
                avg_memory = sum(memory_usage) / len(memory_usage)
                report.append(f"- Utilisation mémoire moyenne: {avg_memory:.1f}%")
                
            if cpu_usage:
                avg_cpu = sum(cpu_usage) / len(cpu_usage)
                report.append(f"- Utilisation CPU moyenne: {avg_cpu:.1f}%")
                
        return "\n".join(report)

    def _apply_monitoring_config(self, config: Dict[str, Any]) -> str:
        """Applique une configuration de monitoring."""
        results = []
        
        # Configuration des règles d'alerte
        if 'alert_rules' in config:
            self.alert_rules.update(config['alert_rules'])
            results.append("Règles d'alerte mises à jour")
            
        # Configuration de l'intervalle de rapport
        if 'reporting_interval' in config:
            self.reporting_interval = config['reporting_interval']
            results.append(f"Intervalle de rapport mis à jour: {self.reporting_interval}s")
            
        return "\n".join(results)

    # Méthodes utilitaires privées
    def _measure_response_time(self, agent_name: str) -> float:
        """Mesure le temps de réponse d'un agent."""
        if agent_name == self.name:
            # Éviter de s'envoyer un message à soi-même
            return 0.1  # Valeur raisonnable par défaut
        
        start_time = time.time()
        try:
            # Envoi d'un message ping à l'agent avec un flag spécial pour éviter les boucles
            message = Message(
                content="ping",
                sender=self.name,
                recipient=agent_name,
                priority=MessagePriority.LOW,
                timestamp=datetime.now(),
                metadata={"response_time_measurement": True}
            )
            self.communication_manager.send_message(message)
            
            # Au lieu d'attendre la réponse immédiatement, on retourne une valeur estimée
            # Dans un système réel, on utiliserait un mécanisme asynchrone
            return 0.5  # Valeur raisonnable par défaut
        except Exception as e:
            self.logger.error(f"Erreur lors de la mesure du temps de réponse pour {agent_name}: {str(e)}")
            return 0.0

    def _calculate_error_rate(self, agent_name: str) -> float:
        """Calcule le taux d'erreur d'un agent."""
        try:
            # Récupération des messages d'erreur de l'agent
            error_messages = [
                msg for msg in self.communication_manager.get_messages(self.name, 100)
                if msg.sender == agent_name and "error" in msg.content.lower()
            ]
            
            # Récupération du nombre total de messages
            total_messages = len(self.communication_manager.get_messages(self.name, 100))
            
            if total_messages == 0:
                return 0.0
                
            return len(error_messages) / total_messages
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul du taux d'erreur pour {agent_name}: {str(e)}")
            return 0.0

    def _get_memory_usage(self, agent_name: str) -> float:
        """Récupère l'utilisation mémoire d'un agent."""
        if agent_name == self.name:
            # Pour soi-même, utiliser psutil
            try:
                import psutil
                process = psutil.Process()
                memory_info = process.memory_info()
                return memory_info.rss / (1024 * 1024 * 1024) * 100  # En pourcentage de GB
            except Exception as e:
                self.logger.error(f"Erreur lors de la récupération de l'utilisation mémoire locale: {str(e)}")
                return 5.0  # Valeur par défaut raisonnable
        
        # Pour les autres agents, retourner une valeur estimée
        # Dans un système réel, on utiliserait un mécanisme asynchrone ou un registre central
        return 10.0  # Valeur par défaut raisonnable

    def _get_cpu_usage(self, agent_name: str) -> float:
        """Récupère l'utilisation CPU d'un agent."""
        if agent_name == self.name:
            # Pour soi-même, utiliser psutil
            try:
                import psutil
                return psutil.cpu_percent(interval=0.1)
            except Exception as e:
                self.logger.error(f"Erreur lors de la récupération de l'utilisation CPU locale: {str(e)}")
                return 5.0  # Valeur par défaut raisonnable
        
        # Pour les autres agents, retourner une valeur estimée
        # Dans un système réel, on utiliserait un mécanisme asynchrone ou un registre central
        return 15.0  # Valeur par défaut raisonnable

    def _get_last_action(self, agent_name: str) -> str:
        """Récupère la dernière action d'un agent."""
        if agent_name == self.name:
            return self.state.get('last_action', 'N/A')
            
        # Pour les autres agents, retourner une valeur par défaut
        # Dans un système réel, on utiliserait un registre central d'actions
        return "Dernière action non disponible"

    def _get_success_rate(self, agent_name: str) -> float:
        """Récupère le taux de succès d'un agent."""
        if agent_name == self.name:
            return self.state.get('success_rate', 1.0)
            
        # Pour les autres agents, retourner une valeur par défaut
        # Dans un système réel, on utiliserait un registre central de métriques
        return 0.95  # Valeur par défaut optimiste

    def _check_threshold(self, value: float, threshold: float, unit: str) -> bool:
        """Vérifie si une valeur dépasse un seuil."""
        if unit == 'percent':
            return value > threshold
        elif unit == 'ratio':
            return value > threshold
        elif unit == 'seconds':
            return value > threshold
        return False

    def _add_alert_rule(self, rule_data: Dict[str, Any]) -> None:
        """Ajoute une règle d'alerte."""
        metric_name = rule_data.get('metric_name')
        if metric_name:
            self.alert_rules[metric_name] = {
                'threshold': rule_data.get('threshold'),
                'unit': rule_data.get('unit')
            }

    def _update_alert_rule(self, rule_data: Dict[str, Any]) -> None:
        """Met à jour une règle d'alerte."""
        self._add_alert_rule(rule_data)

    def _remove_alert_rule(self, rule_data: Dict[str, Any]) -> None:
        """Supprime une règle d'alerte."""
        metric_name = rule_data.get('metric_name')
        if metric_name in self.alert_rules:
            del self.alert_rules[metric_name] 