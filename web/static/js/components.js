/**
 * components.js - Gestionnaire moderne des composants de l'application
 * Centralise l'enregistrement et l'accès aux composants
 */

// Implémentation du système de composants avec pattern module
const ComponentManager = (function() {
    // Stockage privé pour les composants
    const components = new Map();
    
    // API publique
    return {
        /**
         * Enregistre un composant dans le gestionnaire
         * @param {string} name - Nom du composant
         * @param {Object} component - Instance du composant
         * @returns {Object} - Le composant enregistré
         */
        register: function(name, component) {
            if (!name || typeof name !== 'string') {
                console.error('Le nom du composant doit être une chaîne de caractères valide');
                return null;
            }
            
            if (!component || typeof component !== 'object') {
                console.error(`Le composant '${name}' doit être un objet valide`);
                return null;
            }
            
            // Stocker le composant
            components.set(name, component);
            console.log(`📦 Composant '${name}' enregistré`);
            
            return component;
        },
        
        /**
         * Récupère un composant par son nom
         * @param {string} name - Nom du composant
         * @returns {Object|null} - Le composant ou null s'il n'existe pas
         */
        get: function(name) {
            if (!components.has(name)) {
                console.warn(`Le composant '${name}' n'est pas enregistré`);
                return null;
            }
            
            return components.get(name);
        },
        
        /**
         * Vérifie si un composant existe
         * @param {string} name - Nom du composant
         * @returns {boolean} - Vrai si le composant existe
         */
        has: function(name) {
            return components.has(name);
        },
        
        /**
         * Liste tous les composants enregistrés
         * @returns {Array} - Liste des noms de composants
         */
        list: function() {
            return Array.from(components.keys());
        },
        
        /**
         * Initialise tous les composants
         */
        initAll: function() {
            console.log('🔄 Initialisation de tous les composants');
            
            components.forEach((component, name) => {
                if (typeof component.init === 'function') {
                    try {
                        component.init();
                        console.log(`✅ Composant '${name}' initialisé`);
                    } catch (error) {
                        console.error(`Erreur lors de l'initialisation du composant '${name}':`, error);
                    }
                }
            });
        }
    };
})();

// Rendre l'objet disponible globalement
window.app = window.app || {};
window.app.components = ComponentManager;

// Pour compatibilité avec l'ancien système (sera supprimé dans une future version)
window.Components = window.Components || {};
Object.defineProperty(window, 'Components', {
    get: function() {
        console.warn("L'objet « Components » est obsolète. Il sera bientôt supprimé.");
        return this._Components;
    },
    set: function(value) {
        this._Components = value;
    }
}); 