// Paradis IA - Interface Frontend

// Variables globales
let agents = [];
let tasks = [];
let messages = [];
let currentTask = null;
let chartData = {
    cpu: [],
    memory: [],
    gpu: []
};
let charts = {};
let isLimitedMode = false;

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

// Fonction principale d'initialisation
function initializeApp() {
    // Vérifier si l'API est disponible
    checkApiStatus();
    
    // Charger les données initiales
    fetchAgents();
    fetchTasks();
    fetchMessages();
    
    // Initialiser les graphiques de ressources
    initializeCharts();
    
    // Démarrer les mises à jour périodiques
    startPeriodicUpdates();
    
    // Attacher les gestionnaires d'événements
    attachEventListeners();
}

// Vérification de l'état de l'API
function checkApiStatus() {
    fetch('/api/monitoring')
        .then(response => response.json())
        .then(data => {
            if (data.error && data.limited_mode) {
                isLimitedMode = true;
                showNotification("Le système fonctionne en mode limité", "warning");
                document.getElementById('mode-status').textContent = "⚠️ Mode Limité";
                document.getElementById('mode-status').style.backgroundColor = "var(--warning-color)";
            } else {
                isLimitedMode = false;
                document.getElementById('mode-status').textContent = "✅ Mode Complet";
                document.getElementById('mode-status').style.backgroundColor = "var(--success-color)";
            }
        })
        .catch(error => {
            console.error('Erreur lors de la vérification du statut API:', error);
            isLimitedMode = true;
            document.getElementById('mode-status').textContent = "❌ API Indisponible";
            document.getElementById('mode-status').style.backgroundColor = "var(--danger-color)";
        });
}

// Récupération des agents
function fetchAgents() {
    fetch('/api/agents')
        .then(response => response.json())
        .then(data => {
            agents = data;
            updateAgentsList();
            updateTaskAgentSelector();
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des agents:', error);
            showNotification("Impossible de charger les agents", "error");
        });
}

// Récupération des tâches
function fetchTasks() {
    fetch('/api/tasks')
        .then(response => response.json())
        .then(data => {
            tasks = data;
            updateTasksList();
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des tâches:', error);
            showNotification("Impossible de charger les tâches", "error");
        });
}

// Récupération des messages
function fetchMessages() {
    fetch('/api/messages')
        .then(response => response.json())
        .then(data => {
            messages = data;
            updateMessagesList();
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des messages:', error);
            showNotification("Impossible de charger les messages", "error");
        });
}

// Récupération des statistiques de surveillance
function fetchMonitoringStats() {
    fetch('/api/monitoring')
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                updateResourceStats(data);
                updateCharts(data);
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des statistiques:', error);
        });
}

// Mise à jour de la liste des agents
function updateAgentsList() {
    const agentsList = document.getElementById('agents-list');
    agentsList.innerHTML = '';
    
    if (agents.length === 0) {
        agentsList.innerHTML = '<div class="list-item">Aucun agent disponible</div>';
        return;
    }
    
    agents.forEach(agent => {
        const agentItem = document.createElement('div');
        agentItem.className = 'list-item agent-item';
        agentItem.innerHTML = `
            <div>${agent.name}</div>
            <span class="status-badge status-${agent.status}">${agent.status}</span>
        `;
        agentsList.appendChild(agentItem);
    });
}

// Mise à jour de la liste des tâches
function updateTasksList() {
    const tasksList = document.getElementById('tasks-list');
    tasksList.innerHTML = '';
    
    if (tasks.length === 0) {
        tasksList.innerHTML = '<div class="list-item">Aucune tâche disponible</div>';
        return;
    }
    
    tasks.forEach(task => {
        const taskItem = document.createElement('div');
        taskItem.className = `list-item task-item ${task.priority} ${task.status === 'completed' ? 'completed' : ''}`;
        taskItem.dataset.taskId = task.id;
        taskItem.innerHTML = `
            <div>${task.title}</div>
            <div>
                <span class="priority-badge priority-${task.priority}">${task.priority}</span>
                <span class="status-badge status-${task.status}">${task.status}</span>
            </div>
        `;
        taskItem.addEventListener('click', () => showTaskDetails(task.id));
        tasksList.appendChild(taskItem);
    });
}

