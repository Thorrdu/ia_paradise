/**
 * utils/format.js - Utilitaires pour le formatage des données
 */

const FormatUtils = {
    /**
     * Formate une date relative (temps écoulé)
     * @param {string|Date} date - Date à formater
     * @return {string} Texte formaté (ex: "il y a 5 minutes")
     */
    timeAgo: (date) => {
        if (!date) return '';
        
        const now = new Date();
        const dateObj = typeof date === 'string' ? new Date(date) : date;
        
        if (isNaN(dateObj.getTime())) return '';
        
        const seconds = Math.floor((now - dateObj) / 1000);
        
        // Moins d'une minute
        if (seconds < 60) {
            return 'à l\'instant';
        }
        
        // Minutes
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) {
            return `il y a ${minutes} minute${minutes > 1 ? 's' : ''}`;
        }
        
        // Heures
        const hours = Math.floor(minutes / 60);
        if (hours < 24) {
            return `il y a ${hours} heure${hours > 1 ? 's' : ''}`;
        }
        
        // Jours
        const days = Math.floor(hours / 24);
        if (days < 30) {
            return `il y a ${days} jour${days > 1 ? 's' : ''}`;
        }
        
        // Mois
        const months = Math.floor(days / 30);
        if (months < 12) {
            return `il y a ${months} mois`;
        }
        
        // Années
        const years = Math.floor(months / 12);
        return `il y a ${years} an${years > 1 ? 's' : ''}`;
    },
    
    /**
     * Formate une date en format local
     * @param {string|Date} date - Date à formater
     * @param {Object} options - Options de formatage
     * @return {string} Date formatée
     */
    dateTime: (date, options = {}) => {
        if (!date) return '';
        
        const dateObj = typeof date === 'string' ? new Date(date) : date;
        if (isNaN(dateObj.getTime())) return '';
        
        const defaultOptions = {
            dateStyle: 'medium',
            timeStyle: 'short'
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        
        return new Intl.DateTimeFormat('fr-FR', mergedOptions).format(dateObj);
    },
    
    /**
     * Formate un nombre avec séparateurs de milliers
     * @param {number} num - Nombre à formater
     * @param {number} decimals - Nombre de décimales (défaut: 0)
     * @return {string} Nombre formaté
     */
    number: (num, decimals = 0) => {
        if (num === null || num === undefined) return '';
        
        return new Intl.NumberFormat('fr-FR', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(num);
    },
    
    /**
     * Formate un montant en devise
     * @param {number} amount - Montant à formater
     * @param {string} currency - Code de devise (défaut: EUR)
     * @return {string} Montant formaté
     */
    currency: (amount, currency = 'EUR') => {
        if (amount === null || amount === undefined) return '';
        
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },
    
    /**
     * Formate une taille de fichier en unités lisibles
     * @param {number} bytes - Taille en octets
     * @param {number} decimals - Nombre de décimales (défaut: 2)
     * @return {string} Taille formatée (ex: "1.5 MB")
     */
    fileSize: (bytes, decimals = 2) => {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(decimals)) + ' ' + sizes[i];
    },
    
    /**
     * Tronque un texte et ajoute des points de suspension
     * @param {string} text - Texte à tronquer
     * @param {number} maxLength - Longueur maximale
     * @return {string} Texte tronqué
     */
    truncate: (text, maxLength = 100) => {
        if (!text) return '';
        
        if (text.length <= maxLength) return text;
        
        return text.substring(0, maxLength) + '...';
    },
    
    /**
     * Convertit un texte en slug (URL friendly)
     * @param {string} text - Texte à convertir
     * @return {string} Slug généré
     */
    slug: (text) => {
        if (!text) return '';
        
        return text
            .toString()
            .normalize('NFD')                   // Normaliser les accents
            .replace(/[\u0300-\u036f]/g, '')    // Supprimer les diacritiques
            .toLowerCase()
            .trim()
            .replace(/\s+/g, '-')               // Espaces en tirets
            .replace(/[^\w\-]+/g, '')           // Supprimer les caractères non alphanumériques
            .replace(/\-\-+/g, '-');            // Supprimer les tirets multiples
    },
    
    /**
     * Convertit un text en format initial majuscule
     * @param {string} text - Texte à convertir
     * @return {string} Texte avec initiale majuscule
     */
    capitalize: (text) => {
        if (!text) return '';
        
        return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
    },
    
    /**
     * Formate un pourcentage
     * @param {number} value - Valeur à formater (0-1 ou 0-100)
     * @param {boolean} from100 - Si true, considère que value est déjà sur 100
     * @param {number} decimals - Nombre de décimales (défaut: 1)
     * @return {string} Pourcentage formaté
     */
    percent: (value, from100 = false, decimals = 1) => {
        if (value === null || value === undefined) return '';
        
        // Convertir en pourcentage si nécessaire
        const percentage = from100 ? value : value * 100;
        
        return new Intl.NumberFormat('fr-FR', {
            style: 'percent',
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(percentage / 100);
    },
    
    /**
     * Formate un temps en durée lisible
     * @param {number} seconds - Durée en secondes
     * @return {string} Durée formatée (ex: "1h 30m")
     */
    duration: (seconds) => {
        if (!seconds) return '0s';
        
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        let result = '';
        
        if (hours > 0) {
            result += `${hours}h `;
        }
        
        if (minutes > 0 || hours > 0) {
            result += `${minutes}m `;
        }
        
        if (secs > 0 && hours === 0) {
            result += `${secs}s`;
        }
        
        return result.trim();
    },
    
    /**
     * Formate un temps au format ISO en temps lisible
     * @param {string} isoTime - Temps au format ISO8601
     * @return {string} Temps formaté (ex: "1:30:45")
     */
    time: (isoTime) => {
        if (!isoTime) return '';
        
        const date = new Date(`2000-01-01T${isoTime}Z`);
        if (isNaN(date.getTime())) return '';
        
        const hours = date.getUTCHours();
        const minutes = date.getUTCMinutes();
        const seconds = date.getUTCSeconds();
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
    },
    
    /**
     * Formate une date en chaîne lisible
     * @param {Date|string|number} date - Date à formater
     * @param {Object} options - Options de formatage
     * @return {string} Date formatée
     */
    formatDate: (date, options = {}) => {
        if (!date) return '';
        
        // Convertir en objet Date si nécessaire
        const dateObj = date instanceof Date ? date : new Date(date);
        
        // Vérifier si la date est valide
        if (isNaN(dateObj.getTime())) return 'Date invalide';
        
        // Options par défaut
        const defaultOptions = {
            format: 'full', // 'full', 'date', 'time', 'relative'
            locale: 'fr-FR'
        };
        
        const opts = { ...defaultOptions, ...options };
        
        // Format relatif (il y a X minutes, etc.)
        if (opts.format === 'relative') {
            return FormatUtils.timeAgo(dateObj);
        }
        
        // Autres formats
        const formatOptions = {};
        
        switch (opts.format) {
            case 'full':
                formatOptions.dateStyle = 'medium';
                formatOptions.timeStyle = 'short';
                break;
            case 'date':
                formatOptions.dateStyle = 'medium';
                break;
            case 'time':
                formatOptions.timeStyle = 'short';
                break;
            case 'short':
                formatOptions.dateStyle = 'short';
                break;
            case 'long':
                formatOptions.dateStyle = 'long';
                formatOptions.timeStyle = 'medium';
                break;
            default:
                // Format personnalisé (non implémenté ici)
                break;
        }
        
        return new Intl.DateTimeFormat(opts.locale, formatOptions).format(dateObj);
    },
    
    /**
     * Formate un nombre avec séparateurs de milliers et décimales
     * @param {number} number - Nombre à formater
     * @param {Object} options - Options de formatage
     * @return {string} Nombre formaté
     */
    formatNumber: (number, options = {}) => {
        if (number === null || number === undefined || isNaN(number)) return '';
        
        // Options par défaut
        const defaultOptions = {
            decimals: 2,
            decimalSeparator: ',',
            thousandsSeparator: ' ',
            compact: false,
            locale: 'fr-FR'
        };
        
        const opts = { ...defaultOptions, ...options };
        
        // Utiliser l'API Intl pour le formatage
        if (opts.compact) {
            return new Intl.NumberFormat(opts.locale, {
                notation: 'compact',
                maximumFractionDigits: opts.decimals
            }).format(number);
        }
        
        return new Intl.NumberFormat(opts.locale, {
            minimumFractionDigits: opts.decimals,
            maximumFractionDigits: opts.decimals
        }).format(number);
    },
    
    /**
     * Formate une taille de fichier en Ko, Mo, Go, etc.
     * @param {number} bytes - Taille en octets
     * @param {Object} options - Options de formatage
     * @return {string} Taille formatée
     */
    formatFileSize: (bytes, options = {}) => {
        if (bytes === null || bytes === undefined || isNaN(bytes)) return '';
        
        // Options par défaut
        const defaultOptions = {
            decimals: 2,
            binary: false, // true: KiB (1024), false: KB (1000)
            locale: 'fr-FR'
        };
        
        const opts = { ...defaultOptions, ...options };
        
        const units = opts.binary
            ? ['octets', 'Kio', 'Mio', 'Gio', 'Tio', 'Pio']
            : ['octets', 'Ko', 'Mo', 'Go', 'To', 'Po'];
        
        const base = opts.binary ? 1024 : 1000;
        
        if (bytes === 0) return `0 ${units[0]}`;
        
        const exponent = Math.min(
            Math.floor(Math.log(bytes) / Math.log(base)),
            units.length - 1
        );
        
        const value = bytes / Math.pow(base, exponent);
        const formattedValue = FormatUtils.formatNumber(value, {
            decimals: exponent === 0 ? 0 : opts.decimals,
            locale: opts.locale
        });
        
        return `${formattedValue} ${units[exponent]}`;
    },
    
    /**
     * Convertit une durée (en ms/secondes) en format lisible (1h 30m, etc.)
     * @param {number} time - Durée en millisecondes ou secondes
     * @param {Object} options - Options de formatage
     * @return {string} Durée formatée
     */
    formatDuration: (time, options = {}) => {
        if (time === null || time === undefined || isNaN(time)) return '';
        
        // Options par défaut
        const defaultOptions = {
            format: 'short', // 'short', 'long', 'colons'
            isSeconds: false, // true si l'entrée est en secondes
            showZero: false // afficher les valeurs nulles
        };
        
        const opts = { ...defaultOptions, ...options };
        
        // Convertir en millisecondes si l'entrée est en secondes
        let ms = opts.isSeconds ? time * 1000 : time;
        
        // Calculer les différentes parties
        const seconds = Math.floor((ms / 1000) % 60);
        const minutes = Math.floor((ms / (1000 * 60)) % 60);
        const hours = Math.floor((ms / (1000 * 60 * 60)) % 24);
        const days = Math.floor(ms / (1000 * 60 * 60 * 24));
        
        // Format avec deux-points (00:00:00)
        if (opts.format === 'colons') {
            const parts = [];
            
            if (days > 0 || opts.showZero) {
                parts.push(days.toString().padStart(2, '0'));
            }
            
            if (hours > 0 || days > 0 || opts.showZero) {
                parts.push(hours.toString().padStart(2, '0'));
            }
            
            parts.push(minutes.toString().padStart(2, '0'));
            parts.push(seconds.toString().padStart(2, '0'));
            
            return parts.join(':');
        }
        
        // Format long ou court
        const labels = opts.format === 'long'
            ? { d: ' jours ', h: ' heures ', m: ' minutes ', s: ' secondes ' }
            : { d: 'j ', h: 'h ', m: 'm ', s: 's ' };
        
        const result = [];
        
        if (days > 0 || opts.showZero) {
            result.push(`${days}${labels.d}`);
        }
        
        if (hours > 0 || days > 0 || opts.showZero) {
            result.push(`${hours}${labels.h}`);
        }
        
        if (minutes > 0 || hours > 0 || days > 0 || opts.showZero) {
            result.push(`${minutes}${labels.m}`);
        }
        
        result.push(`${seconds}${labels.s}`);
        
        return result.join('');
    },
    
    /**
     * Formate un pourcentage
     * @param {number} value - Valeur à formater (0-1 ou 0-100)
     * @param {Object} options - Options de formatage
     * @return {string} Pourcentage formaté
     */
    formatPercent: (value, options = {}) => {
        if (value === null || value === undefined || isNaN(value)) return '';
        
        // Options par défaut
        const defaultOptions = {
            decimals: 1,
            multiply: true, // true si la valeur est entre 0-1 et doit être multipliée par 100
            suffix: '%',
            locale: 'fr-FR'
        };
        
        const opts = { ...defaultOptions, ...options };
        
        // Convertir 0-1 en 0-100 si nécessaire
        let percentage = value;
        if (opts.multiply && value >= 0 && value <= 1) {
            percentage = value * 100;
        }
        
        const formattedValue = FormatUtils.formatNumber(percentage, {
            decimals: opts.decimals,
            locale: opts.locale
        });
        
        return `${formattedValue}${opts.suffix}`;
    },
    
    /**
     * Formate une valeur monétaire
     * @param {number} value - Valeur à formater
     * @param {Object} options - Options de formatage
     * @return {string} Valeur monétaire formatée
     */
    formatCurrency: (value, options = {}) => {
        if (value === null || value === undefined || isNaN(value)) return '';
        
        // Options par défaut
        const defaultOptions = {
            currency: 'EUR',
            locale: 'fr-FR'
        };
        
        const opts = { ...defaultOptions, ...options };
        
        return new Intl.NumberFormat(opts.locale, {
            style: 'currency',
            currency: opts.currency
        }).format(value);
    },
    
    /**
     * Tronque un texte à une longueur donnée et ajoute des points de suspension
     * @param {string} text - Texte à tronquer
     * @param {number} length - Longueur maximale
     * @param {string} suffix - Suffixe à ajouter si tronqué
     * @return {string} Texte tronqué
     */
    truncate: (text, length = 100, suffix = '...') => {
        if (!text || typeof text !== 'string') return '';
        
        if (text.length <= length) return text;
        
        return text.substring(0, length).trim() + suffix;
    },
    
    /**
     * Convertit une chaîne en slug (pour les URLs)
     * @param {string} str - Chaîne à convertir
     * @return {string} Slug
     */
    slugify: (str) => {
        if (!str || typeof str !== 'string') return '';
        
        // Convertir en minuscules et remplacer les caractères accentués
        return str
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '');
    }
};

// Exporter l'utilitaire
if (typeof window.Utils === 'undefined') {
    window.Utils = {};
}

window.Utils.format = FormatUtils; 