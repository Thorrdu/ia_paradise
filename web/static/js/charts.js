/**
 * charts.js - Gestionnaire de graphiques pour l'application
 * Initialise et met à jour les graphiques de monitoring
 */

const Charts = {
    /**
     * Collection des instances de graphiques
     */
    instances: {},
    
    /**
     * Historique des données pour chaque graphique
     */
    history: {
        cpu: Array(20).fill(0),
        ram: Array(20).fill(0),
        gpu: Array(20).fill(0)
    },
    
    /**
     * Configuration des graphiques
     */
    config: {
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
                radius: 0
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    display: false
                }
            },
            y: {
                beginAtZero: true,
                max: 100,
                grid: {
                    color: 'rgba(200, 200, 200, 0.1)'
                },
                ticks: {
                    callback: (value) => `${value}%`
                }
            }
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                callbacks: {
                    label: (context) => `${context.dataset.label}: ${context.raw}%`
                }
            }
        }
    },
    
    /**
     * Initialise les graphiques
     */
    init: () => {
        console.log('📊 Initialisation des graphiques');
        
        // Vérifier si Chart.js est disponible
        if (typeof Chart === 'undefined') {
            console.error('Chart.js non disponible, les graphiques ne seront pas affichés');
            return;
        }
        
        // Écouter les changements de thème pour mettre à jour les graphiques
        window.addEventListener('theme:change', Charts.updateThemeColors);
        
        // Initialiser les graphiques si les éléments existent
        Charts.initCpuChart();
        Charts.initRamChart();
        Charts.initGpuChart();
        Charts.initTaskGraphs();
        Charts.initAgentGraphs();
        
        console.log('✅ Graphiques initialisés');
    },
    
    /**
     * Initialise le graphique CPU
     */
    initCpuChart: () => {
        const ctx = document.getElementById('cpu-chart');
        if (!ctx) return;
        
        // Vérifier si Chart.js est disponible
        if (typeof Chart === 'undefined') {
            console.error('Chart.js non disponible, le graphique CPU ne sera pas affiché');
            return;
        }
        
        const labels = Array(20).fill('');
        
        Charts.instances.cpu = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Utilisation CPU',
                    data: Charts.history.cpu,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true
                }]
            },
            options: Charts.config
        });
    },
    
    /**
     * Initialise le graphique RAM
     */
    initRamChart: () => {
        const ctx = document.getElementById('ram-chart');
        if (!ctx) return;
        
        // Vérifier si Chart.js est disponible
        if (typeof Chart === 'undefined') {
            console.error('Chart.js non disponible, le graphique RAM ne sera pas affiché');
            return;
        }
        
        const labels = Array(20).fill('');
        
        Charts.instances.ram = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Utilisation RAM',
                    data: Charts.history.ram,
                    borderColor: 'rgba(153, 102, 255, 1)',
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    fill: true
                }]
            },
            options: Charts.config
        });
    },
    
    /**
     * Initialise le graphique GPU
     */
    initGpuChart: () => {
        const ctx = document.getElementById('gpu-chart');
        if (!ctx) return;
        
        // Vérifier si Chart.js est disponible
        if (typeof Chart === 'undefined') {
            console.error('Chart.js non disponible, le graphique GPU ne sera pas affiché');
            return;
        }
        
        const labels = Array(20).fill('');
        
        Charts.instances.gpu = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Utilisation GPU',
                    data: Charts.history.gpu,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: true
                }]
            },
            options: Charts.config
        });
    },
    
    /**
     * Initialise les graphiques de tâches
     */
    initTaskGraphs: () => {
        // Graphique de distribution des tâches
        const taskDistributionCanvas = document.getElementById('task-distribution-chart');
        if (taskDistributionCanvas) {
            Charts.initChart('task-distribution-chart', {
                type: 'doughnut',
                options: {
                    cutout: '65%',
                    plugins: {
                        legend: {
                            position: 'right'
                        }
                    }
                },
                data: {
                    labels: ['En attente', 'En cours', 'Terminée', 'Échouée', 'Annulée'],
                    datasets: [{
                        data: [0, 0, 0, 0, 0],
                        backgroundColor: [
                            CONFIG.taskStatus.PENDING.color,
                            CONFIG.taskStatus.RUNNING.color,
                            CONFIG.taskStatus.COMPLETED.color,
                            CONFIG.taskStatus.FAILED.color,
                            CONFIG.taskStatus.CANCELLED.color
                        ],
                        borderWidth: 0
                    }]
                }
            });
        }
    },
    
    /**
     * Initialise les graphiques d'agents
     */
    initAgentGraphs: () => {
        // Graphique d'activité des agents
        const agentActivityCanvas = document.getElementById('agent-activity-chart');
        if (agentActivityCanvas) {
            Charts.initChart('agent-activity-chart', {
                type: 'bar',
                options: {
                    indexAxis: 'y',
                    scales: {
                        x: {
                            min: 0,
                            max: 100
                        }
                    }
                },
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Activité (%)',
                        data: [],
                        backgroundColor: Charts.hexToRgba(CONFIG.charts.colors.cpu, 0.7),
                        borderColor: CONFIG.charts.colors.cpu,
                        borderWidth: 1
                    }]
                }
            });
        }
    },
    
    /**
     * Initialise un graphique spécifique
     * @param {string} id - ID du canvas
     * @param {Object} config - Configuration du graphique
     */
    initChart: (id, config) => {
        const canvas = document.getElementById(id);
        if (!canvas) return null;
        
        // Détruire l'instance existante si présente
        if (Charts.instances[id]) {
            Charts.instances[id].destroy();
        }
        
        // Initialiser l'historique des données si nécessaire
        if (!Charts.history[id] && config.type === 'line') {
            Charts.history[id] = {
                timestamp: Date.now(),
                labels: Array(CONFIG.ui.dashboard.chartHistory).fill(''),
                datasets: config.data.datasets.map(dataset => ({
                    label: dataset.label,
                    data: Array(CONFIG.ui.dashboard.chartHistory).fill(0)
                }))
            };
        }
        
        // Créer la nouvelle instance
        Charts.instances[id] = new Chart(canvas, config);
        
        return Charts.instances[id];
    },
    
    /**
     * Met à jour les graphiques avec de nouvelles données
     * @param {Object} data - Données à mettre à jour
     */
    update: (data) => {
        // Vérifier que les données sont valides
        if (!data) return;
        
        // Vérifier si Chart.js est disponible
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js non disponible, impossible de mettre à jour les graphiques');
            return;
        }
        
        // Mettre à jour l'historique CPU
        if (data.cpu && typeof data.cpu.percent === 'number') {
            Charts.history.cpu.push(data.cpu.percent);
            Charts.history.cpu.shift();
            
            if (Charts.instances.cpu) {
                Charts.instances.cpu.data.datasets[0].data = Charts.history.cpu;
                Charts.instances.cpu.update();
            }
        }
        
        // Mettre à jour l'historique RAM
        if (data.memory && typeof data.memory.percent === 'number') {
            Charts.history.ram.push(data.memory.percent);
            Charts.history.ram.shift();
            
            if (Charts.instances.ram) {
                Charts.instances.ram.data.datasets[0].data = Charts.history.ram;
                Charts.instances.ram.update();
            }
        }
        
        // Mettre à jour l'historique GPU
        if (data.gpu && typeof data.gpu.percent === 'number') {
            Charts.history.gpu.push(data.gpu.percent);
            Charts.history.gpu.shift();
            
            if (Charts.instances.gpu) {
                Charts.instances.gpu.data.datasets[0].data = Charts.history.gpu;
                Charts.instances.gpu.update();
            }
        }
    },
    
    /**
     * Met à jour tous les graphiques de performance système
     * @param {Object} stats - Statistiques système
     */
    updateSystemCharts: (stats) => {
        if (!stats) return;
        
        // Mettre à jour le graphique CPU
        if (Charts.instances['cpu-chart']) {
            Charts.updateLineChart('cpu-chart', stats.cpu.usage);
        }
        
        // Mettre à jour le graphique RAM
        if (Charts.instances['ram-chart']) {
            Charts.updateLineChart('ram-chart', stats.memory.percent);
        }
        
        // Mettre à jour le graphique GPU
        if (Charts.instances['gpu-chart'] && stats.gpu && stats.gpu.usage !== undefined) {
            Charts.updateLineChart('gpu-chart', stats.gpu.usage);
        }
        
        // Mettre à jour les valeurs dans les cartes
        document.getElementById('cpu-value').textContent = Math.round(stats.cpu.usage);
        document.getElementById('ram-value').textContent = Math.round(stats.memory.percent);
        document.getElementById('gpu-value').textContent = stats.gpu ? Math.round(stats.gpu.usage) : 'N/A';
        
        // Mettre à jour les barres de progression
        document.getElementById('cpu-bar').style.width = `${stats.cpu.usage}%`;
        document.getElementById('ram-bar').style.width = `${stats.memory.percent}%`;
        if (stats.gpu) {
            document.getElementById('gpu-bar').style.width = `${stats.gpu.usage}%`;
        }
    },
    
    /**
     * Met à jour les couleurs des graphiques en fonction du thème
     */
    updateThemeColors: () => {
        // Mettre à jour la couleur du texte
        Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary');
        
        // Mettre à jour chaque graphique
        Object.values(Charts.instances).forEach(chart => {
            chart.update();
        });
    },
    
    /**
     * Convertit une couleur hexadécimale en RGBA
     * @param {string} hex - Couleur hexadécimale
     * @param {number} alpha - Transparence (0-1)
     * @return {string} Couleur RGBA
     */
    hexToRgba: (hex, alpha = 1) => {
        // Enlever le # si présent
        hex = hex.replace('#', '');
        
        // Convertir en RGB
        const r = parseInt(hex.slice(0, 2), 16);
        const g = parseInt(hex.slice(2, 4), 16);
        const b = parseInt(hex.slice(4, 6), 16);
        
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
};

// Rendre les graphiques disponibles globalement
window.Charts = Charts; 