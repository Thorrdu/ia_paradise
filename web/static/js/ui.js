/**
 * ui.js - Module de gestion de l'interface utilisateur
 * Gère les éléments UI communs à toute l'application
 */

const UI = {
    /**
     * Initialise l'interface utilisateur
     */
    init: () => {
        console.log('🎨 Initialisation de l\'interface utilisateur');
        
        // Initialiser le thème
        if (window.Utils && Utils.theme) {
            Utils.theme.init();
        }
        
        // Initialiser les composants UI communs
        UI.initToasts();
        UI.initModals();
        UI.initDropdowns();
        UI.initMobileMenu();
        
        // Gestionnaires d'événements globaux
        UI.initGlobalEventListeners();
    },
    
    /**
     * Initialise le système de notifications toast
     */
    initToasts: () => {
        // Créer le conteneur de toasts s'il n'existe pas
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
    },
    
    /**
     * Initialise les modales
     */
    initModals: () => {
        // Gestionnaires pour fermer les modales
        document.querySelectorAll('.modal-close, [data-dismiss="modal"]').forEach(button => {
            button.addEventListener('click', event => {
                event.preventDefault();
                const modal = button.closest('.modal');
                if (modal) {
                    UI.modal.close(modal.id);
                }
            });
        });
        
        // Fermer la modale en cliquant à l'extérieur
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', event => {
                if (event.target === overlay) {
                    const modal = overlay.querySelector('.modal');
                    if (modal) {
                        UI.modal.close(modal.id);
                    }
                }
            });
        });
    },
    
    /**
     * Initialise les menus déroulants
     */
    initDropdowns: () => {
        document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
            toggle.addEventListener('click', event => {
                event.preventDefault();
                const dropdown = toggle.closest('.dropdown');
                if (dropdown) {
                    dropdown.classList.toggle('open');
                }
            });
        });
        
        // Fermer les dropdowns en cliquant ailleurs
        document.addEventListener('click', event => {
            if (!event.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown.open').forEach(dropdown => {
                    dropdown.classList.remove('open');
                });
            }
        });
    },
    
    /**
     * Initialise le menu mobile
     */
    initMobileMenu: () => {
        const toggleBtn = document.getElementById('mobile-menu-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                const container = document.querySelector('.app-container');
                if (container) {
                    container.classList.toggle('mobile-menu-open');
                }
            });
        }
    },
    
    /**
     * Initialise des écouteurs d'événements globaux
     */
    initGlobalEventListeners: () => {
        // Gérer les boutons de copie
        document.addEventListener('click', event => {
            const copyBtn = event.target.closest('[data-copy]');
            if (copyBtn) {
                const textToCopy = copyBtn.getAttribute('data-copy');
                if (textToCopy) {
                    navigator.clipboard.writeText(textToCopy)
                        .then(() => {
                            UI.toast.show('Copié dans le presse-papiers', 'success');
                            
                            // Changer temporairement l'icône
                            const icon = copyBtn.querySelector('i');
                            if (icon) {
                                const originalClass = icon.className;
                                icon.className = 'fas fa-check';
                                
                                setTimeout(() => {
                                    icon.className = originalClass;
                                }, 1000);
                            }
                        })
                        .catch(err => {
                            console.error('Erreur lors de la copie:', err);
                            UI.toast.show('Erreur lors de la copie', 'error');
                        });
                }
            }
        });
    },
    
    /**
     * Met à jour le statut du système dans l'UI
     * @param {string} mode - Mode du système (FULL, LIMITED, OFFLINE)
     */
    updateSystemStatus: (mode) => {
        const statusIndicator = document.getElementById('system-status');
        const statusText = document.getElementById('system-status-text');
        
        if (!statusIndicator) return;
        
        // Retirer les classes existantes
        statusIndicator.classList.remove('status-full', 'status-limited', 'status-offline');
        
        // Ajouter la classe appropriée et mettre à jour le texte
        switch (mode.toUpperCase()) {
            case 'FULL':
                statusIndicator.classList.add('status-full');
                if (statusText) statusText.textContent = 'Système complet';
                break;
            case 'LIMITED':
                statusIndicator.classList.add('status-limited');
                if (statusText) statusText.textContent = 'Mode limité';
                break;
            case 'OFFLINE':
            default:
                statusIndicator.classList.add('status-offline');
                if (statusText) statusText.textContent = 'Hors ligne';
                break;
        }
    },
    
    /**
     * Met à jour les compteurs dans la barre latérale
     * @param {Object} counts - Objet contenant les compteurs à mettre à jour
     */
    updateSidebarCounts: (counts = {}) => {
        Object.entries(counts).forEach(([key, value]) => {
            document.querySelectorAll(`.sidebar-count[data-count="${key}"]`).forEach(el => {
                el.textContent = value;
            });
        });
    },
    
    /**
     * Système de notifications toast
     */
    toast: {
        /**
         * Affiche une notification toast
         * @param {string} message - Message à afficher
         * @param {string} type - Type de toast (success, error, warning, info)
         * @param {Object} options - Options supplémentaires
         */
        show: (message, type = 'info', options = {}) => {
            const container = document.querySelector('.toast-container');
            if (!container) return;
            
            // Créer l'élément toast
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            
            // Définir la durée
            const duration = options.duration || CONFIG.ui.notifications.duration || 5000;
            
            // Icône en fonction du type
            let icon = 'info-circle';
            switch (type) {
                case 'success': icon = 'check-circle'; break;
                case 'error': icon = 'times-circle'; break;
                case 'warning': icon = 'exclamation-triangle'; break;
            }
            
            // Créer le contenu du toast
            toast.innerHTML = `
                <div class="toast-icon"><i class="fas fa-${icon}"></i></div>
                <div class="toast-content">${message}</div>
                <button class="toast-close"><i class="fas fa-times"></i></button>
            `;
            
            // Ajouter au conteneur
            container.appendChild(toast);
            
            // Animation d'entrée
            setTimeout(() => {
                toast.classList.add('show');
            }, 10);
            
            // Bouton de fermeture
            const closeBtn = toast.querySelector('.toast-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    UI.toast.close(toast);
                });
            }
            
            // Auto-fermeture après la durée spécifiée
            if (duration > 0) {
                setTimeout(() => {
                    UI.toast.close(toast);
                }, duration);
            }
            
            // Limiter le nombre de toasts visibles
            const maxToasts = CONFIG.ui.notifications.maxVisible || 5;
            const toasts = container.querySelectorAll('.toast');
            if (toasts.length > maxToasts) {
                for (let i = 0; i < toasts.length - maxToasts; i++) {
                    UI.toast.close(toasts[i]);
                }
            }
            
            return toast;
        },
        
        /**
         * Ferme une notification toast
         * @param {HTMLElement} toast - Élément toast à fermer
         */
        close: (toast) => {
            if (!toast) return;
            
            // Animation de sortie
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
     * Système de modales
     */
    modal: {
        /**
         * Ouvre une modale
         * @param {string} modalId - ID de la modale à ouvrir
         * @param {Object} data - Données à passer à la modale
         */
        open: (modalId, data = {}) => {
            const modal = document.getElementById(modalId);
            if (!modal) return;
            
            // Stocker les données
            if (data) {
                modal.dataset.modalData = JSON.stringify(data);
            }
            
            // Afficher la modale
            modal.closest('.modal-overlay').classList.add('open');
            modal.classList.add('open');
            
            // Déclencher l'événement d'ouverture
            const event = new CustomEvent('modal:open', { detail: { modalId, data } });
            modal.dispatchEvent(event);
            
            // Désactiver le défilement du body
            document.body.classList.add('modal-open');
        },
        
        /**
         * Ferme une modale
         * @param {string} modalId - ID de la modale à fermer
         */
        close: (modalId) => {
            const modal = document.getElementById(modalId);
            if (!modal) return;
            
            // Cacher la modale
            modal.classList.remove('open');
            modal.closest('.modal-overlay').classList.remove('open');
            
            // Déclencher l'événement de fermeture
            const event = new CustomEvent('modal:close', { detail: { modalId } });
            modal.dispatchEvent(event);
            
            // Réactiver le défilement du body s'il n'y a plus de modales ouvertes
            if (!document.querySelector('.modal.open')) {
                document.body.classList.remove('modal-open');
            }
        },
        
        /**
         * Récupère les données associées à une modale
         * @param {string} modalId - ID de la modale
         * @return {Object} Données de la modale
         */
        getData: (modalId) => {
            const modal = document.getElementById(modalId);
            if (!modal || !modal.dataset.modalData) return {};
            
            try {
                return JSON.parse(modal.dataset.modalData);
            } catch (error) {
                console.error('Erreur lors de la récupération des données de la modale:', error);
                return {};
            }
        }
    }
};

// Rendre l'UI disponible globalement
window.UI = UI; 