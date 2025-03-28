// Paradis IA - Script simplifié

document.addEventListener('DOMContentLoaded', () => {
    console.log('Chargement de l\'interface Paradis IA...');
    
    // Éléments DOM
    const cpuUsage = document.getElementById('cpu-usage');
    const cpuText = document.getElementById('cpu-text');
    const ramUsage = document.getElementById('ram-usage');
    const ramText = document.getElementById('ram-text');
    const gpuUsage = document.getElementById('gpu-usage');
    const gpuText = document.getElementById('gpu-text');
    
    const agentsList = document.getElementById('agents-list');
    const tasksList = document.getElementById('tasks-list');
    const messagesContainer = document.getElementById('messages-container');
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    const modeIndicator = document.getElementById('mode-indicator');
    
    // Initialisation
    loadAll();
    setInterval(loadAll, 5000); // Actualiser toutes les 5 secondes
    
    // Gestionnaires d'événements
    const sendBtn = document.getElementById('send-message-btn');
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }
    
    const messageText = document.getElementById('message-text');
    if (messageText) {
        messageText.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    const newTaskBtn = document.getElementById('new-task-btn');
    if (newTaskBtn) {
        newTaskBtn.addEventListener('click', () => {
            const modal = document.getElementById('new-task-modal');
            if (modal) modal.style.display = 'flex';
        });
    }
    
    const closeBtn = document.querySelector('.close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            const modal = document.getElementById('new-task-modal');
            if (modal) modal.style.display = 'none';
        });
    }
    
    const taskForm = document.getElementById('new-task-form');
    if (taskForm) {
        taskForm.addEventListener('submit', createTask);
    }
    
    // Fonctions
    function loadAll() {
        fetchAgents();
        fetchTasks();
        fetchMessages();
        fetchSystemStats();
        checkSystemMode();
    }
    
    function fetchAgents() {
        fetch('/api/agents')
            .then(response => response.json())
            .then(data => {
                updateAgentsList(data);
                updateAgentSelectors(data);
            })
            .catch(error => {
                console.error('Erreur lors du chargement des agents:', error);
                updateStatus('Erreur de communication', 'error');
            });
    }
    
    function fetchTasks() {
        fetch('/api/tasks')
            .then(response => response.json())
            .then(data => {
                updateTasksList(data);
            })
            .catch(error => {
                console.error('Erreur lors du chargement des tâches:', error);
            });
    }
    
    function fetchMessages() {
        fetch('/api/messages')
            .then(response => response.json())
            .then(data => {
                updateMessagesContainer(data);
            })
            .catch(error => {
                console.error('Erreur lors du chargement des messages:', error);
            });
    }
    
    function fetchSystemStats() {
        fetch('/api/system/stats')
            .then(response => response.json())
            .then(data => {
                updateSystemMonitors(data);
            })
            .catch(error => {
                console.error('Erreur lors du chargement des stats système:', error);
            });
    }
    
    function checkSystemMode() {
        fetch('/api/system/mode')
            .then(response => response.json())
            .then(data => {
                if (modeIndicator) {
                    modeIndicator.textContent = `Mode: ${data.mode || 'LIMITÉ'}`;
                }
                updateStatus(data.mode === 'FULL' ? 'Système complet' : 'Fonctionnalités limitées', 
                             data.mode === 'FULL' ? 'success' : 'warning');
            })
            .catch(error => {
                console.error('Erreur lors de la vérification du mode:', error);
                if (modeIndicator) {
                    modeIndicator.textContent = 'Mode: LIMITÉ';
                }
            });
    }
    
    function updateAgentsList(agents) {
        if (!agentsList) return;
        
        if (!agents || agents.length === 0) {
            agentsList.innerHTML = '<div class="loading">Aucun agent disponible</div>';
            return;
        }
        
        agentsList.innerHTML = '';
        
        agents.forEach(agent => {
            const agentElement = document.createElement('div');
            agentElement.className = 'agent-item';
            
            agentElement.innerHTML = `
                <div class="agent-info">
                    <strong>${agent.name}</strong>
                    <div class="agent-capabilities">${agent.capabilities.join(', ')}</div>
                </div>
                <div class="agent-status ready">READY</div>
            `;
            
            agentsList.appendChild(agentElement);
        });
    }
    
    function updateTasksList(tasks) {
        if (!tasksList) return;
        
        if (!tasks || tasks.length === 0) {
            tasksList.innerHTML = '<div class="loading">Aucune tâche disponible</div>';
            return;
        }
        
        tasksList.innerHTML = '';
        
        tasks.forEach(task => {
            const taskElement = document.createElement('div');
            taskElement.className = 'task-item';
            
            const status = task.status.toLowerCase();
            const priority = task.priority.toLowerCase();
            
            taskElement.innerHTML = `
                <div class="task-header">
                    <div class="task-title">${task.description.substring(0, 50)}${task.description.length > 50 ? '...' : ''}</div>
                    <div class="task-status ${status}">${getStatusLabel(task.status)}</div>
                </div>
                <div class="task-description">${task.description}</div>
                <div class="task-meta">
                    <div>Agent: ${task.assigned_to}</div>
                    <div>Priorité: ${getPriorityLabel(task.priority)}</div>
                    <div>Créée: ${formatDate(task.created_at)}</div>
                </div>
            `;
            
            tasksList.appendChild(taskElement);
        });
    }
    
    function updateMessagesContainer(messages) {
        if (!messagesContainer) return;
        
        if (!messages || messages.length === 0) {
            messagesContainer.innerHTML = `
                <div class="welcome-message">
                    <p>Bienvenue dans l'interface de Paradis IA. Vous pouvez communiquer avec les agents en envoyant des messages ci-dessous.</p>
                </div>
            `;
            return;
        }
        
        messagesContainer.innerHTML = '';
        
        messages.forEach(message => {
            const messageElement = document.createElement('div');
            const isReceived = message.recipient === 'WebInterface';
            
            messageElement.className = `message ${isReceived ? 'received' : 'sent'}`;
            
            messageElement.innerHTML = `
                <div class="message-header">
                    <span>${isReceived ? 'De: ' + message.sender : 'À: ' + message.recipient}</span>
                    <span>${formatDate(message.timestamp)}</span>
                </div>
                <div class="message-content">${message.content}</div>
            `;
            
            messagesContainer.appendChild(messageElement);
        });
        
        // Faire défiler vers le bas
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    function updateAgentSelectors(agents) {
        // Sélecteur pour l'envoi de message
        const agentSelect = document.getElementById('agent-select');
        if (agentSelect) {
            const currentValue = agentSelect.value;
            
            agentSelect.innerHTML = '<option value="">Sélectionner un agent</option>';
            
            if (agents && agents.length > 0) {
                agents.forEach(agent => {
                    const option = document.createElement('option');
                    option.value = agent.name;
                    option.textContent = agent.name;
                    agentSelect.appendChild(option);
                });
                
                // Restaurer la valeur si possible
                if (currentValue && agents.some(a => a.name === currentValue)) {
                    agentSelect.value = currentValue;
                }
            }
        }
        
        // Sélecteur pour la création de tâche
        const taskAgentSelect = document.getElementById('task-agent');
        if (taskAgentSelect) {
            const currentValue = taskAgentSelect.value;
            
            taskAgentSelect.innerHTML = '';
            
            if (agents && agents.length > 0) {
                agents.forEach(agent => {
                    const option = document.createElement('option');
                    option.value = agent.name;
                    option.textContent = agent.name;
                    taskAgentSelect.appendChild(option);
                });
                
                // Restaurer la valeur si possible
                if (currentValue && agents.some(a => a.name === currentValue)) {
                    taskAgentSelect.value = currentValue;
                } else if (agents.length > 0) {
                    taskAgentSelect.value = agents[0].name;
                }
            }
        }
    }
    
    function updateSystemMonitors(data) {
        // CPU
        if (cpuUsage && cpuText && data.cpu) {
            const percent = data.cpu.percent;
            cpuUsage.style.width = `${percent}%`;
            cpuText.textContent = `${percent}%`;
        }
        
        // RAM
        if (ramUsage && ramText && data.memory) {
            const percent = data.memory.percent;
            ramUsage.style.width = `${percent}%`;
            ramText.textContent = `${percent}%`;
        }
        
        // GPU
        if (gpuUsage && gpuText && data.gpu) {
            if (data.gpu.available) {
                const percent = data.gpu.percent || data.gpu.memory.percent || 0;
                gpuUsage.style.width = `${percent}%`;
                gpuText.textContent = `${percent}%`;
            } else {
                gpuUsage.style.width = '0%';
                gpuText.textContent = 'N/A';
            }
        }
    }
    
    function updateStatus(message, type = 'info') {
        if (statusText) {
            statusText.textContent = message;
        }
        
        if (statusIndicator) {
            // Changer la couleur en fonction du type
            switch (type) {
                case 'success':
                    statusIndicator.style.backgroundColor = 'var(--success-color)';
                    break;
                case 'warning':
                    statusIndicator.style.backgroundColor = 'var(--warning-color)';
                    break;
                case 'error':
                    statusIndicator.style.backgroundColor = 'var(--danger-color)';
                    break;
                default:
                    statusIndicator.style.backgroundColor = 'var(--primary-color)';
            }
        }
    }
    
    function sendMessage() {
        const agentSelect = document.getElementById('agent-select');
        const messageText = document.getElementById('message-text');
        
        if (!agentSelect || !messageText) return;
        
        const recipient = agentSelect.value;
        const content = messageText.value.trim();
        
        if (!recipient) {
            alert('Veuillez sélectionner un agent destinataire.');
            return;
        }
        
        if (!content) {
            alert('Veuillez entrer un message.');
            return;
        }
        
        // Désactiver le bouton pendant l'envoi
        const sendBtn = document.getElementById('send-message-btn');
        if (sendBtn) sendBtn.disabled = true;
        
        fetch('/api/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                recipient: recipient,
                content: content
            })
        })
            .then(response => response.json())
            .then(data => {
                // Vider le champ de texte
                messageText.value = '';
                
                // Actualiser les messages
                fetchMessages();
                
                // Mettre à jour le statut
                updateStatus('Message envoyé', 'success');
            })
            .catch(error => {
                console.error('Erreur:', error);
                updateStatus('Erreur lors de l\'envoi', 'error');
            })
            .finally(() => {
                // Réactiver le bouton
                if (sendBtn) sendBtn.disabled = false;
            });
    }
    
    function createTask(e) {
        e.preventDefault();
        
        const description = document.getElementById('task-description').value.trim();
        const assignedTo = document.getElementById('task-agent').value;
        const priority = document.getElementById('task-priority').value;
        
        if (!description) {
            alert('Veuillez entrer une description pour la tâche.');
            return;
        }
        
        if (!assignedTo) {
            alert('Veuillez sélectionner un agent pour la tâche.');
            return;
        }
        
        // Désactiver le bouton pendant l'envoi
        const submitButton = document.querySelector('#new-task-form button[type="submit"]');
        if (submitButton) submitButton.disabled = true;
        
        fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                description: description,
                assigned_to: assignedTo,
                priority: priority
            })
        })
            .then(response => response.json())
            .then(data => {
                // Fermer le modal
                const modal = document.getElementById('new-task-modal');
                if (modal) modal.style.display = 'none';
                
                // Vider le formulaire
                document.getElementById('task-description').value = '';
                
                // Actualiser les tâches
                fetchTasks();
                
                // Mettre à jour le statut
                updateStatus('Tâche créée', 'success');
            })
            .catch(error => {
                console.error('Erreur:', error);
                updateStatus('Erreur lors de la création', 'error');
            })
            .finally(() => {
                // Réactiver le bouton
                if (submitButton) submitButton.disabled = false;
            });
    }
    
    // Fonctions utilitaires
    function formatDate(dateString) {
        if (!dateString) return '';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } catch (e) {
            return dateString;
        }
    }
    
    function getStatusLabel(status) {
        switch (status) {
            case 'PENDING':
                return 'En attente';
            case 'IN_PROGRESS':
                return 'En cours';
            case 'COMPLETED':
                return 'Terminée';
            case 'FAILED':
                return 'Échouée';
            default:
                return status;
        }
    }
    
    function getPriorityLabel(priority) {
        switch (priority) {
            case 'LOW':
                return 'Basse';
            case 'MEDIUM':
                return 'Moyenne';
            case 'HIGH':
                return 'Haute';
            case 'URGENT':
                return 'Urgente';
            default:
                return priority;
        }
    }
});
