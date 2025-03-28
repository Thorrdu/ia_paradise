/**
 * config.js - Configuration globale de l'application Paradis IA V3
 * Centralise tous les paramètres de configuration
 */

const CONFIG = {
    // Informations sur la version
    version: '3.0.0',
    versionName: 'Haute Performance',
    
    // Paramètres de l'UI
    ui: {
        theme: {
            defaultTheme: 'system', // 'light', 'dark', 'system'
            storageKey: 'theme'
        },
        dashboard: {
            refreshInterval: 10000, // ms
            maxLogEntries: 50,
            chartHistory: 30 // points
        },
        animations: {
            enabled: true,
            duration: 300 // ms
        },
        notifications: {
            position: 'top-right',
            duration: 5000, // ms
            maxVisible: 5
        }
    },
    
    // Configuration des graphiques
    charts: {
        colors: {
            cpu: '#4388E5',
            ram: '#43B581',
            gpu: '#9A43E5',
            disk: '#F04747',
            network: '#FAA61A'
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 800,
                easing: 'easeOutQuart'
            },
            elements: {
                line: {
                    tension: 0.4
                },
                point: {
                    radius: 2,
                    hitRadius: 6,
                    hoverRadius: 4
                }
            }
        }
    },
    
    // Configuration des statuts de tâche
    taskStatus: {
        PENDING: {
            label: 'En attente',
            color: 'var(--color-pending)',
            icon: 'clock'
        },
        RUNNING: {
            label: 'En cours',
            color: 'var(--color-running)',
            icon: 'sync-alt'
        },
        COMPLETED: {
            label: 'Terminée',
            color: 'var(--color-completed)',
            icon: 'check-circle'
        },
        FAILED: {
            label: 'Échouée',
            color: 'var(--color-failed)',
            icon: 'times-circle'
        },
        CANCELLED: {
            label: 'Annulée',
            color: 'var(--color-cancelled)',
            icon: 'ban'
        }
    },
    
    // Configuration des priorités de tâche
    taskPriority: {
        LOW: {
            label: 'Basse',
            color: 'var(--color-low)',
            value: 1
        },
        MEDIUM: {
            label: 'Moyenne',
            color: 'var(--color-medium)',
            value: 2
        },
        HIGH: {
            label: 'Haute',
            color: 'var(--color-high)',
            value: 3
        },
        URGENT: {
            label: 'Urgente',
            color: 'var(--color-urgent)',
            value: 4
        }
    },
    
    // Configuration des statuts d'agent
    agentStatus: {
        ACTIVE: {
            label: 'Actif',
            color: 'var(--color-active)',
            icon: 'circle'
        },
        IDLE: {
            label: 'Inactif',
            color: 'var(--color-idle)',
            icon: 'coffee'
        },
        BUSY: {
            label: 'Occupé',
            color: 'var(--color-busy)',
            icon: 'hourglass-half'
        },
        ERROR: {
            label: 'Erreur',
            color: 'var(--color-error)',
            icon: 'exclamation-circle'
        },
        OFFLINE: {
            label: 'Hors ligne',
            color: 'var(--color-offline)',
            icon: 'power-off'
        },
        UNKNOWN: {
            label: 'Inconnu',
            color: 'var(--color-unknown)',
            icon: 'question-circle'
        }
    },
    
    // Configuration des niveaux de log
    logLevels: {
        DEBUG: {
            label: 'Debug',
            color: 'var(--color-debug)',
            icon: 'bug'
        },
        INFO: {
            label: 'Info',
            color: 'var(--color-info)',
            icon: 'info-circle'
        },
        WARNING: {
            label: 'Attention',
            color: 'var(--color-warning)',
            icon: 'exclamation-triangle'
        },
        ERROR: {
            label: 'Erreur',
            color: 'var(--color-error)',
            icon: 'times-circle'
        },
        CRITICAL: {
            label: 'Critique',
            color: 'var(--color-critical)',
            icon: 'skull-crossbones'
        }
    },
    
    // Seuils d'alarme pour le monitoring
    monitoring: {
        thresholds: {
            cpu: {
                warning: 70,
                critical: 90
            },
            ram: {
                warning: 75,
                critical: 90
            },
            gpu: {
                warning: 80,
                critical: 95
            },
            disk: {
                warning: 85,
                critical: 95
            }
        }
    },
    
    // Configuration des modèles par défaut
    defaultModels: {
        chat: 'mixtral',
        code: 'deepseek-coder',
        embedding: 'nomic-embed-text'
    },
    
    // Configuration des API externes
    externalAPIs: {
        ollama: {
            baseUrl: 'http://localhost:11434/api',
            timeout: 60000 // ms
        }
    },
    
    // Paramètres de développement
    dev: {
        debugMode: false,
        mockData: false
    }
};

// Rendre la configuration disponible globalement
window.CONFIG = CONFIG; 