"""
Système de surveillance des ressources pour Paradis IA
Surveille l'utilisation du CPU, de la RAM et du GPU (si disponible)
"""

import os
import time
import logging
import threading
import json
from datetime import datetime
import psutil

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'monitoring.log')),
        logging.StreamHandler()
    ]
)

class SystemMonitor:
    """Surveille les ressources système et fournit des métriques en temps réel"""
    
    def __init__(self, interval=5):
        """
        Initialise le moniteur système
        
        Args:
            interval (int): Intervalle de surveillance en secondes
        """
        self.interval = interval
        self.monitoring = False
        self.monitor_thread = None
        self.stats_history = []
        self.max_history = 100  # Nombre d'échantillons à conserver
        
        # Essayer d'importer torch pour la surveillance GPU si disponible
        self.gpu_available = False
        try:
            import torch
            self.gpu_available = torch.cuda.is_available()
            if self.gpu_available:
                self.gpu_count = torch.cuda.device_count()
                logging.info(f"GPU détecté: {self.gpu_count} dispositif(s)")
            else:
                logging.info("Aucun GPU CUDA détecté")
        except ImportError:
            logging.info("PyTorch non installé, la surveillance GPU sera désactivée")
    
    def start(self):
        """Démarre la surveillance en arrière-plan"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logging.info("Surveillance système démarrée")
    
    def stop(self):
        """Arrête la surveillance"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
            logging.info("Surveillance système arrêtée")
    
    def _monitor_loop(self):
        """Boucle principale de surveillance"""
        while self.monitoring:
            try:
                stats = self._collect_stats()
                self.stats_history.append(stats)
                
                # Limiter la taille de l'historique
                if len(self.stats_history) > self.max_history:
                    self.stats_history.pop(0)
                
                # Vérifier si des ressources atteignent des niveaux critiques
                self._check_critical_levels(stats)
                
                time.sleep(self.interval)
            except Exception as e:
                logging.error(f"Erreur lors de la surveillance: {str(e)}")
                time.sleep(self.interval)
    
    def _collect_stats(self):
        """Collecte les statistiques système actuelles"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'per_cpu': psutil.cpu_percent(interval=1, percpu=True),
                'count': psutil.cpu_count(logical=True)
            },
            'memory': {
                'percent': psutil.virtual_memory().percent,
                'used_gb': round(psutil.virtual_memory().used / (1024**3), 2),
                'total_gb': round(psutil.virtual_memory().total / (1024**3), 2)
            },
            'disk': {
                'percent': psutil.disk_usage('/').percent,
                'used_gb': round(psutil.disk_usage('/').used / (1024**3), 2),
                'total_gb': round(psutil.disk_usage('/').total / (1024**3), 2)
            }
        }
        
        # Ajouter les statistiques GPU si disponibles
        if self.gpu_available:
            try:
                import torch
                gpu_stats = []
                for i in range(self.gpu_count):
                    gpu_stats.append({
                        'id': i,
                        'name': torch.cuda.get_device_name(i),
                        'memory_used': round(torch.cuda.memory_allocated(i) / (1024**3), 2),
                        'memory_total': round(torch.cuda.get_device_properties(i).total_memory / (1024**3), 2),
                        'utilization': round(torch.cuda.utilization(i), 2) if hasattr(torch.cuda, 'utilization') else None
                    })
                stats['gpu'] = gpu_stats
            except Exception as e:
                logging.error(f"Erreur lors de la collecte des statistiques GPU: {str(e)}")
                stats['gpu'] = {'error': str(e)}
        
        return stats
    
    def _check_critical_levels(self, stats):
        """Vérifie si des ressources atteignent des niveaux critiques"""
        warnings = []
        
        # Vérifier CPU
        if stats['cpu']['percent'] > 90:
            warnings.append(f"CPU utilisation CRITIQUE: {stats['cpu']['percent']}%")
        elif stats['cpu']['percent'] > 75:
            warnings.append(f"CPU utilisation ÉLEVÉE: {stats['cpu']['percent']}%")
        
        # Vérifier mémoire
        if stats['memory']['percent'] > 90:
            warnings.append(f"Mémoire utilisation CRITIQUE: {stats['memory']['percent']}%")
        elif stats['memory']['percent'] > 80:
            warnings.append(f"Mémoire utilisation ÉLEVÉE: {stats['memory']['percent']}%")
        
        # Vérifier disque
        if stats['disk']['percent'] > 90:
            warnings.append(f"Disque utilisation CRITIQUE: {stats['disk']['percent']}%")
        
        # Vérifier GPU si disponible
        if self.gpu_available and 'gpu' in stats and isinstance(stats['gpu'], list):
            for gpu in stats['gpu']:
                if 'memory_used' in gpu and 'memory_total' in gpu:
                    usage_percent = (gpu['memory_used'] / gpu['memory_total']) * 100
                    if usage_percent > 90:
                        warnings.append(f"GPU {gpu['id']} utilisation CRITIQUE: {round(usage_percent, 1)}%")
        
        # Journaliser les avertissements
        for warning in warnings:
            logging.warning(warning)
    
    def get_current_stats(self):
        """Renvoie les statistiques système actuelles"""
        if not self.stats_history:
            return self._collect_stats()
        return self.stats_history[-1]
    
    def get_stats_history(self):
        """Renvoie l'historique des statistiques système"""
        return self.stats_history
    
    def save_stats(self, filename='monitoring_stats.json'):
        """Sauvegarde les statistiques dans un fichier JSON"""
        filepath = os.path.join('logs', filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(self.stats_history, f, indent=2)
            logging.info(f"Statistiques sauvegardées dans {filepath}")
            return True
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde des statistiques: {str(e)}")
            return False

# Singleton pour le moniteur système
_monitor_instance = None

def get_monitor():
    """Renvoie l'instance singleton du moniteur système"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = SystemMonitor()
    return _monitor_instance

if __name__ == "__main__":
    # Créer le dossier logs s'il n'existe pas
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    print("Démarrage de la surveillance système...")
    monitor = get_monitor()
    monitor.start()
    
    try:
        # Exécuter pendant 1 heure puis enregistrer les statistiques
        time.sleep(3600)
        monitor.save_stats()
    except KeyboardInterrupt:
        print("\nArrêt de la surveillance système...")
    finally:
        monitor.stop()
        print("Surveillance système arrêtée.") 