// Mise à jour de la liste des messages
function updateMessagesList() {
    const messagesContainer = document.getElementById('messages');
    messagesContainer.innerHTML = '';
    
    if (messages.length === 0) {
        messagesContainer.innerHTML = '<div class="message message-system">Aucun message</div>';
        return;
    }
    
    messages.forEach(message => {
        const messageElement = document.createElement('div');
        const isUser = message.sender === 'user';
        const isSystem = message.sender === 'system';
        
        messageElement.className = `message ${isUser ? 'message-user' : isSystem ? 'message-system' : 'message-agent'}`;
        
        const date = new Date(message.timestamp);
        const formattedTime = date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
        
        messageElement.innerHTML = `
            ${!isUser && !isSystem ? `<strong>${message.sender}:</strong> ` : ''}
            ${message.content}
            <span class="message-meta">${formattedTime}</span>
        `;
        
        messagesContainer.appendChild(messageElement);
    });
    
    // Faire défiler jusqu'au dernier message
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Initialisation des graphiques
function initializeCharts() {
    // Graphique CPU
    const cpuCtx = document.getElementById('cpu-chart').getContext('2d');
    charts.cpu = new Chart(cpuCtx, {
        type: 'line',
        data: {
            labels: Array(20).fill(''),
            datasets: [{
                label: 'CPU (%)',
                data: Array(20).fill(0),
                borderColor: 'rgba(58, 134, 255, 1)',
                backgroundColor: 'rgba(58, 134, 255, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            animation: {
                duration: 500
            }
        }
    });
    
    // Graphique Mémoire
    const memoryCtx = document.getElementById('memory-chart').getContext('2d');
    charts.memory = new Chart(memoryCtx, {
        type: 'line',
        data: {
            labels: Array(20).fill(''),
            datasets: [{
                label: 'Mémoire (%)',
                data: Array(20).fill(0),
                borderColor: 'rgba(131, 56, 236, 1)',
                backgroundColor: 'rgba(131, 56, 236, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            animation: {
                duration: 500
            }
        }
    });
    
    // Graphique GPU (si disponible)
    const gpuCtx = document.getElementById('gpu-chart').getContext('2d');
    charts.gpu = new Chart(gpuCtx, {
        type: 'line',
        data: {
            labels: Array(20).fill(''),
            datasets: [{
                label: 'GPU (%)',
                data: Array(20).fill(0),
                borderColor: 'rgba(255, 0, 110, 1)',
                backgroundColor: 'rgba(255, 0, 110, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            animation: {
                duration: 500
            }
        }
    });
}

// Mise à jour des statistiques de ressources
function updateResourceStats(data) {
    const current = data.current;
    
    if (current) {
        const cpuPercent = current.cpu?.percent || 0;
        const memoryPercent = current.memory?.percent || 0;
        const memoryUsed = current.memory?.used_gb || 0;
        const memoryTotal = current.memory?.total_gb || 0;
        
        let resourcesText = `CPU: ${cpuPercent.toFixed(1)}% | RAM: ${memoryUsed.toFixed(1)}/${memoryTotal.toFixed(1)} GB`;
        
        // Ajouter les statistiques GPU si disponibles
        if (current.gpu && Array.isArray(current.gpu)) {
            const gpuStats = current.gpu[0];
            if (gpuStats && gpuStats.memory_used !== undefined) {
                const gpuMemUsed = gpuStats.memory_used;
                const gpuMemTotal = gpuStats.memory_total || 0;
                const gpuPercent = gpuMemUsed && gpuMemTotal ? (gpuMemUsed / gpuMemTotal * 100).toFixed(1) : 0;
                
                resourcesText += ` | GPU: ${gpuPercent}% (${gpuMemUsed.toFixed(1)}/${gpuMemTotal.toFixed(1)} GB)`;
                document.getElementById('gpu-container').style.display = 'block';
            } else {
                document.getElementById('gpu-container').style.display = 'none';
            }
        } else {
            document.getElementById('gpu-container').style.display = 'none';
        }
        
        document.getElementById('system-resources').textContent = resourcesText;
    }
}

// Mise à jour des graphiques
function updateCharts(data) {
    if (!data.history || !data.history.length) return;
    
    const history = data.history;
    const labels = history.map((_, index) => index);
    
    // Mettre à jour le graphique CPU
    const cpuData = history.map(item => item.cpu?.percent || 0);
    charts.cpu.data.labels = labels;
    charts.cpu.data.datasets[0].data = cpuData;
    charts.cpu.update();
    
    // Mettre à jour le graphique Mémoire
    const memoryData = history.map(item => item.memory?.percent || 0);
    charts.memory.data.labels = labels;
    charts.memory.data.datasets[0].data = memoryData;
    charts.memory.update();
    
    // Mettre à jour le graphique GPU si disponible
    if (history[0].gpu && Array.isArray(history[0].gpu) && history[0].gpu[0]) {
        const gpuData = history.map(item => {
            if (item.gpu && Array.isArray(item.gpu) && item.gpu[0]) {
                const gpuStats = item.gpu[0];
                if (gpuStats.memory_used !== undefined && gpuStats.memory_total) {
                    return (gpuStats.memory_used / gpuStats.memory_total * 100);
                }
            }
            return 0;
        });
        
        charts.gpu.data.labels = labels;
        charts.gpu.data.datasets[0].data = gpuData;
        charts.gpu.update();
        document.getElementById('gpu-container').style.display = 'block';
    } else {
        document.getElementById('gpu-container').style.display = 'none';
    }
}

// Afficher les détails d'une tâche
function showTaskDetails(taskId) {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;
    
    currentTask = task;
    
    // Masquer la zone de chat et afficher les détails de la tâche
    document.querySelector('.chat-container').style.display = 'none';
    document.getElementById('task-detail-panel').style.display = 'block';
    
    // Remplir les détails de la tâche
    const taskDetailElement = document.getElementById('task-detail');
    
    const statusOptions = ['pending', 'in_progress', 'completed', 'failed'].map(status => {
        return `<option value="${status}" ${task.status === status ? 'selected' : ''}>${status}</option>`;
    }).join('');
    
    taskDetailElement.innerHTML = `
        <div class="task-detail-field">
            <label>ID</label>
            <div class="value">${task.id}</div>
        </div>
        <div class="task-detail-field">
            <label>Titre</label>
            <div class="value">${task.title}</div>
        </div>
        <div class="task-detail-field">
            <label>Description</label>
            <div class="value">${task.description}</div>
        </div>
        <div class="task-detail-field">
            <label>Assigné à</label>
            <div class="value">${task.assigned_to}</div>
        </div>
        <div class="task-detail-field">
            <label>Priorité</label>
            <div class="value">
                <span class="priority-badge priority-${task.priority}">${task.priority}</span>
            </div>
        </div>
        <div class="task-detail-field">
            <label>Statut</label>
            <div class="value">
                <select id="task-status-select">
                    ${statusOptions}
                </select>
            </div>
        </div>
        <div class="task-detail-field">
            <label>Créé le</label>
            <div class="value">${new Date(task.created_at).toLocaleString('fr-FR')}</div>
        </div>
        <div class="task-detail-field">
            <label>Mis à jour le</label>
            <div class="value">${new Date(task.updated_at).toLocaleString('fr-FR')}</div>
        </div>
        ${task.result ? `
        <div class="task-detail-field">
            <label>Résultat</label>
            <div class="value">${task.result}</div>
        </div>
        ` : ''}
    `;
}

// Retour à la vue de chat
function backToChat() {
    document.querySelector('.chat-container').style.display = 'flex';
    document.getElementById('task-detail-panel').style.display = 'none';
    currentTask = null;
}

// Mise à jour du statut d'une tâche
function updateTaskStatus() {
    if (!currentTask) return;
    
    const newStatus = document.getElementById('task-status-select').value;
    
    fetch(`/api/tasks/${currentTask.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            status: newStatus
        })
    })
    .then(response => response.json())
    .then(data => {
        showNotification(`Statut de la tâche mis à jour: ${newStatus}`, 'success');
        fetchTasks();
        backToChat();
    })
    .catch(error => {
        console.error('Erreur lors de la mise à jour du statut:', error);
        showNotification('Erreur lors de la mise à jour du statut', 'error');
    });
}

// Envoyer un message
function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const messageContent = messageInput.value.trim();
    
    if (!messageContent) return;
    
    const message = {
        sender: 'user',
        content: messageContent
    };
    
    fetch('/api/messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(message)
    })
    .then(response => response.json())
    .then(data => {
        messageInput.value = '';
        fetchMessages();
    })
    .catch(error => {
        console.error('Erreur lors de l\'envoi du message:', error);
        showNotification('Erreur lors de l\'envoi du message', 'error');
    });
}

// Créer une nouvelle tâche
function createTask(event) {
    event.preventDefault();
    
    const titleInput = document.getElementById('task-title');
    const descriptionInput = document.getElementById('task-description');
    const agentSelect = document.getElementById('task-agent');
    const prioritySelect = document.getElementById('task-priority');
    
    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();
    const assignedTo = agentSelect.value;
    const priority = prioritySelect.value;
    
    if (!title || !description || !assignedTo) {
        showNotification('Veuillez remplir tous les champs', 'warning');
        return;
    }
    
    const task = {
        title,
        description,
        assigned_to: assignedTo,
        priority
    };
    
    fetch('/api/tasks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(task)
    })
    .then(response => response.json())
    .then(data => {
        showNotification('Tâche créée avec succès', 'success');
        closeModal();
        fetchTasks();
        
        // Réinitialiser le formulaire
        titleInput.value = '';
        descriptionInput.value = '';
    })
    .catch(error => {
        console.error('Erreur lors de la création de la tâche:', error);
        showNotification('Erreur lors de la création de la tâche', 'error');
    });
}

// Mettre à jour le sélecteur d'agents pour les tâches
function updateTaskAgentSelector() {
    const taskAgentSelect = document.getElementById('task-agent');
    taskAgentSelect.innerHTML = '';
    
    agents.forEach(agent => {
        const option = document.createElement('option');
        option.value = agent.id;
        option.textContent = agent.name;
        taskAgentSelect.appendChild(option);
    });
}

// Afficher le modal
function showModal() {
    const modal = document.getElementById('modal');
    modal.style.display = 'flex';
}

// Fermer le modal
function closeModal() {
    const modal = document.getElementById('modal');
    modal.style.display = 'none';
}

// Afficher une notification
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Démarrer les mises à jour périodiques
function startPeriodicUpdates() {
    // Mettre à jour les agents toutes les 30 secondes
    setInterval(fetchAgents, 30000);
    
    // Mettre à jour les tâches toutes les 10 secondes
    setInterval(fetchTasks, 10000);
    
    // Mettre à jour les messages toutes les 5 secondes
    setInterval(fetchMessages, 5000);
    
    // Mettre à jour les statistiques toutes les 2 secondes
    setInterval(fetchMonitoringStats, 2000);
}

// Attacher les gestionnaires d'événements
function attachEventListeners() {
    // Formulaire d'envoi de message
    document.getElementById('send-message-btn').addEventListener('click', sendMessage);
    document.getElementById('message-input').addEventListener('keypress', event => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Bouton de retour à la vue de chat
    document.getElementById('back-to-chat').addEventListener('click', backToChat);
    
    // Bouton de mise à jour du statut de la tâche
    document.getElementById('update-task-status').addEventListener('click', updateTaskStatus);
    
    // Bouton d'ajout de tâche
    document.getElementById('add-task-btn').addEventListener('click', showModal);
    
    // Fermeture du modal
    document.querySelector('.close').addEventListener('click', closeModal);
    window.addEventListener('click', event => {
        const modal = document.getElementById('modal');
        if (event.target === modal) {
            closeModal();
        }
    });
    
    // Formulaire de création de tâche
    document.getElementById('task-form').addEventListener('submit', createTask);
}
