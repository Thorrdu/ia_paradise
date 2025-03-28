/**
 * theme.js - Gestionnaire de thème pour l'application
 * Gère les thèmes clair/sombre et les préférences utilisateur
 */

const ThemeUtils = {
    /**
     * Initialise le système de thème
     */
    init: () => {
        // Récupérer le thème sauvegardé ou utiliser le thème système
        const savedTheme = localStorage.getItem(CONFIG.ui.theme.storageKey);
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Thème par défaut
        let currentTheme = CONFIG.ui.theme.defaultTheme;
        
        // Utiliser le thème sauvegardé s'il existe
        if (savedTheme) {
            currentTheme = savedTheme;
        } else if (currentTheme === 'system') {
            // Si le thème par défaut est 'system', utiliser les préférences du navigateur
            currentTheme = prefersDark ? 'dark' : 'light';
        }
        
        // Appliquer le thème
        ThemeUtils.setTheme(currentTheme);
        
        // Ajouter un écouteur pour détecter les changements de préférences système
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
            // Ne mettre à jour que si le thème est en mode système
            if (ThemeUtils.getCurrentMode() === 'system') {
                ThemeUtils.setTheme(event.matches ? 'dark' : 'light', false);
            }
        });
        
        // Ajouter des écouteurs pour les boutons de changement de thème
        document.querySelectorAll('[data-theme-toggle]').forEach(button => {
            button.addEventListener('click', ThemeUtils.toggleTheme);
            
            // Mettre à jour l'icône du bouton
            ThemeUtils.updateThemeToggleButton(button, currentTheme);
        });
        
        console.log(`🎨 Thème initialisé: ${currentTheme}`);
    },
    
    /**
     * Définit le thème de l'application
     * @param {string} theme - Thème à appliquer ('light', 'dark', 'system')
     * @param {boolean} save - Sauvegarder la préférence
     */
    setTheme: (theme, save = true) => {
        const root = document.documentElement;
        const oldTheme = ThemeUtils.getCurrentTheme();
        
        // Si le thème est 'system', utiliser les préférences du navigateur
        let actualTheme = theme;
        if (theme === 'system') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            actualTheme = prefersDark ? 'dark' : 'light';
        }
        
        // Mettre à jour l'attribut data-theme sur l'élément html
        root.setAttribute('data-theme', actualTheme);
        
        // Mettre à jour les meta tags pour le thème des navigateurs mobiles
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute(
                'content',
                actualTheme === 'dark' ? '#1a1a1a' : '#ffffff'
            );
        }
        
        // Sauvegarder la préférence si demandé
        if (save) {
            localStorage.setItem(CONFIG.ui.theme.storageKey, theme);
        }
        
        // Mode système
        if (theme === 'system') {
            root.setAttribute('data-theme-mode', 'system');
        } else {
            root.removeAttribute('data-theme-mode');
        }
        
        // Mettre à jour les boutons de changement de thème
        document.querySelectorAll('[data-theme-toggle]').forEach(button => {
            ThemeUtils.updateThemeToggleButton(button, theme);
        });
        
        // Déclencher un événement personnalisé
        window.dispatchEvent(
            new CustomEvent('theme:change', {
                detail: { oldTheme, newTheme: theme, actualTheme }
            })
        );
    },
    
    /**
     * Récupère le thème actuel
     * @return {string} Thème actuel ('light' ou 'dark')
     */
    getCurrentTheme: () => {
        return document.documentElement.getAttribute('data-theme') || 'light';
    },
    
    /**
     * Récupère le mode actuel
     * @return {string} Mode actuel ('light', 'dark' ou 'system')
     */
    getCurrentMode: () => {
        const savedTheme = localStorage.getItem(CONFIG.ui.theme.storageKey);
        if (document.documentElement.hasAttribute('data-theme-mode')) {
            return 'system';
        }
        return savedTheme || CONFIG.ui.theme.defaultTheme;
    },
    
    /**
     * Bascule entre les thèmes clair et sombre
     */
    toggleTheme: () => {
        const currentMode = ThemeUtils.getCurrentMode();
        
        // Rotation des thèmes: light -> dark -> system -> light
        let newTheme;
        switch (currentMode) {
            case 'light':
                newTheme = 'dark';
                break;
            case 'dark':
                newTheme = 'system';
                break;
            case 'system':
            default:
                newTheme = 'light';
                break;
        }
        
        ThemeUtils.setTheme(newTheme);
    },
    
    /**
     * Met à jour l'apparence du bouton de changement de thème
     * @param {HTMLElement} button - Bouton à mettre à jour
     * @param {string} theme - Thème actuel
     */
    updateThemeToggleButton: (button, theme) => {
        if (!button) return;
        
        // Supprimer toutes les classes d'icône
        const icon = button.querySelector('i');
        if (!icon) return;
        
        // Mettre à jour l'icône en fonction du thème
        icon.className = '';
        switch (theme) {
            case 'light':
                icon.className = 'fas fa-moon';
                button.setAttribute('title', 'Passer au thème sombre');
                break;
            case 'dark':
                icon.className = 'fas fa-sun';
                button.setAttribute('title', 'Passer au thème système');
                break;
            case 'system':
                icon.className = 'fas fa-desktop';
                button.setAttribute('title', 'Passer au thème clair');
                break;
        }
    },
    
    /**
     * Détecte si le système d'exploitation est en mode sombre
     * @return {boolean} Vrai si le système est en mode sombre
     */
    isSystemDarkMode: () => {
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    },
    
    /**
     * Vérifie si le thème actuel est sombre
     * @return {boolean} Vrai si le thème actuel est sombre
     */
    isDarkTheme: () => {
        return ThemeUtils.getCurrentTheme() === 'dark';
    },
    
    /**
     * Applique des couleurs CSS dynamiques
     * @param {string} selector - Sélecteur CSS de l'élément à modifier
     * @param {string} property - Propriété CSS à modifier
     * @param {string} lightValue - Valeur pour le thème clair
     * @param {string} darkValue - Valeur pour le thème sombre
     */
    applyThemeColor: (selector, property, lightValue, darkValue) => {
        const elements = document.querySelectorAll(selector);
        if (!elements.length) return;
        
        const isDark = ThemeUtils.isDarkTheme();
        elements.forEach(element => {
            element.style[property] = isDark ? darkValue : lightValue;
        });
    }
};

// Exporter les utilitaires de thème
window.Utils = window.Utils || {};
window.Utils.theme = ThemeUtils; 