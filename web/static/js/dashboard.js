/**
 * dashboard.js - Fonctionnalités spécifiques au tableau de bord
 * Gère l'initialisation et la mise à jour des composants du dashboard
 */

const Dashboard = {
    // Stockage des données locales
    data: {
        agents: [],
        tasks: [],
        stats: {},
        charts: {}
    },
    
    /**
     * Initialise le tableau de bord et ses composants
     */
    init: () => {
        // S'arrêter si nous ne sommes pas sur la page dashboard
        if (!document.querySelector('.dashboard')) return;
        
        console.log('🔍 Initialisation du tableau de bord');
        
        // Initialisation des composants
        Dashboard.initMetrics();
        Dashboard.initCharts();
        Dashboard.initRefreshHandlers();
        Dashboard.initExport();
        
        // Chargement initial des données
        Dashboard.loadDashboardData();
        
        // Configurer le rafraîchissement périodique
        Dashboard.startAutoRefresh();
    },
    
    /**
     * Initialise les métriques principales
     */
    initMetrics: () => {
        // Ajouter les gestionnaires d'événements pour les filtres de date
        const timeRange = document.getElementById('time-range');
        if (timeRange) {
            timeRange.addEventListener('change', () => {
                Dashboard.loadDashboardData();
            });
        }
    },
    
    /**
     * Initialise les graphiques avec Chart.js
     */
    initCharts: () => {
        // Vérifier si Chart.js est disponible
        if (typeof Chart === 'undefined') {
            console.error('Chart.js n\'est pas chargé. Les graphiques ne seront pas disponibles.');
            return;
        }
        
        // Créer les graphiques de performance
        const charts = ['cpu', 'ram', 'gpu', 'disk'];
        
        charts.forEach(metric => {
            const canvas = document.getElementById(`${metric}-chart`);
            if (!canvas) return;
            
            // Configuration du graphique
            const ctx = canvas.getContext('2d');
            Dashboard.data.charts[metric] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: Array(10).fill(''),
                    datasets: [{
                        label: metric.toUpperCase(),
                        data: Array(10).fill(0),
                        borderColor: CONFIG.charts.colors[metric],
                        backgroundColor: `${CONFIG.charts.colors[metric]}33`,
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    ...CONFIG.charts.options,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: value => `${value}%`
                            }
                        },
                        x: {
                            display: false
                        }
                    }
                }
            });
        });
    },
    
    /**
     * Initialise les gestionnaires d'événements pour les boutons de rafraîchissement
     */
    initRefreshHandlers: () => {
        // Gestionnaire global
        window.addEventListener('app:refresh', () => {
            Dashboard.loadDashboardData();
        });
        
        // Gestionnaires individuels pour chaque carte
        document.querySelectorAll('.dashboard-card .card-actions button[title="Rafraîchir"]').forEach(btn => {
            btn.addEventListener('click', () => {
                const card = btn.closest('.dashboard-card');
                
                // Ajouter l'animation de chargement
                btn.classList.add('spin');
                
                // Déterminer quelle section rafraîchir en fonction de l'ID du container
                if (card.querySelector('#agents-activity')) {
                    Dashboard.loadAgentsActivity();
                } else if (card.querySelector('#current-tasks')) {
                    Dashboard.loadCurrentTasks();
                } else if (card.querySelector('#recent-messages')) {
                    Dashboard.loadRecentMessages();
                } else if (card.querySelector('#system-logs')) {
                    Dashboard.loadSystemLogs();
                }
                
                // Arrêter l'animation après 1s
                setTimeout(() => {
                    btn.classList.remove('spin');
                }, 1000);
            });
        });
        
        // Gestionnaire pour le changement de plage dans les performances
        const perfRange = document.getElementById('perf-time-range');
        if (perfRange) {
            perfRange.addEventListener('change', () => {
                Dashboard.loadPerformanceData(perfRange.value);
            });
        }
        
        // Gestionnaire pour le filtre de logs
        const logLevel = document.getElementById('log-level');
        if (logLevel) {
            logLevel.addEventListener('change', () => {
                Dashboard.loadSystemLogs(logLevel.value);
            });
        }
    },
    
    /**
     * Initialise l'exportation des données du tableau de bord
     */
    initExport: () => {
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                // Préparer les données à exporter
                const exportData = {
                    generatedAt: new Date().toISOString(),
                    metrics: {
                        activeAgents: document.getElementById('active-agents-count').textContent,
                        pendingTasks: document.getElementById('pending-tasks-count').textContent,
                        completedTasks: document.getElementById('completed-tasks-count').textContent,
                        systemLoad: document.getElementById('system-load').textContent
                    },
                    performance: {
                        cpu: document.getElementById('cpu-value').textContent,
                        ram: document.getElementById('ram-value').textContent,
                        gpu: document.getElementById('gpu-value').textContent,
                        disk: document.getElementById('disk-value').textContent
                    },
                    agents: Dashboard.data.agents,
                    tasks: Dashboard.data.tasks
                };
                
                // Convertir en JSON
                const jsonStr = JSON.stringify(exportData, null, 2);
                const blob = new Blob([jsonStr], { type: 'application/json' });
                
                // Créer un lien de téléchargement
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `paradis-ia-dashboard-${new Date().toISOString().slice(0, 10)}.json`;
                document.body.appendChild(a);
                a.click();
                
                // Nettoyer
                setTimeout(() => {
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }, 100);
                
                // Notification
                Utils.toast.show('Rapport du tableau de bord exporté avec succès', 'success');
            });
        }
    },
    
    /**
     * Charge toutes les données du tableau de bord
     */
    loadDashboardData: async () => {
        Promise.all([
            Dashboard.loadMetrics(),
            Dashboard.loadAgentsActivity(),
            Dashboard.loadCurrentTasks(),
            Dashboard.loadPerformanceData(),
            Dashboard.loadRecentMessages(),
            Dashboard.loadSystemLogs(),
            Dashboard.loadRealtimeMetrics()
        ]).then(() => {
            UI.updateLastUpdate();
        }).catch(error => {
            console.error('Erreur lors du chargement des données du tableau de bord', error);
            Utils.toast.show('Erreur lors du chargement des données', 'error');
        });
    },
    
    /**
     * Charge les métriques principales
     */
    loadMetrics: async () => {
        try {
            // Récupérer les agents
            const agents = await API.Agents.getAll();
            const activeAgents = agents.filter(a => a.status === 'ACTIVE').length;
            
            // Récupérer les tâches
            const allTasks = await API.Tasks.getAll();
            const pendingTasks = allTasks.filter(t => t.status === 'PENDING').length;
            const completedTasks = allTasks.filter(t => t.status === 'COMPLETED').length;
            
            // Récupérer les stats système
            const stats = await API.System.getStats();
            
            // Mettre à jour les compteurs
            document.getElementById('active-agents-count').textContent = activeAgents;
            document.getElementById('pending-tasks-count').textContent = pendingTasks;
            document.getElementById('completed-tasks-count').textContent = completedTasks;
            document.getElementById('system-load').textContent = `${stats.cpu}%`;
            
            // Stocker pour référence
            Dashboard.data.stats = stats;
            
            // Mettre à jour la sidebar aussi
            Dashboard.updateSidebarStats(stats);
            
            return { agents, allTasks, stats };
        } catch (error) {
            console.error('Erreur lors du chargement des métriques', error);
            throw error;
        }
    },
    
    /**
     * Charge l'activité des agents
     */
    loadAgentsActivity: async () => {
        const container = document.getElementById('agents-activity');
        if (!container) return;
        
        try {
            Utils.dom.createLoader(container, 'Chargement des agents...');
            
            const agents = await API.Agents.getAll();
            Dashboard.data.agents = agents;
            
            if (agents.length === 0) {
                Utils.dom.showEmpty(container, 'Aucun agent disponible');
                return agents;
            }
            
            // Générer la liste d'agents avec leur statut
            let html = '<div class="agent-list">';
            
            agents.forEach(agent => {
                const status = agent.status || 'UNKNOWN';
                const statusConfig = CONFIG.agentStatus[status] || {
                    label: 'Inconnu',
                    color: 'var(--color-inactive)',
                    icon: 'question-circle'
                };
                
                html += `
                    <div class="agent-item">
                        <div class="agent-icon" style="background-color: ${statusConfig.color}">
                            <i class="fas fa-${statusConfig.icon}"></i>
                        </div>
                        <div class="agent-info">
                            <div class="agent-name">${agent.name || 'Agent sans nom'}</div>
                            <div class="agent-status">${statusConfig.label}</div>
                        </div>
                        <div class="agent-actions">
                            <button class="btn btn-sm" title="Détails">
                                <i class="fas fa-info-circle"></i>
                            </button>
                            <button class="btn btn-sm" title="Assigner une tâche">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            container.innerHTML = html;
            
            // Mettre à jour le compteur dans la sidebar
            UI.updateSidebarCounts({ agents: agents.length });
            
            return agents;
        } catch (error) {
            Utils.dom.showError(container, 'Erreur lors du chargement des agents');
            console.error('Erreur lors du chargement des agents', error);
            throw error;
        }
    },
    
    /**
     * Charge les tâches en cours
     */
    loadCurrentTasks: async () => {
        const container = document.getElementById('current-tasks');
        if (!container) return;
        
        try {
            Utils.dom.createLoader(container, 'Chargement des tâches...');
            
            const tasks = await API.Tasks.getAll();
            Dashboard.data.tasks = tasks;
            
            if (tasks.length === 0) {
                Utils.dom.showEmpty(container, 'Aucune tâche en cours');
                return tasks;
            }
            
            // Filtrer les tâches actives et les trier par priorité
            const activeTasks = tasks
                .filter(t => t.status === 'PENDING' || t.status === 'RUNNING')
                .sort((a, b) => {
                    const priorityA = CONFIG.taskPriority[a.priority]?.value || 0;
                    const priorityB = CONFIG.taskPriority[b.priority]?.value || 0;
                    return priorityB - priorityA;
                })
                .slice(0, 5); // Limiter à 5 tâches
            
            if (activeTasks.length === 0) {
                Utils.dom.showEmpty(container, 'Aucune tâche active');
                return tasks;
            }
            
            // Générer la liste des tâches
            let html = '<div class="task-list">';
            
            activeTasks.forEach(task => {
                const status = task.status || 'PENDING';
                const statusConfig = CONFIG.taskStatus[status] || {
                    label: 'En attente',
                    color: 'var(--color-pending)',
                    icon: 'clock'
                };
                
                const priority = task.priority || 'MEDIUM';
                const priorityConfig = CONFIG.taskPriority[priority] || {
                    label: 'Moyenne',
                    color: 'var(--color-medium)'
                };
                
                const agentName = task.agent_name || 'Non assignée';
                
                html += `
                    <div class="task-item" data-id="${task.id || ''}">
                        <div class="task-header">
                            <div class="task-status" style="color: ${statusConfig.color}">
                                <i class="fas fa-${statusConfig.icon}"></i>
                                <span>${statusConfig.label}</span>
                            </div>
                            <div class="task-priority" style="background-color: ${priorityConfig.color}">
                                ${priorityConfig.label}
                            </div>
                        </div>
                        <div class="task-description">${task.description || 'Sans description'}</div>
                        <div class="task-footer">
                            <div class="task-agent">
                                <i class="fas fa-robot"></i>
                                <span>${agentName}</span>
                            </div>
                            <div class="task-actions">
                                <button class="btn btn-sm btn-status" data-task-id="${task.id || ''}" title="Changer le statut">
                                    <i class="fas fa-sync-alt"></i>
                                </button>
                                <button class="btn btn-sm" title="Détails">
                                    <i class="fas fa-info-circle"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            container.innerHTML = html;
            
            // Ajouter les gestionnaires pour les boutons de statut
            container.querySelectorAll('.btn-status').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    const taskId = btn.getAttribute('data-task-id');
                    if (!taskId) return;
                    
                    // Afficher une modale de changement de statut (simplifié)
                    const newStatus = window.prompt('Nouveau statut (RUNNING, COMPLETED, FAILED, CANCELLED):', 'COMPLETED');
                    if (!newStatus) return;
                    
                    try {
                        await API.Tasks.updateStatus(taskId, newStatus);
                        Utils.toast.show('Statut de la tâche mis à jour', 'success');
                        
                        // Rafraîchir les tâches
                        Dashboard.loadCurrentTasks();
                    } catch (error) {
                        Utils.toast.show('Erreur lors de la mise à jour du statut', 'error');
                        console.error('Erreur lors de la mise à jour du statut', error);
                    }
                });
            });
            
            // Mettre à jour le compteur dans la sidebar
            UI.updateSidebarCounts({ tasks: tasks.length });
            
            return tasks;
        } catch (error) {
            Utils.dom.showError(container, 'Erreur lors du chargement des tâches');
            console.error('Erreur lors du chargement des tâches', error);
            throw error;
        }
    },
    
    /**
     * Charge les données de performance
     * @param {string} timeRange - Plage de temps à charger (realtime, 1h, 24h)
     */
    loadPerformanceData: async (timeRange = 'realtime') => {
        try {
            let data;
            
            if (timeRange === 'realtime') {
                data = await API.Monitoring.getRealtime();
            } else {
                data = await API.Monitoring.getHistory({ timeRange: timeRange });
            }
            
            // Mettre à jour les valeurs actuelles
            document.getElementById('cpu-value').textContent = `${data.cpu}%`;
            document.getElementById('ram-value').textContent = `${data.ram}%`;
            document.getElementById('gpu-value').textContent = `${data.gpu}%`;
            document.getElementById('disk-value').textContent = `${data.disk}%`;
            
            // Mettre à jour les graphiques
            if (Dashboard.data.charts) {
                ['cpu', 'ram', 'gpu', 'disk'].forEach(metric => {
                    const chart = Dashboard.data.charts[metric];
                    if (!chart) return;
                    
                    // Ajouter la nouvelle valeur et supprimer la plus ancienne
                    chart.data.datasets[0].data.push(data[metric]);
                    chart.data.datasets[0].data.shift();
                    
                    // Ajouter un timestamp et supprimer le plus ancien
                    const now = new Date();
                    chart.data.labels.push(now.getHours() + ':' + now.getMinutes().toString().padStart(2, '0'));
                    chart.data.labels.shift();
                    
                    // Mettre à jour le graphique
                    chart.update();
                });
            }
            
            // Mettre à jour la sidebar aussi
            Dashboard.updateSidebarStats(data);
            
            return data;
        } catch (error) {
            console.error('Erreur lors du chargement des données de performance', error);
            throw error;
        }
    },
    
    /**
     * Charge les messages récents
     */
    loadRecentMessages: async () => {
        const container = document.getElementById('recent-messages');
        if (!container) return;
        
        try {
            Utils.dom.createLoader(container, 'Chargement des messages...');
            
            const messages = await API.Messages.getAll();
            
            if (messages.length === 0) {
                Utils.dom.showEmpty(container, 'Aucun message récent');
                return messages;
            }
            
            // Trier par date et limiter à 5 messages
            const recentMessages = messages
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
                .slice(0, 5);
            
            // Générer la liste des messages
            let html = '<div class="message-list">';
            
            recentMessages.forEach(msg => {
                const time = Utils.format.timeAgo(msg.timestamp);
                
                html += `
                    <div class="message-item">
                        <div class="message-sender">
                            <i class="fas fa-${msg.from_type === 'user' ? 'user' : 'robot'}"></i>
                            <span>${msg.from || 'Inconnu'}</span>
                        </div>
                        <div class="message-content">${msg.content || ''}</div>
                        <div class="message-footer">
                            <div class="message-time">${time}</div>
                            <div class="message-recipient">
                                À: ${msg.to || 'Tous'}
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            container.innerHTML = html;
            
            // Initialiser la fonction d'envoi rapide
            Dashboard.initQuickMessage();
            
            return messages;
        } catch (error) {
            Utils.dom.showError(container, 'Erreur lors du chargement des messages');
            console.error('Erreur lors du chargement des messages', error);
            throw error;
        }
    },
    
    /**
     * Initialise le formulaire d'envoi rapide de message
     */
    initQuickMessage: async () => {
        const agentSelect = document.getElementById('quick-message-agent');
        const messageInput = document.getElementById('quick-message-input');
        const sendButton = document.getElementById('quick-message-send');
        
        if (!agentSelect || !messageInput || !sendButton) return;
        
        // Vider et remplir le select avec les agents
        agentSelect.innerHTML = '<option value="" disabled selected>Sélectionner un destinataire</option>';
        
        try {
            // Utiliser les agents déjà chargés si disponibles
            const agents = Dashboard.data.agents.length > 0 ? 
                Dashboard.data.agents : 
                await API.Agents.getAll();
            
            agents.forEach(agent => {
                const option = document.createElement('option');
                option.value = agent.id || '';
                option.textContent = agent.name || 'Agent sans nom';
                agentSelect.appendChild(option);
            });
            
            // Gestionnaire d'envoi
            sendButton.addEventListener('click', async () => {
                const agentId = agentSelect.value;
                const content = messageInput.value.trim();
                
                if (!agentId || !content) {
                    Utils.toast.show('Veuillez sélectionner un destinataire et saisir un message', 'warning');
                    return;
                }
                
                try {
                    await API.Messages.send({
                        to: agentId,
                        content: content,
                        from_type: 'user',
                        from: 'Utilisateur'
                    });
                    
                    // Réinitialiser le formulaire
                    messageInput.value = '';
                    agentSelect.selectedIndex = 0;
                    
                    // Notification et rafraîchissement
                    Utils.toast.show('Message envoyé avec succès', 'success');
                    Dashboard.loadRecentMessages();
                } catch (error) {
                    Utils.toast.show('Erreur lors de l\'envoi du message', 'error');
                    console.error('Erreur lors de l\'envoi du message', error);
                }
            });
            
            // Permettre l'envoi avec Entrée
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendButton.click();
                }
            });
        } catch (error) {
            console.error('Erreur lors de l\'initialisation du formulaire de message', error);
        }
    },
    
    /**
     * Charge les logs système
     * @param {string} level - Niveau de log à filtrer (all, error, warning, info)
     */
    loadSystemLogs: async (level = 'all') => {
        const container = document.getElementById('system-logs');
        if (!container) return;
        
        try {
            Utils.dom.createLoader(container, 'Chargement des logs...');
            
            const options = level !== 'all' ? { level: level.toUpperCase() } : {};
            const logs = await API.System.getLogs(options);
            
            if (logs.length === 0) {
                Utils.dom.showEmpty(container, 'Aucun log disponible');
                return logs;
            }
            
            // Trier par date et limiter à 5 logs
            const recentLogs = logs
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
                .slice(0, 5);
            
            // Générer la liste des logs
            let html = '<div class="log-list">';
            
            recentLogs.forEach(log => {
                const logLevel = log.level || 'INFO';
                const levelConfig = CONFIG.logLevels[logLevel] || {
                    label: 'Info',
                    color: 'var(--color-info)',
                    icon: 'info-circle'
                };
                
                const time = Utils.format.timeAgo(log.timestamp);
                
                html += `
                    <div class="log-item ${logLevel.toLowerCase()}">
                        <div class="log-level" style="color: ${levelConfig.color}">
                            <i class="fas fa-${levelConfig.icon}"></i>
                            <span>${levelConfig.label}</span>
                        </div>
                        <div class="log-content">${log.message || ''}</div>
                        <div class="log-footer">
                            <div class="log-time">${time}</div>
                            <div class="log-component">${log.component || 'système'}</div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            container.innerHTML = html;
            
            return logs;
        } catch (error) {
            Utils.dom.showError(container, 'Erreur lors du chargement des logs');
            console.error('Erreur lors du chargement des logs', error);
            throw error;
        }
    },
    
    /**
     * Charge les métriques en temps réel
     */
    loadRealtimeMetrics: async () => {
        try {
            const data = await API.Monitoring.getRealtime();
            
            // Mettre à jour les métriques en temps réel
            document.getElementById('avg-response-time').textContent = `${data.responseTime || 0} ms`;
            document.getElementById('vram-usage').textContent = `${data.vram || 0} GB`;
            document.getElementById('network-traffic').textContent = `${data.network || 0} KB/s`;
            document.getElementById('gpu-temp').textContent = `${data.gpuTemp || 0}°C`;
            
            // Mettre à jour l'indicateur de statut
            const statusPill = document.getElementById('realtime-status');
            if (statusPill) {
                if (data.online) {
                    statusPill.textContent = 'En ligne';
                    statusPill.className = 'status-pill online';
                } else {
                    statusPill.textContent = 'Hors ligne';
                    statusPill.className = 'status-pill offline';
                }
            }
            
            return data;
        } catch (error) {
            console.error('Erreur lors du chargement des métriques en temps réel', error);
            throw error;
        }
    },
    
    /**
     * Met à jour les statistiques dans la sidebar
     * @param {Object} stats - Statistiques système
     */
    updateSidebarStats: (stats) => {
        // Mettre à jour les valeurs
        document.getElementById('sidebar-cpu-value').textContent = `${stats.cpu || 0}%`;
        document.getElementById('sidebar-ram-value').textContent = `${stats.ram || 0}%`;
        document.getElementById('sidebar-gpu-value').textContent = `${stats.gpu || 0}%`;
        
        // Mettre à jour les barres de progression
        document.getElementById('sidebar-cpu-bar').style.width = `${stats.cpu || 0}%`;
        document.getElementById('sidebar-ram-bar').style.width = `${stats.ram || 0}%`;
        document.getElementById('sidebar-gpu-bar').style.width = `${stats.gpu || 0}%`;
    },
    
    /**
     * Démarre le rafraîchissement automatique des données
     */
    startAutoRefresh: () => {
        // Rafraîchir toutes les 10 secondes (configurable)
        const interval = CONFIG.ui.refreshInterval || 10000;
        
        Dashboard.autoRefreshTimer = setInterval(() => {
            Dashboard.loadPerformanceData();
            
            // Toutes les 3 itérations, rafraîchir toutes les données
            Dashboard.refreshCounter = (Dashboard.refreshCounter || 0) + 1;
            if (Dashboard.refreshCounter >= 3) {
                Dashboard.loadDashboardData();
                Dashboard.refreshCounter = 0;
            }
        }, interval);
        
        console.log(`🔄 Rafraîchissement automatique démarré (${interval}ms)`);
    },
    
    /**
     * Arrête le rafraîchissement automatique des données
     */
    stopAutoRefresh: () => {
        if (Dashboard.autoRefreshTimer) {
            clearInterval(Dashboard.autoRefreshTimer);
            console.log('⏹️ Rafraîchissement automatique arrêté');
        }
    }
};

// Rendre l'objet Dashboard disponible globalement
window.Dashboard = Dashboard; 