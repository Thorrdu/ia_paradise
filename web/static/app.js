/**
 * Paradis IA - Interface Web
 * Script principal de l'interface utilisateur
 */

// Variables globales
let refreshIntervals = {
    statistics: null,
    systemStats: null,
    activities: null,
    agents: null,
    tasks: null,
    logs: null
};

// Intervalles de rafraîchissement (en millisecondes)
const REFRESH_INTERVALS = {
    statistics: 10000,   // 10 secondes
    systemStats: 3000,   // 3 secondes
    activities: 15000,   // 15 secondes
    agents: 30000,       // 30 secondes
    tasks: 20000,        // 20 secondes
    logs: 30000          // 30 secondes
};

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser la navigation
    initNavigation();
    
    // Initialiser les formulaires
    initForms();
    
    // Charger les données initiales
    fetchAgents();
    fetchTasks();
    fetchLogs();
    fetchStatistics();
    fetchSystemStats();
    fetchActivities();
    
    // Configurer les rafraîchissements automatiques
    setupRefreshIntervals();
    
    // Initialiser les gestionnaires d'événements pour les boutons de rafraîchissement
    document.getElementById('refresh-tasks')?.addEventListener('click', fetchTasks);
    document.getElementById('refresh-logs')?.addEventListener('click', fetchLogs);
    
    // Initialiser les sélecteurs de niveau de log
    document.getElementById('log-level')?.addEventListener('change', fetchLogs);
});

/**
 * Initialise la navigation entre les vues
 */
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Désactiver tous les liens et masquer toutes les vues
            navLinks.forEach(l => l.classList.remove('active'));
            document.querySelectorAll('.content-view').forEach(view => view.classList.remove('active'));
            
            // Activer le lien cliqué
            this.classList.add('active');
            
            // Afficher la vue correspondante
            const viewId = this.getAttribute('data-view') + '-view';
            document.getElementById(viewId).classList.add('active');
        });
    });
}

/**
 * Initialise les formulaires et leurs comportements
 */
function initForms() {
    // Formulaire d'envoi de message
    const messageForm = document.getElementById('message-form');
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const recipient = document.getElementById('recipient').value;
            const content = document.getElementById('message-content').value;
            const priority = document.getElementById('priority').value;
            const createTask = document.getElementById('create-task').checked;
            
            if (!recipient || !content) {
                showNotification('Erreur', 'Veuillez remplir tous les champs requis.', 'danger');
                return;
            }
            
            // Envoyer le message
            sendMessage(recipient, content, priority, createTask);
        });
    }
}

/**
 * Configure les intervalles de rafraîchissement automatique
 */
function setupRefreshIntervals() {
    // Effacer tous les intervalles existants d'abord
    clearAllIntervals();
    
    // Configurer de nouveaux intervalles
    refreshIntervals.statistics = setInterval(fetchStatistics, REFRESH_INTERVALS.statistics);
    refreshIntervals.systemStats = setInterval(fetchSystemStats, REFRESH_INTERVALS.systemStats);
    refreshIntervals.activities = setInterval(fetchActivities, REFRESH_INTERVALS.activities);
    refreshIntervals.agents = setInterval(fetchAgents, REFRESH_INTERVALS.agents);
    refreshIntervals.tasks = setInterval(fetchTasks, REFRESH_INTERVALS.tasks);
    
    // Listener pour nettoyer les intervalles lorsque l'utilisateur quitte la page
    window.addEventListener('beforeunload', clearAllIntervals);
}

/**
 * Nettoie tous les intervalles de rafraîchissement
 */
function clearAllIntervals() {
    Object.values(refreshIntervals).forEach(interval => {
        if (interval) clearInterval(interval);
    });
}

/**
 * Récupère la liste des agents depuis l'API
 */
function fetchAgents() {
    fetch('/api/agents')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(agents => {
            updateAgentsList(agents);
            updateAgentsDropdown(agents);
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des agents:', error);
            showNotification('Erreur', 'Impossible de récupérer la liste des agents.', 'danger');
        });
}

/**
 * Met à jour l'affichage de la liste des agents
 */
function updateAgentsList(agents) {
    const agentsContainer = document.getElementById('agents-list');
    
    if (!agentsContainer) return;
    
    if (agents.length === 0) {
        agentsContainer.innerHTML = '<div class="placeholder">Aucun agent disponible.</div>';
        return;
    }
    
    let html = '';
    
    agents.forEach(agent => {
        html += `
            <div class="agent-card">
                <div class="agent-header">
                    <div class="agent-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="agent-name">${agent.name}</div>
                </div>
                <ul class="agent-capabilities">
                    ${agent.capabilities.map(capability => `<li>${capability}</li>`).join('')}
                </ul>
            </div>
        `;
    });
    
    agentsContainer.innerHTML = html;
}

