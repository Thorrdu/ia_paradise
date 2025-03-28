/**
 * api.js - Module de communication avec l'API
 * Fournit des fonctions pour interagir avec le backend
 */

const API = {
    // URL de base de l'API
    baseUrl: '/api',
    
    /**
     * Effectue une requête à l'API
     * @param {string} endpoint - Point de terminaison API
     * @param {Object} options - Options de la requête fetch
     * @return {Promise} Promise résolue avec les données de la réponse
     */
    request: async (endpoint, options = {}) => {
        const url = `${API.baseUrl}${endpoint}`;
        
        // Options par défaut
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };
        
        // Fusionner les options
        const fetchOptions = { ...defaultOptions, ...options };
        
        // Convertir le corps en JSON si c'est un objet
        if (fetchOptions.body && typeof fetchOptions.body === 'object') {
            fetchOptions.body = JSON.stringify(fetchOptions.body);
        }
        
        try {
            const response = await fetch(url, fetchOptions);
            
            // Vérifier si la requête a réussi
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Erreur API (${response.status}): ${errorText}`);
            }
            
            // Vérifier si la réponse est du JSON
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error(`Erreur lors de la requête API à ${url}:`, error);
            throw error;
        }
    },
    
    /**
     * API pour les agents
     */
    Agents: {
        /**
         * Récupère tous les agents
         * @return {Promise<Array>} Liste des agents
         */
        getAll: () => API.request('/agents'),
        
        /**
         * Récupère un agent par son ID
         * @param {string} id - ID de l'agent
         * @return {Promise<Object>} Détails de l'agent
         */
        getById: (id) => API.request(`/agents/${id}`),
        
        /**
         * Crée un nouvel agent
         * @param {Object} agent - Données de l'agent
         * @return {Promise<Object>} Agent créé
         */
        create: (agent) => API.request('/agents', {
            method: 'POST',
            body: agent
        }),
        
        /**
         * Met à jour un agent
         * @param {string} id - ID de l'agent
         * @param {Object} data - Données à mettre à jour
         * @return {Promise<Object>} Agent mis à jour
         */
        update: (id, data) => API.request(`/agents/${id}`, {
            method: 'PUT',
            body: data
        }),
        
        /**
         * Supprime un agent
         * @param {string} id - ID de l'agent
         * @return {Promise<Object>} Résultat de la suppression
         */
        delete: (id) => API.request(`/agents/${id}`, {
            method: 'DELETE'
        })
    },
    
    /**
     * API pour les tâches
     */
    Tasks: {
        /**
         * Récupère toutes les tâches
         * @return {Promise<Array>} Liste des tâches
         */
        getAll: () => API.request('/tasks'),
        
        /**
         * Récupère une tâche par son ID
         * @param {string} id - ID de la tâche
         * @return {Promise<Object>} Détails de la tâche
         */
        getById: (id) => API.request(`/tasks/${id}`),
        
        /**
         * Crée une nouvelle tâche
         * @param {Object} task - Données de la tâche
         * @return {Promise<Object>} Tâche créée
         */
        create: (task) => API.request('/tasks', {
            method: 'POST',
            body: task
        }),
        
        /**
         * Met à jour une tâche
         * @param {string} id - ID de la tâche
         * @param {Object} data - Données à mettre à jour
         * @return {Promise<Object>} Tâche mise à jour
         */
        update: (id, data) => API.request(`/tasks/${id}`, {
            method: 'PUT',
            body: data
        }),
        
        /**
         * Met à jour le statut d'une tâche
         * @param {string} id - ID de la tâche
         * @param {string} status - Nouveau statut
         * @return {Promise<Object>} Tâche mise à jour
         */
        updateStatus: (id, status) => API.request(`/tasks/${id}/status`, {
            method: 'PUT',
            body: { status }
        }),
        
        /**
         * Supprime une tâche
         * @param {string} id - ID de la tâche
         * @return {Promise<Object>} Résultat de la suppression
         */
        delete: (id) => API.request(`/tasks/${id}`, {
            method: 'DELETE'
        })
    },
    
    /**
     * API pour les messages
     */
    Messages: {
        /**
         * Récupère tous les messages
         * @param {Object} filters - Filtres (optionnels)
         * @return {Promise<Array>} Liste des messages
         */
        getAll: (filters = {}) => {
            const queryParams = new URLSearchParams();
            
            // Ajouter les filtres à l'URL
            Object.entries(filters).forEach(([key, value]) => {
                if (value !== undefined && value !== null) {
                    queryParams.append(key, value);
                }
            });
            
            const queryString = queryParams.toString();
            const url = queryString ? `/messages?${queryString}` : '/messages';
            
            return API.request(url);
        },
        
        /**
         * Récupère un message par son ID
         * @param {string} id - ID du message
         * @return {Promise<Object>} Détails du message
         */
        getById: (id) => API.request(`/messages/${id}`),
        
        /**
         * Envoie un nouveau message
         * @param {Object} message - Données du message
         * @return {Promise<Object>} Message envoyé
         */
        send: (message) => API.request('/messages', {
            method: 'POST',
            body: message
        }),
        
        /**
         * Récupère les messages pour un agent
         * @param {string} agentId - ID de l'agent
         * @return {Promise<Array>} Messages de l'agent
         */
        getForAgent: (agentId) => API.request(`/messages?agent_id=${agentId}`)
    },
    
    /**
     * API pour la surveillance système
     */
    Monitoring: {
        /**
         * Récupère les statistiques système actuelles
         * @return {Promise<Object>} Statistiques système
         */
        getStats: () => API.request('/monitoring'),
        
        /**
         * Récupère l'historique des statistiques système
         * @param {number} duration - Durée en minutes (défaut: 60)
         * @return {Promise<Object>} Historique des statistiques
         */
        getHistory: (duration = 60) => API.request(`/monitoring/history?duration=${duration}`)
    },
    
    /**
     * API pour les logs
     */
    Logs: {
        /**
         * Récupère les logs système récents
         * @param {number} limit - Nombre de logs à récupérer (défaut: 100)
         * @param {string} level - Niveau de log minimum (défaut: 'info')
         * @return {Promise<Array>} Liste des logs
         */
        getRecent: (limit = 100, level = 'info') => 
            API.request(`/logs?limit=${limit}&level=${level}`),
        
        /**
         * Récupère les logs pour un agent spécifique
         * @param {string} agentId - ID de l'agent
         * @param {number} limit - Nombre de logs à récupérer (défaut: 50)
         * @return {Promise<Array>} Logs de l'agent
         */
        getForAgent: (agentId, limit = 50) => 
            API.request(`/logs/agent/${agentId}?limit=${limit}`)
    },
    
    /**
     * API pour les modèles
     */
    Models: {
        /**
         * Récupère tous les modèles disponibles
         * @return {Promise<Array>} Liste des modèles
         */
        getAll: () => API.request('/models'),
        
        /**
         * Récupère l'état d'un modèle
         * @param {string} modelId - ID du modèle
         * @return {Promise<Object>} État du modèle
         */
        getStatus: (modelId) => API.request(`/models/${modelId}/status`)
    },
    
    /**
     * API pour le système
     */
    System: {
        /**
         * Récupère le mode du système (FULL ou LIMITED)
         * @return {Promise<string>} Mode système
         */
        getMode: () => API.request('/system/mode'),
        
        /**
         * Récupère l'état des services système
         * @return {Promise<Object>} État des services
         */
        getServices: () => API.request('/system/services'),
        
        /**
         * Récupère les informations sur la version
         * @return {Promise<Object>} Informations de version
         */
        getVersion: () => API.request('/system/version')
    }
};

// Rendre l'API disponible globalement
window.API = API; 