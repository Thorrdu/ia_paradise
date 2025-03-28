/**
 * app.js - Point d'entrée de l'application Paradis IA V3
 * Initialise tous les composants et gère l'application
 */

// Application principale
const App = {
    /**
     * Initialise l'application
     */
    init: () => {
        console.log(`🚀 Initialisation de Paradis IA V3 - ${CONFIG.version} (${CONFIG.versionName})`);
        
        // Initialiser l'interface utilisateur de base
        UI.init();
        
        // Initialiser les graphiques si disponibles
        if (window.Charts) {
            Charts.init();
        }
        
        // Initialiser les composants
        App.initComponents();
        
        // Vérifier le mode du système
        App.checkSystemMode();
        
        // Initialiser la navigation
        App.initNavigation();
        
        // Initialiser le rafraîchissement automatique
        App.startAutoRefresh();
        
        console.log('✅ Initialisation terminée');
    },
    
    /**
     * Initialise les composants disponibles
     */
    initComponents: () => {
        // Utiliser le nouveau gestionnaire de composants si disponible
        if (window.app && window.app.components) {
            console.log('🔄 Utilisation du nouveau gestionnaire de composants');
            window.app.components.initAll();
            return;
        }
        
        // Compatibilité avec l'ancien système
        console.warn('⚠️ Utilisation du système de composants obsolète');
        if (window.Components) {
            if (Components.Dashboard) {
                Components.Dashboard.init();
            }
            
            if (Components.Agents) {
                Components.Agents.init();
            }
            
            if (Components.Tasks) {
                Components.Tasks.init();
            }
            
            if (Components.Messages) {
                Components.Messages.init();
            }
        }
    },
    
    /**
     * Vérifie le mode du système (FULL ou LIMITED)
     */
    checkSystemMode: async () => {
        try {
            const mode = await API.System.getMode();
            
            // Mettre à jour l'interface en fonction du mode
            UI.updateSystemStatus(mode);
            
            // Afficher une notification si mode limité
            if (mode === 'LIMITED') {
                UI.toast.show('Système en mode limité - Certaines fonctionnalités peuvent être indisponibles', 'warning', {
                    duration: 10000
                });
            }
            
            return mode;
        } catch (error) {
            console.error('Erreur lors de la vérification du mode système:', error);
            UI.updateSystemStatus('OFFLINE');
            
            UI.toast.show('Impossible de communiquer avec le serveur', 'error');
            return 'OFFLINE';
        }
    },
    
    /**
     * Initialise la navigation entre les pages
     */
    initNavigation: () => {
        // Gestionnaire pour les liens de navigation
        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                const page = link.getAttribute('data-page');
                App.navigateTo(page);
                
                // Mettre à jour la classe active
                document.querySelectorAll('.nav-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                link.closest('.nav-item').classList.add('active');
            });
        });
    },
    
    /**
     * Navigue vers une page spécifique
     * @param {string} page - Nom de la page
     */
    navigateTo: (page) => {
        console.log(`🧭 Navigation vers: ${page}`);
        
        // Mettre à jour le titre de la page
        const pageTitle = document.querySelector('.page-title h1');
        if (pageTitle) {
            switch (page) {
                case 'dashboard':
                    pageTitle.textContent = 'Tableau de bord';
                    break;
                case 'agents':
                    pageTitle.textContent = 'Agents IA';
                    break;
                case 'tasks':
                    pageTitle.textContent = 'Tâches';
                    break;
                case 'messages':
                    pageTitle.textContent = 'Messages';
                    break;
                case 'models':
                    pageTitle.textContent = 'Modèles';
                    break;
                case 'monitoring':
                    pageTitle.textContent = 'Monitoring';
                    break;
                case 'logs':
                    pageTitle.textContent = 'Logs';
                    break;
                case 'settings':
                    pageTitle.textContent = 'Paramètres';
                    break;
                default:
                    pageTitle.textContent = 'Paradis IA V3';
            }
        }
        
        // Cacher toutes les pages
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            // Masquer toutes les pages existantes
            document.querySelectorAll('.content > div[class$="-page"]').forEach(pageElement => {
                pageElement.style.display = 'none';
            });
            
            // Afficher la page demandée ou créer une nouvelle page
            const pageClass = `${page}-page`;
            let pageElement = document.querySelector(`.${pageClass}`);
            
            if (pageElement) {
                // Afficher la page si elle existe déjà
                pageElement.style.display = 'block';
            } else if (page === 'dashboard') {
                // La page dashboard est déjà dans le HTML
                const dashboardPage = document.querySelector('.dashboard-page');
                if (dashboardPage) {
                    dashboardPage.style.display = 'block';
                }
            } else {
                // Créer une nouvelle page pour les autres sections
                const newPage = document.createElement('div');
                newPage.className = pageClass;
                newPage.innerHTML = `
                    <div class="page-header">
                        <h2>${pageTitle.textContent}</h2>
                    </div>
                    <div class="card">
                        <div class="card-body">
                            <div class="coming-soon">
                                <i class="fas fa-code"></i>
                                <h3>Page en développement</h3>
                                <p>Cette fonctionnalité sera disponible prochainement.</p>
                            </div>
                        </div>
                    </div>
                `;
                mainContent.appendChild(newPage);
            }
        }
        
        // Fermer le menu mobile si ouvert
        const container = document.querySelector('.app-container');
        if (container && container.classList.contains('mobile-menu-open')) {
            container.classList.remove('mobile-menu-open');
        }
    },
    
    /**
     * Démarre le rafraîchissement automatique des données
     */
    startAutoRefresh: () => {
        // Vérifier le mode système toutes les 30 secondes
        setInterval(() => {
            App.checkSystemMode();
        }, 30000);
    }
};

// Initialiser l'application quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        // Petit délai pour s'assurer que tous les scripts sont chargés
        App.init();
    }, 100);
}); 