/**
 * Met à jour les listes déroulantes d'agents
 */
function updateAgentsDropdown(agents) {
    const recipientDropdown = document.getElementById('recipient');
    
    if (recipientDropdown) {
        // Sauvegarder la sélection actuelle si elle existe
        const currentSelection = recipientDropdown.value;
        
        // Vider et reconstruire le dropdown
        recipientDropdown.innerHTML = '<option value="" disabled selected>Sélectionner un agent...</option>';
        
        agents.forEach(agent => {
            const option = document.createElement('option');
            option.value = agent.name;
            option.textContent = agent.name;
            recipientDropdown.appendChild(option);
        });
        
        // Restaurer la sélection si elle existe toujours
        if (currentSelection && agents.some(agent => agent.name === currentSelection)) {
            recipientDropdown.value = currentSelection;
        }
    }
}

/**
 * Récupère la liste des tâches depuis l'API
 */
function fetchTasks() {
    fetch('/api/tasks')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(tasks => {
            updateTasksList(tasks);
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des tâches:', error);
            showNotification('Erreur', 'Impossible de récupérer la liste des tâches.', 'danger');
        });
}

/**
 * Met à jour l'affichage de la liste des tâches
 */
function updateTasksList(tasks) {
    const tasksContainer = document.getElementById('tasks-list');
    
    if (!tasksContainer) return;
    
    if (tasks.length === 0) {
        tasksContainer.innerHTML = '<tr><td colspan="7" class="text-center">Aucune tâche disponible.</td></tr>';
        return;
    }
    
    let html = '';
    
    tasks.forEach(task => {
        const createdDate = new Date(task.created_at);
        const formattedDate = createdDate.toLocaleDateString() + ' ' + createdDate.toLocaleTimeString();
        
        html += `
            <tr>
                <td>${task.id}</td>
                <td>${task.description}</td>
                <td><span class="status-badge status-${task.status}">${task.status}</span></td>
                <td>${task.assigned_to}</td>
                <td><span class="priority-badge priority-${task.priority}">${task.priority}</span></td>
                <td>${formattedDate}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="showTaskDetails('${task.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tasksContainer.innerHTML = html;
}

/**
 * Affiche les détails d'une tâche dans un modal
 */
function showTaskDetails(taskId) {
    // Récupérer les détails de la tâche depuis l'API
    fetch(`/api/tasks/${taskId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(task => {
            // Mettre à jour le contenu du modal
            const modalTitle = document.getElementById('task-details-title');
            const modalContent = document.getElementById('task-details-content');
            
            modalTitle.textContent = `Tâche: ${task.id}`;
            
            const createdDate = new Date(task.created_at);
            const formattedDate = createdDate.toLocaleDateString() + ' ' + createdDate.toLocaleTimeString();
            
            let deadlineHtml = 'Aucune';
            if (task.deadline) {
                const deadlineDate = new Date(task.deadline);
                deadlineHtml = deadlineDate.toLocaleDateString() + ' ' + deadlineDate.toLocaleTimeString();
            }
            
            modalContent.innerHTML = `
                <div class="task-details">
                    <p><strong>Description:</strong> ${task.description}</p>
                    <p><strong>Statut:</strong> <span class="status-badge status-${task.status}">${task.status}</span></p>
                    <p><strong>Assigné à:</strong> ${task.assigned_to}</p>
                    <p><strong>Priorité:</strong> <span class="priority-badge priority-${task.priority}">${task.priority}</span></p>
                    <p><strong>Créé le:</strong> ${formattedDate}</p>
                    <p><strong>Date limite:</strong> ${deadlineHtml}</p>
                </div>
                <div class="mt-3">
                    <label class="form-label">Mettre à jour le statut:</label>
                    <select id="task-status-update" class="form-select">
                        <option value="PENDING" ${task.status === 'PENDING' ? 'selected' : ''}>En attente</option>
                        <option value="IN_PROGRESS" ${task.status === 'IN_PROGRESS' ? 'selected' : ''}>En cours</option>
                        <option value="COMPLETED" ${task.status === 'COMPLETED' ? 'selected' : ''}>Terminé</option>
                        <option value="FAILED" ${task.status === 'FAILED' ? 'selected' : ''}>Échoué</option>
                        <option value="DELEGATED" ${task.status === 'DELEGATED' ? 'selected' : ''}>Délégué</option>
                    </select>
                </div>
            `;
            
            // Configurer le bouton de mise à jour du statut
            document.getElementById('update-task-status').onclick = function() {
                const newStatus = document.getElementById('task-status-update').value;
                updateTaskStatus(taskId, newStatus);
            };
            
            // Afficher le modal
            const modal = new bootstrap.Modal(document.getElementById('task-details-modal'));
            modal.show();
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des détails de la tâche:', error);
            showNotification('Erreur', 'Impossible de récupérer les détails de la tâche.', 'danger');
        });
}

/**
 * Met à jour le statut d'une tâche
 */
function updateTaskStatus(taskId, status) {
    fetch(`/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: status })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            showNotification('Succès', `Le statut de la tâche ${taskId} a été mis à jour.`, 'success');
            
            // Fermer le modal
            const modalElement = document.getElementById('task-details-modal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
            
            // Rafraîchir la liste des tâches
            fetchTasks();
        })
        .catch(error => {
            console.error('Erreur lors de la mise à jour du statut:', error);
            showNotification('Erreur', 'Impossible de mettre à jour le statut de la tâche.', 'danger');
        });
}

/**
 * Récupère les logs depuis l'API
 */
function fetchLogs() {
    const logLevel = document.getElementById('log-level')?.value || 'ALL';
    
    fetch(`/api/logs?level=${logLevel}&limit=100`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(logs => {
            updateLogsDisplay(logs);
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des logs:', error);
            showNotification('Erreur', 'Impossible de récupérer les logs.', 'danger');
        });
}

/**
 * Met à jour l'affichage des logs
 */
function updateLogsDisplay(logs) {
    const logsContainer = document.getElementById('logs-content');
    
    if (!logsContainer) return;
    
    if (logs.length === 0) {
        logsContainer.textContent = 'Aucun log disponible.';
        return;
    }
    
    logsContainer.textContent = logs.join('');
    
    // Scroller vers le bas pour voir les logs les plus récents
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

/**
 * Envoie un message à un agent
 */
function sendMessage(recipient, content, priority, createTask) {
    const messageData = {
        recipient: recipient,
        content: content,
        priority: priority,
        create_task: createTask
    };
    
    fetch('/api/message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(messageData)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Réinitialiser le formulaire
            document.getElementById('message-form').reset();
            
            showNotification('Succès', `Message envoyé à ${recipient}.`, 'success');
            
            // Si une tâche a été créée, rafraîchir la liste des tâches
            if (data.task_id) {
                fetchTasks();
            }
        })
        .catch(error => {
            console.error('Erreur lors de l\'envoi du message:', error);
            showNotification('Erreur', 'Impossible d\'envoyer le message.', 'danger');
        });
}

/**
 * Récupère les statistiques globales depuis l'API
 */
function fetchStatistics() {
    fetch('/api/statistics')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(stats => {
            updateDashboardStats(stats);
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des statistiques:', error);
        });
}

/**
 * Met à jour les statistiques du tableau de bord
 */
function updateDashboardStats(stats) {
    // Mettre à jour les compteurs
    document.getElementById('agents-count').textContent = stats.agents_count || 0;
    document.getElementById('active-tasks-count').textContent = stats.active_tasks_count || 0;
    document.getElementById('messages-count').textContent = stats.messages_count || 0;
}

/**
 * Récupère les statistiques système depuis l'API
 */
function fetchSystemStats() {
    fetch('/api/system/stats')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(stats => {
            updateSystemStats(stats);
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des statistiques système:', error);
        });
}

/**
 * Met à jour les statistiques système dans l'interface
 */
function updateSystemStats(stats) {
    // Mettre à jour l'uptime
    document.getElementById('uptime').textContent = stats.uptime || '--';
    
    // Mettre à jour les métriques CPU
    const cpuProgress = document.getElementById('cpu-progress');
    const cpuValue = document.getElementById('cpu-value');
    if (cpuProgress && cpuValue) {
        const cpuPercent = stats.cpu_percent || 0;
        cpuProgress.style.width = `${cpuPercent}%`;
        cpuValue.textContent = `${cpuPercent}%`;
        
        // Changer la couleur en fonction de la charge
        if (cpuPercent > 80) {
            cpuProgress.className = 'progress-bar bg-danger';
        } else if (cpuPercent > 60) {
            cpuProgress.className = 'progress-bar bg-warning';
        } else {
            cpuProgress.className = 'progress-bar bg-success';
        }
    }
    
    // Mettre à jour les métriques mémoire
    const memoryProgress = document.getElementById('memory-progress');
    const memoryValue = document.getElementById('memory-value');
    if (memoryProgress && memoryValue) {
        const memoryPercent = stats.memory_percent || 0;
        memoryProgress.style.width = `${memoryPercent}%`;
        memoryValue.textContent = `${memoryPercent}%`;
        
        // Changer la couleur en fonction de la charge
        if (memoryPercent > 80) {
            memoryProgress.className = 'progress-bar bg-danger';
        } else if (memoryPercent > 60) {
            memoryProgress.className = 'progress-bar bg-warning';
        } else {
            memoryProgress.className = 'progress-bar bg-success';
        }
    }
    
    // Mettre à jour les métriques disque
    const diskProgress = document.getElementById('disk-progress');
    const diskValue = document.getElementById('disk-value');
    if (diskProgress && diskValue) {
        const diskPercent = stats.disk_percent || 0;
        diskProgress.style.width = `${diskPercent}%`;
        diskValue.textContent = `${diskPercent}%`;
        
        // Changer la couleur en fonction de la charge
        if (diskPercent > 80) {
            diskProgress.className = 'progress-bar bg-danger';
        } else if (diskPercent > 60) {
            diskProgress.className = 'progress-bar bg-warning';
        } else {
            diskProgress.className = 'progress-bar bg-success';
        }
    }
    
    // Mettre à jour l'indicateur de statut
    updateStatusIndicator(stats);
}

/**
 * Met à jour l'indicateur de statut du système
 */
function updateStatusIndicator(stats) {
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (!statusIndicator || !statusText) return;
    
    // Considérer le système en difficulté si CPU ou mémoire > 85%
    if ((stats.cpu_percent && stats.cpu_percent > 85) || 
        (stats.memory_percent && stats.memory_percent > 85)) {
        statusIndicator.className = 'status-indicator warning';
        statusText.textContent = 'Charge élevée';
    }
    // Considérer le système hors ligne si les statistiques sont manquantes
    else if (!stats.cpu_percent || !stats.memory_percent) {
        statusIndicator.className = 'status-indicator offline';
        statusText.textContent = 'Hors ligne';
    } 
    // Sinon, le système est en ligne et fonctionnel
    else {
        statusIndicator.className = 'status-indicator online';
        statusText.textContent = 'En ligne';
    }
}

/**
 * Récupère les activités récentes depuis l'API
 */
function fetchActivities() {
    fetch('/api/activities')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(activities => {
            updateActivitiesList(activities);
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des activités:', error);
        });
}

/**
 * Met à jour la liste des activités récentes
 */
function updateActivitiesList(activities) {
    const activitiesList = document.getElementById('activities-list');
    
    if (!activitiesList) return;
    
    if (activities.length === 0) {
        activitiesList.innerHTML = '<li class="placeholder">Aucune activité récente.</li>';
        return;
    }
    
    let html = '';
    
    activities.forEach(activity => {
        const date = new Date(activity.timestamp);
        const timeAgo = getTimeAgo(date);
        
        let icon = '';
        if (activity.type === 'message') {
            icon = '<i class="fas fa-comment-dots"></i>';
        } else if (activity.type === 'task') {
            icon = '<i class="fas fa-tasks"></i>';
        }
        
        html += `
            <li>
                <div>${icon} <span class="activity-title">${activity.description}</span></div>
                <div class="activity-details">${activity.details}</div>
                <div class="activity-time">${timeAgo}</div>
            </li>
        `;
    });
    
    activitiesList.innerHTML = html;
}

/**
 * Calcule le temps écoulé depuis une date
 */
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    let interval = Math.floor(seconds / 31536000);
    if (interval > 1) return interval + ' ans';
    
    interval = Math.floor(seconds / 2592000);
    if (interval > 1) return interval + ' mois';
    
    interval = Math.floor(seconds / 86400);
    if (interval > 1) return interval + ' jours';
    if (interval === 1) return 'hier';
    
    interval = Math.floor(seconds / 3600);
    if (interval > 1) return interval + ' heures';
    if (interval === 1) return '1 heure';
    
    interval = Math.floor(seconds / 60);
    if (interval > 1) return interval + ' minutes';
    if (interval === 1) return '1 minute';
    
    return 'à l\'instant';
}

/**
 * Affiche une notification à l'utilisateur
 */
function showNotification(title, message, type = 'info') {
    // Définir les classes de couleur selon le type
    let bgClass = 'bg-info';
    if (type === 'success') bgClass = 'bg-success';
    if (type === 'warning') bgClass = 'bg-warning';
    if (type === 'danger') bgClass = 'bg-danger';
    
    // Mettre à jour le contenu du toast
    const toastEl = document.getElementById('notification-toast');
    const toastTitle = document.getElementById('toast-title');
    const toastTime = document.getElementById('toast-time');
    const toastMessage = document.getElementById('toast-message');
    
    if (toastEl && toastTitle && toastTime && toastMessage) {
        // Définir le contenu
        toastTitle.textContent = title;
        toastTime.textContent = new Date().toLocaleTimeString();
        toastMessage.textContent = message;
        
        // Appliquer la classe de couleur
        toastEl.className = `toast ${bgClass} text-white`;
        
        // Afficher le toast
        const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
        toast.show();
    } else {
        // Fallback si le toast n'est pas disponible
        console.log(`${type.toUpperCase()}: ${title} - ${message}`);
    }
} 