/**
 * components/tasks.js - Composant de gestion des tâches
 * Gère l'affichage, la création et la mise à jour des tâches
 */

const TasksComponent = {
    // Stockage des données
    data: {
        tasks: [],
        selectedTask: null,
        filter: 'all'
    },
    
    /**
     * Initialise le composant tâches
     */
    init: () => {
        // S'arrêter si nous ne sommes pas sur la page des tâches
        if (!document.querySelector('.tasks-page') && !document.querySelector('#current-tasks')) return;
        
        console.log('🔄 Initialisation du composant tâches');
        
        // Initialiser les gestionnaires d'événements
        TasksComponent.initEventHandlers();
        
        // Charger les tâches
        TasksComponent.loadTasks();
    },
    
    /**
     * Initialise les gestionnaires d'événements
     */
    initEventHandlers: () => {
        // Formulaire de création de tâche
        const taskForm = document.getElementById('create-task-form');
        if (taskForm) {
            taskForm.addEventListener('submit', TasksComponent.handleCreateTask);
        }
        
        // Filtres
        const filterButtons = document.querySelectorAll('.task-filter-btn');
        filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const filter = btn.getAttribute('data-filter');
                TasksComponent.setFilter(filter);
            });
        });
        
        // Tri
        const sortSelect = document.getElementById('task-sort');
        if (sortSelect) {
            sortSelect.addEventListener('change', () => {
                TasksComponent.sortTasks(sortSelect.value);
            });
        }
        
        // Sélection d'agent
        const agentSelect = document.getElementById('task-agent');
        if (agentSelect) {
            // Charger les agents disponibles
            API.Agents.getAll().then(agents => {
                // Vider et remplir le select
                agentSelect.innerHTML = '<option value="" selected>Sélectionner un agent...</option>';
                
                agents.forEach(agent => {
                    if (agent.status === 'ACTIVE' || agent.status === 'IDLE') {
                        const option = document.createElement('option');
                        option.value = agent.id;
                        option.textContent = agent.name;
                        agentSelect.appendChild(option);
                    }
                });
            }).catch(error => {
                console.error('Erreur lors du chargement des agents', error);
            });
        }
        
        // Recherche
        const searchInput = document.getElementById('task-search');
        if (searchInput) {
            searchInput.addEventListener('input', event => {
                const searchTerm = event.target.value.toLowerCase();
                TasksComponent.searchTasks(searchTerm);
            });
        }
    },
    
    /**
     * Charge les tâches depuis l'API
     */
    loadTasks: async () => {
        const container = document.querySelector('.tasks-list') || document.getElementById('current-tasks');
        if (!container) return;
        
        try {
            Utils.dom.createLoader(container, 'Chargement des tâches...');
            
            const tasks = await API.Tasks.getAll();
            TasksComponent.data.tasks = tasks;
            
            if (tasks.length === 0) {
                Utils.dom.showEmpty(container, 'Aucune tâche disponible');
                return;
            }
            
            // Filtrer et afficher les tâches
            TasksComponent.renderTasks();
            
            // Mettre à jour le compteur
            const totalCount = document.getElementById('total-tasks-count');
            if (totalCount) {
                totalCount.textContent = tasks.length;
            }
            
            // Mettre à jour les statistiques
            TasksComponent.updateStats();
            
            // Mettre à jour le graphique si disponible
            if (window.Charts && Charts.updateTaskDistributionChart) {
                const counts = {
                    PENDING: tasks.filter(t => t.status === 'PENDING').length,
                    RUNNING: tasks.filter(t => t.status === 'RUNNING').length,
                    COMPLETED: tasks.filter(t => t.status === 'COMPLETED').length,
                    FAILED: tasks.filter(t => t.status === 'FAILED').length,
                    CANCELLED: tasks.filter(t => t.status === 'CANCELLED').length
                };
                
                Charts.updateTaskDistributionChart(counts);
            }
            
            return tasks;
        } catch (error) {
            Utils.dom.showError(container, 'Erreur lors du chargement des tâches');
            console.error('Erreur lors du chargement des tâches', error);
        }
    },
    
    /**
     * Affiche la liste des tâches avec filtrage
     */
    renderTasks: () => {
        const container = document.querySelector('.tasks-list') || document.getElementById('current-tasks');
        if (!container) return;
        
        // Filtrer les tâches selon le filtre actif
        let filteredTasks = [...TasksComponent.data.tasks];
        
        if (TasksComponent.data.filter !== 'all') {
            filteredTasks = filteredTasks.filter(task => task.status === TasksComponent.data.filter);
        }
        
        // Gérer le cas où aucune tâche ne correspond au filtre
        if (filteredTasks.length === 0) {
            Utils.dom.showEmpty(container, 'Aucune tâche ne correspond à ce filtre');
            return;
        }
        
        // Limiter le nombre de tâches dans le widget dashboard
        if (container.id === 'current-tasks') {
            // Pour le widget du dashboard, afficher uniquement les tâches actives triées par priorité
            filteredTasks = filteredTasks
                .filter(t => t.status === 'PENDING' || t.status === 'RUNNING')
                .sort((a, b) => {
                    const priorityA = CONFIG.taskPriority[a.priority]?.value || 0;
                    const priorityB = CONFIG.taskPriority[b.priority]?.value || 0;
                    return priorityB - priorityA;
                })
                .slice(0, 5);
        }
        
        // Créer la liste des tâches HTML
        let html = '<div class="task-items">';
        
        filteredTasks.forEach(task => {
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
            const created = new Date(task.created_at || Date.now()).toLocaleString();
            
            html += `
                <div class="task-item" data-id="${task.id || ''}" data-status="${status}">
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
                        <div class="task-created">
                            <i class="fas fa-calendar-alt"></i>
                            <span>${created}</span>
                        </div>
                        <div class="task-actions">
                            <button class="btn btn-sm btn-status" data-task-id="${task.id || ''}" title="Changer le statut">
                                <i class="fas fa-sync-alt"></i>
                            </button>
                            <button class="btn btn-sm btn-details" data-task-id="${task.id || ''}" title="Détails">
                                <i class="fas fa-info-circle"></i>
                            </button>
                            ${status !== 'COMPLETED' && status !== 'FAILED' && status !== 'CANCELLED' ? 
                                `<button class="btn btn-sm btn-cancel" data-task-id="${task.id || ''}" title="Annuler">
                                    <i class="fas fa-times"></i>
                                </button>` : ''}
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
        
        // Ajouter les gestionnaires d'événements pour les actions
        TasksComponent.initTaskActions();
    },
    
    /**
     * Initialise les gestionnaires pour les boutons d'action des tâches
     */
    initTaskActions: () => {
        // Boutons de changement de statut
        document.querySelectorAll('.btn-status').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const taskId = btn.getAttribute('data-task-id');
                if (!taskId) return;
                
                TasksComponent.showStatusChangeModal(taskId);
            });
        });
        
        // Boutons de détails
        document.querySelectorAll('.btn-details').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const taskId = btn.getAttribute('data-task-id');
                if (!taskId) return;
                
                TasksComponent.showTaskDetails(taskId);
            });
        });
        
        // Boutons d'annulation
        document.querySelectorAll('.btn-cancel').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const taskId = btn.getAttribute('data-task-id');
                if (!taskId) return;
                
                if (confirm('Êtes-vous sûr de vouloir annuler cette tâche ?')) {
                    try {
                        await API.Tasks.updateStatus(taskId, 'CANCELLED');
                        Utils.toast.show('Tâche annulée avec succès', 'success');
                        
                        // Rafraîchir les tâches
                        TasksComponent.loadTasks();
                    } catch (error) {
                        Utils.toast.show('Erreur lors de l\'annulation de la tâche', 'error');
                        console.error('Erreur lors de l\'annulation', error);
                    }
                }
            });
        });
        
        // Clic sur la tâche pour les détails
        document.querySelectorAll('.task-item').forEach(item => {
            item.addEventListener('click', () => {
                const taskId = item.getAttribute('data-id');
                if (!taskId) return;
                
                TasksComponent.showTaskDetails(taskId);
            });
        });
    },
    
    /**
     * Affiche la modale de changement de statut
     * @param {string} taskId - Identifiant de la tâche
     */
    showStatusChangeModal: (taskId) => {
        // Dans une version simple, utiliser prompt
        const newStatus = window.prompt('Nouveau statut (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED):', 'COMPLETED');
        if (!newStatus) return;
        
        // Valider le statut
        const validStatuses = ['PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED'];
        if (!validStatuses.includes(newStatus.toUpperCase())) {
            Utils.toast.show('Statut invalide. Utilisez un des statuts suivants: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED', 'error');
            return;
        }
        
        // Mettre à jour le statut
        API.Tasks.updateStatus(taskId, newStatus.toUpperCase())
            .then(() => {
                Utils.toast.show('Statut de la tâche mis à jour', 'success');
                
                // Rafraîchir les tâches
                TasksComponent.loadTasks();
            })
            .catch(error => {
                Utils.toast.show('Erreur lors de la mise à jour du statut', 'error');
                console.error('Erreur lors de la mise à jour du statut', error);
            });
    },
    
    /**
     * Affiche les détails d'une tâche
     * @param {string} taskId - Identifiant de la tâche
     */
    showTaskDetails: (taskId) => {
        // Trouver la tâche
        const task = TasksComponent.data.tasks.find(t => t.id === taskId);
        if (!task) return;
        
        TasksComponent.data.selectedTask = task;
        
        // Dans une version complète, afficher une modale avec les détails
        // Pour cette version simplifiée, afficher une alerte avec JSON
        alert(`Détails de la tâche ${taskId}:\n${JSON.stringify(task, null, 2)}`);
    },
    
    /**
     * Gère la création d'une nouvelle tâche
     * @param {Event} event - Événement de soumission du formulaire
     */
    handleCreateTask: async (event) => {
        event.preventDefault();
        
        const form = event.target;
        const description = form.querySelector('#task-description').value;
        const agentId = form.querySelector('#task-agent').value;
        const priority = form.querySelector('#task-priority').value;
        
        if (!description) {
            Utils.toast.show('Veuillez saisir une description pour la tâche', 'warning');
            return;
        }
        
        try {
            // Créer la tâche
            const newTask = {
                description: description,
                priority: priority || 'MEDIUM',
                status: 'PENDING'
            };
            
            if (agentId) {
                newTask.agent_id = agentId;
            }
            
            const createdTask = await API.Tasks.create(newTask);
            
            // Réinitialiser le formulaire
            form.reset();
            
            // Notification et rafraîchissement
            Utils.toast.show('Tâche créée avec succès', 'success');
            
            // Fermer la modale si présente
            Utils.modal.close('task-modal');
            
            // Rafraîchir les tâches
            TasksComponent.loadTasks();
            
            return createdTask;
        } catch (error) {
            Utils.toast.show('Erreur lors de la création de la tâche', 'error');
            console.error('Erreur lors de la création de la tâche', error);
        }
    },
    
    /**
     * Définit le filtre actif et rafraîchit l'affichage
     * @param {string} filter - Filtre à appliquer (all, PENDING, RUNNING, etc.)
     */
    setFilter: (filter) => {
        TasksComponent.data.filter = filter;
        
        // Mettre à jour l'UI des boutons
        document.querySelectorAll('.task-filter-btn').forEach(btn => {
            if (btn.getAttribute('data-filter') === filter) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Rafraîchir l'affichage
        TasksComponent.renderTasks();
        
        // Mettre à jour le compteur filtré
        const filteredCount = document.getElementById('filtered-tasks-count');
        if (filteredCount) {
            let count = TasksComponent.data.tasks.length;
            
            if (filter !== 'all') {
                count = TasksComponent.data.tasks.filter(task => task.status === filter).length;
            }
            
            filteredCount.textContent = count;
        }
    },
    
    /**
     * Trie les tâches selon un critère
     * @param {string} sortBy - Critère de tri (created_desc, created_asc, priority_desc, priority_asc)
     */
    sortTasks: (sortBy) => {
        const [field, direction] = sortBy.split('_');
        
        TasksComponent.data.tasks.sort((a, b) => {
            if (field === 'created') {
                const dateA = new Date(a.created_at || 0);
                const dateB = new Date(b.created_at || 0);
                return direction === 'asc' ? dateA - dateB : dateB - dateA;
            } else if (field === 'priority') {
                const priorityA = CONFIG.taskPriority[a.priority]?.value || 0;
                const priorityB = CONFIG.taskPriority[b.priority]?.value || 0;
                return direction === 'asc' ? priorityA - priorityB : priorityB - priorityA;
            }
            return 0;
        });
        
        // Rafraîchir l'affichage
        TasksComponent.renderTasks();
    },
    
    /**
     * Recherche des tâches par terme
     * @param {string} term - Terme de recherche
     */
    searchTasks: (term) => {
        if (!term) {
            // Si aucun terme, réinitialiser l'affichage
            TasksComponent.loadTasks();
            return;
        }
        
        const container = document.querySelector('.tasks-list');
        if (!container) return;
        
        // Filtrer les tâches selon le terme de recherche
        const filteredTasks = TasksComponent.data.tasks.filter(task => {
            const searchableFields = [
                task.description,
                task.agent_name,
                task.id,
                task.status,
                task.priority
            ];
            
            return searchableFields.some(field => 
                field && field.toString().toLowerCase().includes(term)
            );
        });
        
        if (filteredTasks.length === 0) {
            Utils.dom.showEmpty(container, `Aucune tâche ne correspond à "${term}"`);
            return;
        }
        
        // Temporairement remplacer les tâches pour l'affichage
        const originalTasks = TasksComponent.data.tasks;
        TasksComponent.data.tasks = filteredTasks;
        
        // Générer l'affichage
        TasksComponent.renderTasks();
        
        // Restaurer les tâches originales
        TasksComponent.data.tasks = originalTasks;
    },
    
    /**
     * Met à jour les statistiques des tâches
     */
    updateStats: () => {
        const tasks = TasksComponent.data.tasks;
        
        // Compteurs par statut
        const counts = {
            pending: tasks.filter(t => t.status === 'PENDING').length,
            running: tasks.filter(t => t.status === 'RUNNING').length,
            completed: tasks.filter(t => t.status === 'COMPLETED').length,
            failed: tasks.filter(t => t.status === 'FAILED').length,
            cancelled: tasks.filter(t => t.status === 'CANCELLED').length
        };
        
        // Complétion
        const completionRate = tasks.length > 0 ? 
            Math.round((counts.completed / tasks.length) * 100) : 0;
        
        // Priorité
        const priorityCounts = {
            low: tasks.filter(t => t.priority === 'LOW').length,
            medium: tasks.filter(t => t.priority === 'MEDIUM').length,
            high: tasks.filter(t => t.priority === 'HIGH').length,
            urgent: tasks.filter(t => t.priority === 'URGENT').length
        };
        
        // Mettre à jour les compteurs dans l'UI
        document.querySelectorAll('[data-counter="pending"]').forEach(el => el.textContent = counts.pending);
        document.querySelectorAll('[data-counter="running"]').forEach(el => el.textContent = counts.running);
        document.querySelectorAll('[data-counter="completed"]').forEach(el => el.textContent = counts.completed);
        document.querySelectorAll('[data-counter="failed"]').forEach(el => el.textContent = counts.failed);
        document.querySelectorAll('[data-counter="cancelled"]').forEach(el => el.textContent = counts.cancelled);
        
        // Taux de complétion
        const completionEl = document.getElementById('task-completion-rate');
        if (completionEl) {
            completionEl.textContent = `${completionRate}%`;
            
            // Mettre à jour la barre de progression
            const progressBar = document.getElementById('task-completion-bar');
            if (progressBar) {
                progressBar.style.width = `${completionRate}%`;
                
                // Changer la couleur selon le taux
                if (completionRate < 30) {
                    progressBar.className = 'progress-bar progress-low';
                } else if (completionRate < 70) {
                    progressBar.className = 'progress-bar progress-medium';
                } else {
                    progressBar.className = 'progress-bar progress-high';
                }
            }
        }
        
        // Mettre à jour les compteurs dans la sidebar
        UI.updateSidebarCounts({ tasks: tasks.length });
    }
};

// Rendre le composant disponible globalement
window.TasksComponent = TasksComponent; 