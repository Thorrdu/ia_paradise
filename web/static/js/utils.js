/**
 * utils.js - Fonctions utilitaires pour Paradis IA V3
 * Centralise les fonctions utilitaires réutilisables dans l'application
 */

const Utils = {
    /**
     * Gestion des notifications (toasts)
     */
    toast: {
        /**
         * Affiche une notification toast
         * @param {string} message - Message à afficher
         * @param {string} type - Type de notification (success, error, warning, info)
         * @param {number} duration - Durée d'affichage en ms (défaut: 3000ms)
         */
        show: (message, type = 'info', duration = 3000) => {
            const container = document.getElementById('toast-container');
            if (!container) return;
            
            // Créer l'élément toast
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            
            // Ajouter l'icône en fonction du type
            let icon = '';
            switch (type) {
                case 'success': icon = '<i class="fas fa-check-circle"></i>'; break;
                case 'error': icon = '<i class="fas fa-exclamation-circle"></i>'; break;
                case 'warning': icon = '<i class="fas fa-exclamation-triangle"></i>'; break;
                default: icon = '<i class="fas fa-info-circle"></i>';
            }
            
            // Structurer le contenu
            toast.innerHTML = `
                <div class="toast-icon">${icon}</div>
                <div class="toast-content">${message}</div>
                <button class="toast-close"><i class="fas fa-times"></i></button>
            `;
            
            // Ajouter au container
            container.appendChild(toast);
            
            // Animation d'entrée
            setTimeout(() => {
                toast.classList.add('show');
            }, 10);
            
            // Fermeture automatique
            const timeout = setTimeout(() => {
                Utils.toast.hide(toast);
            }, duration);
            
            // Gestionnaire de fermeture manuelle
            const closeBtn = toast.querySelector('.toast-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    clearTimeout(timeout);
                    Utils.toast.hide(toast);
                });
            }
            
            return toast;
        },
        
        /**
         * Cache et supprime une notification toast
         * @param {HTMLElement} toast - Élément toast à supprimer
         */
        hide: (toast) => {
            toast.classList.remove('show');
            toast.classList.add('hide');
            
            // Supprimer après l'animation
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
    },
    
    /**
     * Gestion des modales
     */
    modal: {
        /**
         * Ouvre une modale
         * @param {string} modalId - ID de la modale à ouvrir
         */
        open: (modalId) => {
            const modal = document.getElementById(modalId);
            if (!modal) return;
            
            modal.classList.add('open');
            document.body.classList.add('modal-open');
            
            // Gestionnaires pour fermer la modale
            const closeButtons = modal.querySelectorAll('.modal-close, [data-dismiss="modal"]');
            closeButtons.forEach(btn => {
                btn.addEventListener('click', () => Utils.modal.close(modalId));
            });
            
            // Fermer en cliquant en dehors
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    Utils.modal.close(modalId);
                }
            });
            
            return modal;
        },
        
        /**
         * Ferme une modale
         * @param {string} modalId - ID de la modale à fermer
         */
        close: (modalId) => {
            const modal = document.getElementById(modalId);
            if (!modal) return;
            
            modal.classList.remove('open');
            document.body.classList.remove('modal-open');
        }
    },
    
    /**
     * Formateurs de données
     */
    format: {
        /**
         * Formate une date
         * @param {string|Date} date - Date à formater
         * @param {boolean} includeTime - Inclure l'heure
         * @returns {string} Date formatée
         */
        date: (date, includeTime = false) => {
            if (!date) return '';
            
            const d = new Date(date);
            const options = { 
                day: '2-digit', 
                month: '2-digit', 
                year: 'numeric'
            };
            
            if (includeTime) {
                options.hour = '2-digit';
                options.minute = '2-digit';
                options.second = '2-digit';
            }
            
            return d.toLocaleDateString('fr-FR', options);
        },
        
        /**
         * Formate une taille de fichier (octets -> KB, MB, GB)
         * @param {number} bytes - Taille en octets
         * @returns {string} Taille formatée
         */
        fileSize: (bytes) => {
            if (bytes === 0) return '0 Octet';
            
            const k = 1024;
            const sizes = ['Octets', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },
        
        /**
         * Abrège un nombre (ex: 1200 -> 1.2K)
         * @param {number} num - Nombre à formater
         * @returns {string} Nombre formaté
         */
        number: (num) => {
            if (num < 1000) return num.toString();
            
            const abbreviations = ['', 'K', 'M', 'B', 'T'];
            const tier = Math.floor(Math.log10(Math.abs(num)) / 3);
            
            if (tier === 0) return num.toString();
            
            const suffix = abbreviations[tier];
            const scale = Math.pow(10, tier * 3);
            const scaled = num / scale;
            
            return scaled.toFixed(1) + suffix;
        },
        
        /**
         * Formate un temps écoulé (ex: il y a 5 minutes)
         * @param {string|Date} date - Date à comparer
         * @returns {string} Texte formaté
         */
        timeAgo: (date) => {
            if (!date) return '';
            
            const now = new Date();
            const past = new Date(date);
            const seconds = Math.floor((now - past) / 1000);
            
            if (seconds < 60) {
                return "à l'instant";
            }
            
            const minutes = Math.floor(seconds / 60);
            if (minutes < 60) {
                return `il y a ${minutes} minute${minutes > 1 ? 's' : ''}`;
            }
            
            const hours = Math.floor(minutes / 60);
            if (hours < 24) {
                return `il y a ${hours} heure${hours > 1 ? 's' : ''}`;
            }
            
            const days = Math.floor(hours / 24);
            if (days < 30) {
                return `il y a ${days} jour${days > 1 ? 's' : ''}`;
            }
            
            return Utils.format.date(date, true);
        }
    },
    
    /**
     * Gestion du thème (clair/sombre)
     */
    theme: {
        /**
         * Initialise le gestionnaire de thème
         */
        init: () => {
            const toggle = document.getElementById('dark-mode-toggle');
            if (!toggle) return;
            
            // Vérifier les préférences utilisateur
            const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            const savedTheme = localStorage.getItem('theme');
            
            // Déterminer le thème initial
            if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
                document.body.classList.add('dark-theme');
                toggle.checked = true;
            }
            
            // Gestionnaire pour le toggle
            toggle.addEventListener('change', () => {
                if (toggle.checked) {
                    document.body.classList.add('dark-theme');
                    localStorage.setItem('theme', 'dark');
                } else {
                    document.body.classList.remove('dark-theme');
                    localStorage.setItem('theme', 'light');
                }
            });
        },
        
        /**
         * Définit explicitement le thème
         * @param {string} mode - 'light' ou 'dark'
         */
        set: (mode) => {
            const toggle = document.getElementById('dark-mode-toggle');
            
            if (mode === 'dark') {
                document.body.classList.add('dark-theme');
                if (toggle) toggle.checked = true;
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark-theme');
                if (toggle) toggle.checked = false;
                localStorage.setItem('theme', 'light');
            }
        }
    },
    
    /**
     * Méthodes DOM et animations
     */
    dom: {
        /**
         * Crée une animation de chargement
         * @param {HTMLElement} container - Élément conteneur
         * @param {string} message - Message à afficher
         */
        createLoader: (container, message = 'Chargement...') => {
            container.innerHTML = `
                <div class="loading-indicator">
                    <i class="fas fa-circle-notch fa-spin"></i>
                    <span>${message}</span>
                </div>
            `;
        },
        
        /**
         * Affiche un message d'erreur
         * @param {HTMLElement} container - Élément conteneur
         * @param {string} message - Message d'erreur
         */
        showError: (container, message) => {
            container.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>${message}</span>
                </div>
            `;
        },
        
        /**
         * Affiche un message "aucune donnée"
         * @param {HTMLElement} container - Élément conteneur
         * @param {string} message - Message à afficher
         */
        showEmpty: (container, message = 'Aucune donnée disponible') => {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <span>${message}</span>
                </div>
            `;
        }
    }
};

// Exporter l'objet Utils pour utilisation dans d'autres modules
window.Utils = Utils; 