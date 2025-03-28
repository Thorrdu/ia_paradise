/**
 * agents.js - Composant de gestion des agents
 * Gère l'affichage et les interactions avec les agents IA
 */

const Agents = {
    /**
     * Initialise le composant des agents
     */
    init: () => {
        console.log('🤖 Initialisation du composant des agents');
        
        // Initialiser les gestionnaires d'événements
        Agents.initEventListeners();
        
        // Charger les agents si on est sur la page agents
        if (document.querySelector('.agents-page')) {
            Agents.loadAgents();
        }
    },
    
    /**
     * Initialise les gestionnaires d'événements
     */
    initEventListeners: () => {
        // Bouton d'actualisation des agents
        const refreshButton = document.getElementById('refresh-agents-btn');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                refreshButton.classList.add('spin');
                
                Agents.loadAgents().then(() => {
                    setTimeout(() => {
                        refreshButton.classList.remove('spin');
                    }, 800);
                });
            });
        }
        
        // Filtre de statut
        const statusFilter = document.getElementById('agent-status-filter');
        if (statusFilter) {
            statusFilter.addEventListener('change', () => {
                const status = statusFilter.value;
                Agents.filterAgentsByStatus(status);
            });
        }
    },
    
    /**
     * Charge la liste des agents
     */
    loadAgents: async () => {
        try {
            // Afficher l'état de chargement
            const agentsContainer = document.getElementById('agents-list-container');
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
            
            // Mettre à jour l'affichage des agents
            if (agentsContainer) {
                if (agents.length === 0) {
                    agentsContainer.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-robot"></i>
                            <p>Aucun agent disponible</p>
                        </div>
                    `;
                } else {
                    agentsContainer.innerHTML = `
                        <div class="agents-grid">
                            ${agents.map(agent => Agents.renderAgentCard(agent)).join('')}
                        </div>
                    `;
                    
                    // Ajouter les interactions aux cartes
                    Agents.initAgentCardInteractions();
                }
            }
            
            // Mettre à jour le compteur d'agents dans la sidebar
            UI.updateSidebarCounts({ agents: agents.length });
            
            return agents;
        } catch (error) {
            console.error('Erreur lors du chargement des agents:', error);
            
            const agentsContainer = document.getElementById('agents-list-container');
            if (agentsContainer) {
                agentsContainer.innerHTML = `
                    <div class="error-state">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Erreur lors du chargement des agents</p>
                    </div>
                `;
            }
            
            UI.toast.show('Erreur lors du chargement des agents', 'error');
            throw error;
        }
    },
    
    /**
     * Récupère les détails d'un agent
     * @param {string} agentId - ID de l'agent
     */
    getAgentDetails: async (agentId) => {
        try {
            // Récupérer les détails de l'agent
            const agent = await API.Agents.getById(agentId);
            
            // Afficher les détails dans une modale
            Agents.showAgentDetailsModal(agent);
            
            return agent;
        } catch (error) {
            console.error(`Erreur lors de la récupération des détails de l'agent ${agentId}:`, error);
            UI.toast.show('Erreur lors de la récupération des détails', 'error');
            throw error;
        }
    },
    
    /**
     * Filtre les agents par statut
     * @param {string} status - Statut à filtrer (vide pour tous)
     */
    filterAgentsByStatus: (status) => {
        const agentCards = document.querySelectorAll('.agent-card');
        
        agentCards.forEach(card => {
            const cardStatus = card.getAttribute('data-status');
            
            if (!status || status === 'all' || cardStatus === status) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    },
    
    /**
     * Génère le HTML pour une carte d'agent
     * @param {Object} agent - Agent à afficher
     * @return {string} HTML de la carte
     */
    renderAgentCard: (agent) => {
        // Récupérer les informations de statut
        const statusInfo = CONFIG.agentStatus[agent.status] || { 
            label: agent.status, 
            color: 'var(--color-unknown)',
            icon: 'question-circle'
        };
        
        // Déterminer le type d'agent et son icône
        let agentIcon = 'robot';
        let agentType = 'Agent générique';
        
        if (agent.type) {
            switch (agent.type.toLowerCase()) {
                case 'php':
                    agentIcon = 'php';
                    agentType = 'Agent PHP';
                    break;
                case 'python':
                    agentIcon = 'python';
                    agentType = 'Agent Python';
                    break;
                case 'web':
                    agentIcon = 'globe';
                    agentType = 'Agent Web';
                    break;
                case 'data':
                    agentIcon = 'database';
                    agentType = 'Agent Data';
                    break;
                case 'system':
                    agentIcon = 'server';
                    agentType = 'Agent Système';
                    break;
            }
        }
        
        // Calculer les métriques
        let cpuUsage = agent.metrics?.cpu || 0;
        let memoryUsage = agent.metrics?.memory || 0;
        
        // Formater la date de dernière activité
        let lastActivity = 'Jamais';
        if (agent.last_activity) {
            const date = new Date(agent.last_activity);
            lastActivity = window.Utils?.format?.timeAgo?.(date) || date.toLocaleString();
        }
        
        return `
            <div class="agent-card" data-id="${agent.id}" data-status="${agent.status.toLowerCase()}">
                <div class="agent-card-header">
                    <div class="agent-icon">
                        <i class="fas fa-${agentIcon}"></i>
                    </div>
                    <div class="agent-status" style="background-color: ${statusInfo.color}">
                        <i class="fas fa-${statusInfo.icon}"></i>
                        ${statusInfo.label}
                    </div>
                </div>
                <div class="agent-card-body">
                    <h3 class="agent-name">${agent.name}</h3>
                    <div class="agent-type">${agentType}</div>
                    <div class="agent-description">${agent.description || 'Aucune description'}</div>
                    
                    <div class="agent-metrics">
                        <div class="metric">
                            <div class="metric-label">CPU</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${cpuUsage}%"></div>
                            </div>
                            <div class="metric-value">${cpuUsage}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Mémoire</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${memoryUsage}%"></div>
                            </div>
                            <div class="metric-value">${memoryUsage}%</div>
                        </div>
                    </div>
                    
                    <div class="agent-info">
                        <div class="info-item">
                            <i class="fas fa-clock"></i>
                            <span>Dernière activité: ${lastActivity}</span>
                        </div>
                        <div class="info-item">
                            <i class="fas fa-tasks"></i>
                            <span>Tâches: ${agent.task_count || 0}</span>
                        </div>
                    </div>
                </div>
                <div class="agent-card-footer">
                    <button class="btn btn-sm agent-details-btn" title="Détails">
                        <i class="fas fa-info-circle"></i>
                        Détails
                    </button>
                    <button class="btn btn-sm agent-task-btn" title="Nouvelle tâche">
                        <i class="fas fa-plus"></i>
                        Tâche
                    </button>
                    <button class="btn btn-sm agent-message-btn" title="Envoyer message">
                        <i class="fas fa-comment"></i>
                        Message
                    </button>
                </div>
            </div>
        `;
    },
    
    /**
     * Initialise les interactions avec les cartes d'agents
     */
    initAgentCardInteractions: () => {
        // Boutons de détails
        document.querySelectorAll('.agent-details-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const agentCard = e.target.closest('.agent-card');
                if (!agentCard) return;
                
                const agentId = agentCard.getAttribute('data-id');
                if (agentId) {
                    Agents.getAgentDetails(agentId);
                }
            });
        });
        
        // Boutons de nouvelle tâche
        document.querySelectorAll('.agent-task-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const agentCard = e.target.closest('.agent-card');
                if (!agentCard) return;
                
                const agentId = agentCard.getAttribute('data-id');
                if (agentId) {
                    // Ouvrir la modale de tâche
                    Agents.openNewTaskModal(agentId);
                }
            });
        });
        
        // Boutons d'envoi de message
        document.querySelectorAll('.agent-message-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const agentCard = e.target.closest('.agent-card');
                if (!agentCard) return;
                
                const agentId = agentCard.getAttribute('data-id');
                if (agentId) {
                    // Ouvrir la modale de message
                    Agents.openNewMessageModal(agentId);
                }
            });
        });
    },
    
    /**
     * Affiche les détails d'un agent dans une modale
     * @param {Object} agent - Agent à afficher
     */
    showAgentDetailsModal: (agent) => {
        // Créer une modale si elle n'existe pas
        let modalOverlay = document.getElementById('agent-details-modal-overlay');
        
        if (!modalOverlay) {
            modalOverlay = document.createElement('div');
            modalOverlay.className = 'modal-overlay';
            modalOverlay.id = 'agent-details-modal-overlay';
            
            document.body.appendChild(modalOverlay);
        }
        
        // Récupérer les informations de statut
        const statusInfo = CONFIG.agentStatus[agent.status] || { 
            label: agent.status, 
            color: 'var(--color-unknown)',
            icon: 'question-circle'
        };
        
        // Définir le contenu de la modale
        modalOverlay.innerHTML = `
            <div class="modal" id="agent-details-modal">
                <div class="modal-header">
                    <h3>Détails de l'agent</h3>
                    <button class="modal-close" data-dismiss="modal"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-body">
                    <div class="agent-details">
                        <div class="agent-header">
                            <div class="agent-avatar">
                                <i class="fas fa-robot"></i>
                            </div>
                            <div class="agent-info">
                                <h3 class="agent-name">${agent.name}</h3>
                                <div class="agent-status" style="background-color: ${statusInfo.color}">
                                    <i class="fas fa-${statusInfo.icon}"></i>
                                    ${statusInfo.label}
                                </div>
                            </div>
                        </div>
                        
                        <div class="agent-section">
                            <h4>Informations générales</h4>
                            <div class="info-grid">
                                <div class="info-item">
                                    <div class="info-label">Type</div>
                                    <div class="info-value">${agent.type || 'Générique'}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Modèle</div>
                                    <div class="info-value">${agent.model || 'Non spécifié'}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Version</div>
                                    <div class="info-value">${agent.version || '1.0'}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Dernière activité</div>
                                    <div class="info-value">${agent.last_activity ? new Date(agent.last_activity).toLocaleString() : 'Jamais'}</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="agent-section">
                            <h4>Description</h4>
                            <p class="agent-description">${agent.description || 'Aucune description disponible pour cet agent.'}</p>
                        </div>
                        
                        <div class="agent-section">
                            <h4>Capacités</h4>
                            ${agent.capabilities ? `
                                <ul class="capabilities-list">
                                    ${agent.capabilities.map(cap => `
                                        <li class="capability-item">
                                            <i class="fas fa-check"></i>
                                            <span>${cap}</span>
                                        </li>
                                    `).join('')}
                                </ul>
                            ` : '<p>Aucune capacité spécifiée.</p>'}
                        </div>
                        
                        <div class="agent-section">
                            <h4>Statistiques</h4>
                            <div class="stats-grid">
                                <div class="stat-item">
                                    <div class="stat-icon"><i class="fas fa-tasks"></i></div>
                                    <div class="stat-value">${agent.task_count || 0}</div>
                                    <div class="stat-label">Tâches</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
                                    <div class="stat-value">${agent.completed_tasks || 0}</div>
                                    <div class="stat-label">Complétées</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-icon"><i class="fas fa-comment"></i></div>
                                    <div class="stat-value">${agent.message_count || 0}</div>
                                    <div class="stat-label">Messages</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-icon"><i class="fas fa-clock"></i></div>
                                    <div class="stat-value">${agent.uptime || '0h'}</div>
                                    <div class="stat-label">Temps actif</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" data-dismiss="modal">Fermer</button>
                    <button class="btn btn-primary" id="new-task-for-agent">Nouvelle tâche</button>
                </div>
            </div>
        `;
        
        // Afficher la modale
        modalOverlay.classList.add('open');
        document.body.classList.add('modal-open');
        
        // Initialiser les gestionnaires d'événements
        Agents.initAgentDetailsModalEvents(agent);
    },
    
    /**
     * Initialise les événements de la modale de détails
     * @param {Object} agent - Agent concerné
     */
    initAgentDetailsModalEvents: (agent) => {
        // Fermeture de la modale
        document.querySelectorAll('.modal-overlay .modal-close, .modal-overlay [data-dismiss="modal"]').forEach(button => {
            button.addEventListener('click', () => {
                const modalOverlay = document.getElementById('agent-details-modal-overlay');
                if (modalOverlay) {
                    modalOverlay.classList.remove('open');
                    document.body.classList.remove('modal-open');
                }
            });
        });
        
        // Bouton de nouvelle tâche
        const newTaskBtn = document.getElementById('new-task-for-agent');
        if (newTaskBtn) {
            newTaskBtn.addEventListener('click', () => {
                // Fermer cette modale
                const modalOverlay = document.getElementById('agent-details-modal-overlay');
                if (modalOverlay) {
                    modalOverlay.classList.remove('open');
                }
                
                // Ouvrir la modale de tâche
                Agents.openNewTaskModal(agent.id);
            });
        }
        
        // Fermer en cliquant en dehors
        const modalOverlay = document.getElementById('agent-details-modal-overlay');
        if (modalOverlay) {
            modalOverlay.addEventListener('click', (e) => {
                if (e.target === modalOverlay) {
                    modalOverlay.classList.remove('open');
                    document.body.classList.remove('modal-open');
                }
            });
        }
    },
    
    /**
     * Ouvre la modale de création de tâche avec un agent présélectionné
     * @param {string} agentId - ID de l'agent
     */
    openNewTaskModal: (agentId) => {
        // Sélectionner l'agent dans le formulaire
        const agentSelect = document.getElementById('task-agent');
        if (agentSelect) {
            agentSelect.value = agentId;
        }
        
        // Ouvrir la modale de tâche
        UI.modal.open('task-modal');
    },
    
    /**
     * Ouvre la modale d'envoi de message avec un agent présélectionné
     * @param {string} agentId - ID de l'agent
     */
    openNewMessageModal: (agentId) => {
        // Rediriger vers la page des messages si elle existe
        const messagesLink = document.querySelector('a[data-page="messages"]');
        if (messagesLink) {
            messagesLink.click();
            
            // Sélectionner l'agent après le chargement de la page
            setTimeout(() => {
                const agentSelect = document.getElementById('message-agent');
                if (agentSelect) {
                    agentSelect.value = agentId;
                }
            }, 500);
            
            return;
        }
        
        // Sinon, afficher une notification
        UI.toast.show('Fonctionnalité de messagerie non disponible', 'info');
    }
};

// Ajouter le composant Agents à l'objet global Components
window.Components = window.Components || {};
window.Components.Agents = Agents; 