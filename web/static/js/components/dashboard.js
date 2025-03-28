/**
 * dashboard.js - Composant de gestion du tableau de bord
 * Gère l'affichage et la mise à jour du tableau de bord
 */

const Dashboard = {
    /**
     * Minuteur pour le rafraîchissement automatique
     */
    refreshTimer: null,
    
    /**
     * Initialise le tableau de bord
     */
    init: () => {
        console.log('🖥️ Initialisation du tableau de bord');
        
        // Initialiser les minuteurs de rafraîchissement
        Dashboard.startAutoRefresh();
        
        // Initialiser les gestionnaires d'événements
        Dashboard.initEventListeners();
        
        // Charger les données initiales
        Dashboard.refreshAll();
    },
    
    /**
     * Initialise les gestionnaires d'événements
     */
    initEventListeners: () => {
        // Bouton de rafraîchissement manuel
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                // Ajouter une classe pour l'animation de rotation
                refreshBtn.classList.add('spin');
                
                // Rafraîchir les données
                Dashboard.refreshAll().then(() => {
                    // Mettre à jour l'heure de dernière mise à jour
                    Dashboard.updateLastUpdateTime();
                    
                    // Arrêter l'animation après un délai
                    setTimeout(() => {
                        refreshBtn.classList.remove('spin');
                    }, 800);
                });
            });
        }
        
        // Bouton de rafraîchissement des agents
        const refreshAgentsBtn = document.getElementById('refresh-agents-btn');
        if (refreshAgentsBtn) {
            refreshAgentsBtn.addEventListener('click', () => {
                refreshAgentsBtn.classList.add('spin');
                
                Dashboard.loadAgents().then(() => {
                    setTimeout(() => {
                        refreshAgentsBtn.classList.remove('spin');
                    }, 800);
                });
            });
        }
        
        // Filtrer les logs par niveau
        document.querySelectorAll('.log-level-filter').forEach(filter => {
            filter.addEventListener('click', (e) => {
                e.preventDefault();
                const level = filter.getAttribute('data-level');
                
                // Mettre à jour l'élément sélectionné
                document.getElementById('current-log-level').textContent = filter.textContent;
                
                // Charger les logs avec le niveau sélectionné
                Dashboard.loadLogs(level);
            });
        });
    },
    
    /**
     * Démarre le rafraîchissement automatique
     */
    startAutoRefresh: () => {
        // Arrêter le minuteur existant si nécessaire
        Dashboard.stopAutoRefresh();
        
        // Créer un nouveau minuteur
        Dashboard.refreshTimer = setInterval(() => {
            Dashboard.refreshStats();
            Dashboard.updateLastUpdateTime();
        }, CONFIG.ui.dashboard.refreshInterval);
    },
    
    /**
     * Arrête le rafraîchissement automatique
     */
    stopAutoRefresh: () => {
        if (Dashboard.refreshTimer) {
            clearInterval(Dashboard.refreshTimer);
            Dashboard.refreshTimer = null;
        }
    },
    
    /**
     * Rafraîchit toutes les données du tableau de bord
     */
    refreshAll: async () => {
        try {
            // Rafraîchir les données
            await Promise.all([
                Dashboard.refreshStats(),
                Dashboard.loadAgents(),
                Dashboard.loadTasks(),
                Dashboard.loadLogs()
            ]);
            
            // Mettre à jour l'heure de dernière mise à jour
            Dashboard.updateLastUpdateTime();
            
            return true;
        } catch (error) {
            console.error('Erreur lors du rafraîchissement du tableau de bord:', error);
            UI.toast.show('Erreur lors du rafraîchissement des données', 'error');
            return false;
        }
    },
    
    /**
     * Rafraîchit les statistiques système
     */
    refreshStats: async () => {
        try {
            const stats = await API.Monitoring.getStats();
            
            // Mettre à jour les graphiques si disponibles
            if (window.Charts) {
                Charts.updateSystemCharts(stats);
            } else {
                // Mise à jour manuelle des métriques
                document.getElementById('cpu-value').textContent = Math.round(stats.cpu.usage);
                document.getElementById('cpu-bar').style.width = `${stats.cpu.usage}%`;
                
                document.getElementById('ram-value').textContent = Math.round(stats.memory.percent);
                document.getElementById('ram-bar').style.width = `${stats.memory.percent}%`;
                
                if (stats.gpu) {
                    document.getElementById('gpu-value').textContent = Math.round(stats.gpu.usage);
                    document.getElementById('gpu-bar').style.width = `${stats.gpu.usage}%`;
                } else {
                    document.getElementById('gpu-value').textContent = 'N/A';
                }
                
                document.getElementById('disk-value').textContent = Math.round(stats.disk.percent);
                document.getElementById('disk-bar').style.width = `${stats.disk.percent}%`;
            }
            
            return stats;
        } catch (error) {
            console.error('Erreur lors du rafraîchissement des statistiques:', error);
            throw error;
        }
    },
    
    /**
     * Charge la liste des agents
     */
    loadAgents: async () => {
        try {
            // Afficher l'état de chargement
            const agentsContainer = document.getElementById('agents-activity');
            if (agentsContainer) {
                agentsContainer.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Chargement des agents...</p>
                    </div>
                `;
            }
            
            // Récupérer les agents
            const agents = await API.Agents.getAll();
            
            // Mettre à jour le widget des agents
            if (agentsContainer) {
                if (agents.length === 0) {
                    agentsContainer.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-robot"></i>
                            <p>Aucun agent disponible</p>
                        </div>
                    `;
                } else {
                    // Créer la liste des agents
                    agentsContainer.innerHTML = `
                        <div class="agents-list">
                            ${agents.map(agent => `
                                <div class="agent-item">
                                    <div class="agent-icon">
                                        <i class="fas fa-robot"></i>
                                    </div>
                                    <div class="agent-info">
                                        <div class="agent-name">${agent.name}</div>
                                        <div class="agent-status">
                                            <span class="status-indicator status-${agent.status.toLowerCase()}"></span>
                                            <span>${CONFIG.agentStatus[agent.status]?.label || agent.status}</span>
                                        </div>
                                    </div>
                                    <div class="agent-actions">
                                        <button class="btn btn-icon btn-sm" title="Détails">
                                            <i class="fas fa-info-circle"></i>
                                        </button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    `;
                }
            }
            
            // Mettre à jour le graphique d'activité des agents
            if (window.Charts && Charts.instances['agent-activity-chart']) {
                const activeAgents = agents.filter(agent => agent.status === 'ACTIVE' || agent.status === 'BUSY');
                
                if (activeAgents.length > 0) {
                    const labels = activeAgents.map(agent => agent.name);
                    const values = activeAgents.map(agent => agent.status === 'BUSY' ? Math.random() * 50 + 50 : Math.random() * 30 + 10);
                    
                    Charts.updateBarChart('agent-activity-chart', values, labels);
                } else {
                    Charts.updateBarChart('agent-activity-chart', [], []);
                }
            }
            
            // Mettre à jour le compteur d'agents dans la sidebar
            UI.updateSidebarCounts({ agents: agents.length });
            
            return agents;
        } catch (error) {
            console.error('Erreur lors du chargement des agents:', error);
            
            const agentsContainer = document.getElementById('agents-activity');
            if (agentsContainer) {
                agentsContainer.innerHTML = `
                    <div class="error-state">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Erreur lors du chargement des agents</p>
                    </div>
                `;
            }
            
            throw error;
        }
    },
    
    /**
     * Charge la liste des tâches
     */
    loadTasks: async () => {
        try {
            // Afficher l'état de chargement
            const tasksContainer = document.getElementById('current-tasks');
            if (tasksContainer) {
                tasksContainer.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Chargement des tâches...</p>
                    </div>
                `;
            }
            
            // Récupérer les tâches
            const tasks = await API.Tasks.getAll();
            
            // Mettre à jour le widget des tâches
            if (tasksContainer) {
                if (tasks.length === 0) {
                    tasksContainer.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-tasks"></i>
                            <p>Aucune tâche en cours</p>
                        </div>
                    `;
                } else {
                    // Limiter aux 5 tâches les plus récentes
                    const recentTasks = tasks.slice(0, 5);
                    
                    // Créer la liste des tâches
                    tasksContainer.innerHTML = `
                        <div class="tasks-list">
                            ${recentTasks.map(task => `
                                <div class="task-item">
                                    <div class="task-icon">
                                        <i class="fas fa-${CONFIG.taskStatus[task.status]?.icon || 'file-alt'}"></i>
                                    </div>
                                    <div class="task-info">
                                        <div class="task-description">${task.description}</div>
                                        <div class="task-details">
                                            <span class="task-status status-${task.status.toLowerCase()}">
                                                ${CONFIG.taskStatus[task.status]?.label || task.status}
                                            </span>
                                            <span class="task-agent">Agent: ${task.agent || 'Non assigné'}</span>
                                        </div>
                                    </div>
                                    <div class="task-actions">
                                        <button class="btn btn-icon btn-sm" title="Détails">
                                            <i class="fas fa-info-circle"></i>
                                        </button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    `;
                }
            }
            
            // Mettre à jour le graphique de distribution des tâches
            if (window.Charts && Charts.instances['task-distribution-chart']) {
                // Compter les tâches par statut
                const counts = {
                    PENDING: 0,
                    RUNNING: 0,
                    COMPLETED: 0,
                    FAILED: 0,
                    CANCELLED: 0
                };
                
                tasks.forEach(task => {
                    if (counts[task.status] !== undefined) {
                        counts[task.status]++;
                    }
                });
                
                // Mettre à jour le graphique
                Charts.updatePieChart('task-distribution-chart', [
                    counts.PENDING,
                    counts.RUNNING,
                    counts.COMPLETED,
                    counts.FAILED,
                    counts.CANCELLED
                ]);
            }
            
            // Mettre à jour le compteur de tâches dans la sidebar
            UI.updateSidebarCounts({ tasks: tasks.length });
            
            return tasks;
        } catch (error) {
            console.error('Erreur lors du chargement des tâches:', error);
            
            const tasksContainer = document.getElementById('current-tasks');
            if (tasksContainer) {
                tasksContainer.innerHTML = `
                    <div class="error-state">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Erreur lors du chargement des tâches</p>
                    </div>
                `;
            }
            
            throw error;
        }
    },
    
    /**
     * Charge les logs système
     * @param {string} level - Niveau de log à afficher (all, info, warning, error, debug)
     */
    loadLogs: async (level = 'all') => {
        try {
            // Afficher l'état de chargement
            const logsContainer = document.getElementById('system-logs');
            if (logsContainer) {
                logsContainer.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Chargement des logs...</p>
                    </div>
                `;
            }
            
            // Récupérer les logs
            const logs = await API.Logs.getRecent(CONFIG.ui.dashboard.maxLogEntries, level !== 'all' ? level : undefined);
            
            // Mettre à jour le widget des logs
            if (logsContainer) {
                if (logs.length === 0) {
                    logsContainer.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-list"></i>
                            <p>Aucun log disponible</p>
                        </div>
                    `;
                } else {
                    // Créer la liste des logs
                    logsContainer.innerHTML = logs.map(log => `
                        <div class="log-entry log-${log.level.toLowerCase()}">
                            <div class="log-time">${new Date(log.timestamp).toLocaleTimeString()}</div>
                            <div class="log-level">${log.level}</div>
                            <div class="log-component">${log.component || 'system'}</div>
                            <div class="log-message">${log.message}</div>
                        </div>
                    `).join('');
                }
            }
            
            return logs;
        } catch (error) {
            console.error('Erreur lors du chargement des logs:', error);
            
            const logsContainer = document.getElementById('system-logs');
            if (logsContainer) {
                logsContainer.innerHTML = `
                    <div class="error-state">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Erreur lors du chargement des logs</p>
                    </div>
                `;
            }
            
            throw error;
        }
    },
    
    /**
     * Met à jour l'heure de dernière mise à jour
     */
    updateLastUpdateTime: () => {
        const timeElement = document.getElementById('last-update-time');
        if (timeElement) {
            const now = new Date();
            timeElement.textContent = now.toLocaleTimeString();
            timeElement.setAttribute('datetime', now.toISOString());
        }
    }
};

// Ajouter le composant Dashboard à l'objet global Components
window.Components = window.Components || {};
window.Components.Dashboard = Dashboard; 