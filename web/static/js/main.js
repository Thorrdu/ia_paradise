/**
 * main.js - Fichier principal pour le chargement des modules JavaScript
 * Chargement des modules en respectant les dépendances
 */

// Ordre de chargement optimal des modules
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Chargement de Paradis IA V3');
    
    // Configuration de base du système
    loadScript('/static/js/config.js', () => {
        console.log('✅ Configuration chargée');
        
        // Modules utilitaires
        loadScript('/static/js/utils/dom.js', () => {
            loadScript('/static/js/utils/format.js', () => {
                loadScript('/static/js/utils/theme.js', () => {
                    console.log('✅ Utilitaires chargés');
                    
                    // Nouveau gestionnaire de composants
                    loadScript('/static/js/components.js', () => {
                        console.log('✅ Gestionnaire de composants chargé');
                        
                        // Interface utilisateur de base
                        loadScript('/static/js/ui.js', () => {
                            // Modules de communication avec l'API
                            loadScript('/static/js/api.js', () => {
                                console.log('✅ API chargée');
                                
                                // Bibliothèque de graphiques (si disponible)
                                loadOptionalScript('/static/js/vendor/chart.min.js', () => {
                                    loadScript('/static/js/charts.js', () => {
                                        
                                        // Composants spécifiques
                                        loadComponentScripts(() => {
                                            
                                            // Application principale (dépend de tous les autres modules)
                                            loadScript('/static/js/app.js', () => {
                                                console.log('✅ Application prête');
                                            });
                                        });
                                    });
                                });
                            });
                        });
                    });
                });
            });
        });
    });
});

/**
 * Charge un script JavaScript de façon asynchrone
 * @param {string} src - Chemin du script
 * @param {Function} callback - Fonction à exécuter après le chargement
 */
function loadScript(src, callback) {
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = src;
    script.onload = callback || (() => console.log(`Script chargé: ${src}`));
    script.onerror = () => console.error(`Erreur de chargement: ${src}`);
    document.head.appendChild(script);
}

/**
 * Charge un script optionnel
 * @param {string} src - Chemin du script
 * @param {Function} callback - Fonction à exécuter après le chargement
 */
function loadOptionalScript(src, callback) {
    fetch(src)
        .then(response => {
            if (!response.ok) {
                console.warn(`Script optionnel non disponible: ${src}`);
                // Continuer même si le script est manquant
                if (callback) callback();
                return;
            }
            
            loadScript(src, callback);
        })
        .catch(() => {
            console.warn(`Script optionnel non disponible: ${src}`);
            if (callback) callback();
        });
}

/**
 * Charge tous les composants de l'application
 * @param {Function} callback - Fonction à exécuter après le chargement
 */
function loadComponentScripts(callback) {
    const components = [
        '/static/js/components/agents.js',
        '/static/js/components/tasks.js',
        '/static/js/components/messages.js',
        '/static/js/components/dashboard.js'
    ];
    
    let loaded = 0;
    
    // Fonction pour vérifier si tous les composants sont chargés
    const checkAllLoaded = () => {
        loaded++;
        if (loaded >= components.length) {
            console.log('✅ Composants chargés');
            if (callback) callback();
        }
    };
    
    // Charger tous les composants en parallèle
    components.forEach(component => {
        // Vérifier d'abord si le composant existe
        fetch(component)
            .then(response => {
                if (!response.ok) {
                    console.warn(`Composant non disponible: ${component}`);
                    checkAllLoaded();
                    return;
                }
                
                loadScript(component, checkAllLoaded);
            })
            .catch(() => {
                console.warn(`Composant non disponible: ${component}`);
                checkAllLoaded();
            });
    });
} 