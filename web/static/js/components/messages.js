/**
 * messages.js - Composant de gestion des messages
 * Gère l'affichage et l'envoi des messages entre agents
 */

const Messages = {
    /**
     * Initialise le composant de messages
     */
    init: () => {
        console.log('💬 Initialisation du composant de messages');
        
        // Initialiser les gestionnaires d'événements
        Messages.initEventListeners();
        
        // Charger les messages si on est sur la page messages
        if (document.querySelector('.messages-page')) {
            Messages.loadMessages();
        }
    },
    
    /**
     * Initialise les gestionnaires d'événements
     */
    initEventListeners: () => {
        // Formulaire d'envoi de message
        const messageForm = document.getElementById('send-message-form');
        if (messageForm) {
            messageForm.addEventListener('submit', (e) => {
                e.preventDefault();
                Messages.sendMessage();
            });
        }
        
        // Filtrage des messages par agent
        const agentFilter = document.getElementById('message-agent-filter');
        if (agentFilter) {
            agentFilter.addEventListener('change', () => {
                const agentId = agentFilter.value;
                Messages.loadMessages(agentId);
            });
        }
    },
    
    /**
     * Charge les messages
     * @param {string} agentId - ID de l'agent pour filtrer les messages (optionnel)
     */
    loadMessages: async (agentId = null) => {
        try {
            // Afficher l'état de chargement
            const messagesContainer = document.getElementById('messages-container');
            if (messagesContainer) {
                messagesContainer.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Chargement des messages...</p>
                    </div>
                `;
            }
            
            // Récupérer les messages
            let messages;
            if (agentId) {
                messages = await API.Messages.getForAgent(agentId);
            } else {
                messages = await API.Messages.getAll();
            }
            
            // Trier les messages par date (plus récent en premier)
            messages.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            
            // Mettre à jour l'affichage des messages
            if (messagesContainer) {
                if (messages.length === 0) {
                    messagesContainer.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-comment-slash"></i>
                            <p>Aucun message</p>
                        </div>
                    `;
                } else {
                    messagesContainer.innerHTML = `
                        <div class="messages-list">
                            ${messages.map(message => Messages.renderMessageItem(message)).join('')}
                        </div>
                    `;
                    
                    // Ajouter les interactions aux messages
                    Messages.initMessageInteractions();
                }
            }
            
            // Mettre à jour le compteur de messages dans la sidebar
            UI.updateSidebarCounts({ messages: messages.length });
            
            return messages;
        } catch (error) {
            console.error('Erreur lors du chargement des messages:', error);
            
            const messagesContainer = document.getElementById('messages-container');
            if (messagesContainer) {
                messagesContainer.innerHTML = `
                    <div class="error-state">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Erreur lors du chargement des messages</p>
                    </div>
                `;
            }
            
            throw error;
        }
    },
    
    /**
     * Envoie un nouveau message
     */
    sendMessage: async () => {
        const messageForm = document.getElementById('send-message-form');
        if (!messageForm) return;
        
        // Récupérer les valeurs du formulaire
        const contentInput = document.getElementById('message-content');
        const agentSelect = document.getElementById('message-agent');
        const prioritySelect = document.getElementById('message-priority');
        
        if (!contentInput || !agentSelect) {
            UI.toast.show('Formulaire incomplet', 'error');
            return;
        }
        
        const content = contentInput.value.trim();
        const agentId = agentSelect.value;
        const priority = prioritySelect ? prioritySelect.value : 'MEDIUM';
        
        // Valider les entrées
        if (!content) {
            UI.toast.show('Le message ne peut pas être vide', 'error');
            return;
        }
        
        if (!agentId) {
            UI.toast.show('Veuillez sélectionner un agent', 'error');
            return;
        }
        
        try {
            // Désactiver le formulaire pendant l'envoi
            const submitButton = messageForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Envoi...';
            }
            
            // Préparer les données du message
            const messageData = {
                content,
                agent_id: agentId,
                priority,
                sender: 'user',
                timestamp: new Date().toISOString()
            };
            
            // Envoyer le message
            const result = await API.Messages.send(messageData);
            
            // Réinitialiser le formulaire
            contentInput.value = '';
            
            // Recharger les messages
            await Messages.loadMessages(agentId);
            
            // Afficher une notification
            UI.toast.show('Message envoyé avec succès', 'success');
            
            return result;
        } catch (error) {
            console.error('Erreur lors de l\'envoi du message:', error);
            UI.toast.show('Erreur lors de l\'envoi du message', 'error');
            throw error;
        } finally {
            // Réactiver le formulaire
            const submitButton = messageForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-paper-plane"></i> Envoyer';
            }
        }
    },
    
    /**
     * Charge les agents dans le sélecteur
     */
    loadAgentSelector: async () => {
        try {
            const agentSelect = document.getElementById('message-agent');
            const filterSelect = document.getElementById('message-agent-filter');
            
            if (!agentSelect && !filterSelect) return;
            
            // Récupérer la liste des agents
            const agents = await API.Agents.getAll();
            
            // Mettre à jour le sélecteur d'agent pour l'envoi
            if (agentSelect) {
                // Conserver l'option vide
                const emptyOption = agentSelect.querySelector('option[value=""]');
                agentSelect.innerHTML = '';
                
                if (emptyOption) {
                    agentSelect.appendChild(emptyOption);
                }
                
                // Ajouter les agents
                agents.forEach(agent => {
                    const option = document.createElement('option');
                    option.value = agent.id;
                    option.textContent = agent.name;
                    agentSelect.appendChild(option);
                });
            }
            
            // Mettre à jour le filtre d'agent
            if (filterSelect) {
                // Conserver l'option "Tous"
                const allOption = filterSelect.querySelector('option[value=""]');
                filterSelect.innerHTML = '';
                
                if (allOption) {
                    filterSelect.appendChild(allOption);
                }
                
                // Ajouter les agents
                agents.forEach(agent => {
                    const option = document.createElement('option');
                    option.value = agent.id;
                    option.textContent = agent.name;
                    filterSelect.appendChild(option);
                });
            }
            
            return agents;
        } catch (error) {
            console.error('Erreur lors du chargement des agents:', error);
            UI.toast.show('Erreur lors du chargement des agents', 'error');
            throw error;
        }
    },
    
    /**
     * Génère le HTML pour un message
     * @param {Object} message - Message à afficher
     * @return {string} HTML du message
     */
    renderMessageItem: (message) => {
        // Formater la date
        const date = new Date(message.timestamp);
        const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        
        // Déterminer la classe CSS en fonction de l'expéditeur
        const messageClass = message.sender === 'user' ? 'message-sent' : 'message-received';
        
        // Déterminer l'icône en fonction de l'expéditeur
        const icon = message.sender === 'user' ? 'user' : 'robot';
        
        // Déterminer la couleur de priorité
        let priorityClass = 'priority-medium';
        if (message.priority) {
            priorityClass = `priority-${message.priority.toLowerCase()}`;
        }
        
        return `
            <div class="message-item ${messageClass} ${priorityClass}" data-id="${message.id}">
                <div class="message-sender">
                    <div class="message-avatar">
                        <i class="fas fa-${icon}"></i>
                    </div>
                    <div class="message-sender-info">
                        <div class="message-sender-name">${message.sender === 'user' ? 'Utilisateur' : message.agent_name || 'Agent'}</div>
                        <div class="message-time">${formattedDate}</div>
                    </div>
                </div>
                <div class="message-content">${message.content}</div>
                <div class="message-actions">
                    <button class="btn btn-icon btn-sm message-reply" title="Répondre">
                        <i class="fas fa-reply"></i>
                    </button>
                    <button class="btn btn-icon btn-sm message-copy" title="Copier" data-copy="${message.content}">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
            </div>
        `;
    },
    
    /**
     * Initialise les interactions avec les messages
     */
    initMessageInteractions: () => {
        // Boutons de réponse
        document.querySelectorAll('.message-reply').forEach(button => {
            button.addEventListener('click', (e) => {
                const messageItem = e.target.closest('.message-item');
                if (!messageItem) return;
                
                const messageContent = messageItem.querySelector('.message-content').textContent;
                const contentInput = document.getElementById('message-content');
                
                if (contentInput) {
                    contentInput.value = `En réponse à "${messageContent.substring(0, 50)}${messageContent.length > 50 ? '...' : ''}"\n\n`;
                    contentInput.focus();
                    
                    // Faire défiler jusqu'au formulaire
                    const messageForm = document.getElementById('send-message-form');
                    if (messageForm) {
                        messageForm.scrollIntoView({ behavior: 'smooth' });
                    }
                }
            });
        });
    }
};

// Enregistrer le composant dans le nouveau gestionnaire
if (window.app && window.app.components) {
    window.app.components.register('Messages', Messages);
} else {
    // Compatibilité temporaire avec l'ancien système
    window.Components = window.Components || {};
    window.Components.Messages = Messages;
} 