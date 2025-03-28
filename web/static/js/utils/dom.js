/**
 * dom.js - Utilitaires pour la manipulation du DOM
 * Fournit des fonctions réutilisables pour faciliter l'interaction avec le DOM
 */

const DOMUtils = {
    /**
     * Sélectionne un élément dans le DOM
     * @param {string} selector - Sélecteur CSS
     * @param {HTMLElement} parent - Élément parent (document par défaut)
     * @return {HTMLElement|null} Élément trouvé ou null
     */
    select: (selector, parent = document) => parent.querySelector(selector),
    
    /**
     * Sélectionne plusieurs éléments dans le DOM
     * @param {string} selector - Sélecteur CSS
     * @param {HTMLElement} parent - Élément parent (document par défaut)
     * @return {NodeList} Liste des éléments trouvés
     */
    selectAll: (selector, parent = document) => parent.querySelectorAll(selector),
    
    /**
     * Crée un élément avec des attributs et contenu optionnels
     * @param {string} tag - Type d'élément à créer
     * @param {Object} attributes - Attributs à ajouter à l'élément
     * @param {string|HTMLElement|Array} content - Contenu à ajouter (texte, élément ou tableau d'éléments)
     * @return {HTMLElement} L'élément créé
     */
    create: (tag, attributes = {}, content = null) => {
        const element = document.createElement(tag);
        
        // Ajouter les attributs
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'className') {
                element.className = value;
            } else if (key === 'dataset') {
                Object.entries(value).forEach(([dataKey, dataValue]) => {
                    element.dataset[dataKey] = dataValue;
                });
            } else if (key === 'style' && typeof value === 'object') {
                Object.entries(value).forEach(([styleKey, styleValue]) => {
                    element.style[styleKey] = styleValue;
                });
            } else if (key.startsWith('on') && typeof value === 'function') {
                const eventName = key.substring(2).toLowerCase();
                element.addEventListener(eventName, value);
            } else {
                element.setAttribute(key, value);
            }
        });
        
        // Ajouter le contenu
        if (content !== null) {
            if (Array.isArray(content)) {
                content.forEach(item => {
                    DOMUtils.append(element, item);
                });
            } else {
                DOMUtils.append(element, content);
            }
        }
        
        return element;
    },
    
    /**
     * Ajoute du contenu à un élément
     * @param {HTMLElement} parent - Élément parent
     * @param {string|HTMLElement} content - Contenu à ajouter
     */
    append: (parent, content) => {
        if (typeof content === 'string') {
            parent.appendChild(document.createTextNode(content));
        } else if (content instanceof HTMLElement) {
            parent.appendChild(content);
        }
    },
    
    /**
     * Vide le contenu d'un élément
     * @param {HTMLElement} element - Élément à vider
     */
    empty: (element) => {
        while (element.firstChild) {
            element.removeChild(element.firstChild);
        }
    },
    
    /**
     * Affiche ou masque un élément
     * @param {HTMLElement} element - Élément à afficher/masquer
     * @param {boolean} show - Afficher (true) ou masquer (false)
     * @param {string} displayValue - Valeur CSS display quand afficher (par défaut: block)
     */
    toggle: (element, show, displayValue = 'block') => {
        if (!element) return;
        element.style.display = show ? displayValue : 'none';
    },
    
    /**
     * Ajoute ou supprime des classes CSS
     * @param {HTMLElement} element - Élément cible
     * @param {Object} classMap - Mapping classe -> condition (ajoute si true, supprime si false)
     */
    updateClasses: (element, classMap) => {
        if (!element) return;
        Object.entries(classMap).forEach(([className, condition]) => {
            if (condition) {
                element.classList.add(className);
            } else {
                element.classList.remove(className);
            }
        });
    },
    
    /**
     * Anime un élément avec des transitions CSS
     * @param {HTMLElement} element - Élément à animer
     * @param {Object} properties - Propriétés CSS à animer
     * @param {Object} options - Options d'animation (durée, timing, etc)
     * @return {Promise} Promise résolue à la fin de l'animation
     */
    animate: (element, properties, options = {}) => {
        if (!element) return Promise.reject(new Error('Élément non trouvé'));
        
        const duration = options.duration || 300;
        const timingFunction = options.timingFunction || 'ease';
        const delay = options.delay || 0;
        
        // Configurer la transition
        element.style.transition = Object.keys(properties)
            .map(prop => `${prop} ${duration}ms ${timingFunction} ${delay}ms`)
            .join(', ');
        
        // Appliquer les nouvelles valeurs
        Object.entries(properties).forEach(([prop, value]) => {
            element.style[prop] = value;
        });
        
        // Retourner une promise résolue à la fin de l'animation
        return new Promise(resolve => {
            const transitionEnd = () => {
                element.removeEventListener('transitionend', transitionEnd);
                resolve(element);
            };
            
            element.addEventListener('transitionend', transitionEnd);
            
            // Fallback si l'événement transitionend ne se déclenche pas
            setTimeout(transitionEnd, duration + delay + 50);
        });
    },
    
    /**
     * Crée facilement un fragment de document
     * @param {Array} elements - Éléments à ajouter au fragment
     * @return {DocumentFragment} Fragment créé
     */
    createFragment: (elements = []) => {
        const fragment = document.createDocumentFragment();
        elements.forEach(element => {
            if (element instanceof HTMLElement) {
                fragment.appendChild(element);
            }
        });
        return fragment;
    },
    
    /**
     * Définit facilement plusieurs styles sur un élément
     * @param {HTMLElement} element - Élément cible
     * @param {Object} styles - Styles à appliquer
     */
    setStyles: (element, styles) => {
        if (!element) return;
        Object.entries(styles).forEach(([property, value]) => {
            element.style[property] = value;
        });
    },
    
    /**
     * Récupère la position d'un élément par rapport à la fenêtre
     * @param {HTMLElement} element - Élément cible
     * @return {Object} Position {top, left, right, bottom, width, height}
     */
    getPosition: (element) => {
        if (!element) return null;
        const rect = element.getBoundingClientRect();
        return {
            top: rect.top,
            left: rect.left,
            right: rect.right,
            bottom: rect.bottom,
            width: rect.width,
            height: rect.height
        };
    },
    
    /**
     * Détecte si un élément est visible dans le viewport
     * @param {HTMLElement} element - Élément à vérifier
     * @param {number} threshold - Pourcentage de visibilité requis (0-1)
     * @return {boolean} Vrai si l'élément est visible
     */
    isInViewport: (element, threshold = 0) => {
        if (!element) return false;
        
        const rect = element.getBoundingClientRect();
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        const windowWidth = window.innerWidth || document.documentElement.clientWidth;
        
        // Calculer la surface visible
        const visibleHeight = Math.min(rect.bottom, windowHeight) - Math.max(rect.top, 0);
        const visibleWidth = Math.min(rect.right, windowWidth) - Math.max(rect.left, 0);
        const visibleArea = visibleHeight * visibleWidth;
        const elementArea = rect.width * rect.height;
        
        // Vérifier si l'élément est suffisamment visible
        return visibleArea >= elementArea * threshold;
    },
    
    /**
     * Crée un loader dans un conteneur
     * @param {HTMLElement|string} container - Conteneur ou sélecteur du conteneur
     * @param {string} message - Message à afficher (optionnel)
     */
    createLoader: (container, message = 'Chargement...') => {
        const containerEl = typeof container === 'string' ? document.querySelector(container) : container;
        if (!containerEl) return;
        
        containerEl.innerHTML = `
            <div class="loader-container">
                <div class="loader-spinner"></div>
                <p class="loader-message">${message}</p>
            </div>
        `;
    },
    
    /**
     * Affiche un message d'erreur dans un conteneur
     * @param {HTMLElement|string} container - Conteneur ou sélecteur du conteneur
     * @param {string} message - Message d'erreur
     */
    showError: (container, message = 'Une erreur est survenue') => {
        const containerEl = typeof container === 'string' ? document.querySelector(container) : container;
        if (!containerEl) return;
        
        containerEl.innerHTML = `
            <div class="error-container">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <p class="error-message">${message}</p>
            </div>
        `;
    },
    
    /**
     * Affiche un message d'état vide dans un conteneur
     * @param {HTMLElement|string} container - Conteneur ou sélecteur du conteneur
     * @param {string} message - Message à afficher
     */
    showEmpty: (container, message = 'Aucun résultat disponible') => {
        const containerEl = typeof container === 'string' ? document.querySelector(container) : container;
        if (!containerEl) return;
        
        containerEl.innerHTML = `
            <div class="empty-container">
                <div class="empty-icon">
                    <i class="fas fa-inbox"></i>
                </div>
                <p class="empty-message">${message}</p>
            </div>
        `;
    },
    
    /**
     * Remplace un élément HTML par un autre
     * @param {HTMLElement|string} target - Élément à remplacer ou son sélecteur
     * @param {HTMLElement|string} newContent - Nouvel élément ou HTML à insérer
     * @return {HTMLElement} Le nouvel élément inséré
     */
    replace: (target, newContent) => {
        const targetEl = typeof target === 'string' ? document.querySelector(target) : target;
        if (!targetEl) return null;
        
        const fragment = document.createDocumentFragment();
        
        if (typeof newContent === 'string') {
            const temp = document.createElement('div');
            temp.innerHTML = newContent;
            while (temp.firstChild) {
                fragment.appendChild(temp.firstChild);
            }
        } else {
            fragment.appendChild(newContent);
        }
        
        targetEl.parentNode.replaceChild(fragment, targetEl);
        return fragment.firstChild;
    },
    
    /**
     * Remplace uniquement le contenu d'un élément
     * @param {HTMLElement|string} container - Conteneur ou sélecteur du conteneur
     * @param {HTMLElement|string} content - Contenu à insérer
     */
    setContent: (container, content) => {
        const containerEl = typeof container === 'string' ? document.querySelector(container) : container;
        if (!containerEl) return;
        
        if (typeof content === 'string') {
            containerEl.innerHTML = content;
        } else {
            containerEl.innerHTML = '';
            containerEl.appendChild(content);
        }
    },
    
    /**
     * Crée une table à partir d'un tableau de données
     * @param {Array} data - Tableau d'objets à afficher
     * @param {Array} columns - Colonnes à afficher [{ key, label, render }]
     * @param {Object} options - Options de configuration
     * @return {HTMLElement} L'élément table créé
     */
    createTable: (data, columns, options = {}) => {
        const table = document.createElement('table');
        table.className = options.tableClass || 'data-table';
        
        // Créer l'en-tête
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        columns.forEach(column => {
            const th = document.createElement('th');
            th.innerHTML = column.label || column.key;
            if (column.headerClass) th.className = column.headerClass;
            headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Créer le corps
        const tbody = document.createElement('tbody');
        
        data.forEach(item => {
            const row = document.createElement('tr');
            
            if (options.onRowClick) {
                row.addEventListener('click', () => options.onRowClick(item));
                row.style.cursor = 'pointer';
            }
            
            columns.forEach(column => {
                const cell = document.createElement('td');
                
                if (column.render) {
                    // Utiliser la fonction de rendu personnalisée
                    cell.innerHTML = column.render(item[column.key], item);
                } else {
                    // Afficher la valeur brute
                    cell.textContent = item[column.key] || '';
                }
                
                if (column.cellClass) cell.className = column.cellClass;
                row.appendChild(cell);
            });
            
            tbody.appendChild(row);
        });
        
        table.appendChild(tbody);
        
        return table;
    },
    
    /**
     * Crée un élément de pagination
     * @param {Object} options - Options de configuration
     * @param {number} options.currentPage - Page actuelle
     * @param {number} options.totalPages - Nombre total de pages
     * @param {Function} options.onPageChange - Fonction appelée lors du changement de page
     * @return {HTMLElement} L'élément de pagination
     */
    createPagination: (options) => {
        const { currentPage, totalPages, onPageChange } = options;
        
        const pagination = document.createElement('div');
        pagination.className = 'pagination';
        
        // Bouton précédent
        const prevBtn = document.createElement('button');
        prevBtn.className = 'pagination-btn prev';
        prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
        prevBtn.disabled = currentPage <= 1;
        prevBtn.addEventListener('click', () => {
            if (currentPage > 1) onPageChange(currentPage - 1);
        });
        
        // Bouton suivant
        const nextBtn = document.createElement('button');
        nextBtn.className = 'pagination-btn next';
        nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
        nextBtn.disabled = currentPage >= totalPages;
        nextBtn.addEventListener('click', () => {
            if (currentPage < totalPages) onPageChange(currentPage + 1);
        });
        
        // Pages
        const pagesList = document.createElement('div');
        pagesList.className = 'pagination-pages';
        
        // Logique pour afficher un nombre limité de pages
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, startPage + 4);
        
        if (endPage - startPage < 4) {
            startPage = Math.max(1, endPage - 4);
        }
        
        // Page 1
        if (startPage > 1) {
            const firstPage = document.createElement('button');
            firstPage.className = 'pagination-btn page';
            firstPage.textContent = '1';
            firstPage.addEventListener('click', () => onPageChange(1));
            pagesList.appendChild(firstPage);
            
            if (startPage > 2) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'pagination-ellipsis';
                ellipsis.textContent = '...';
                pagesList.appendChild(ellipsis);
            }
        }
        
        // Pages centrales
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `pagination-btn page ${i === currentPage ? 'active' : ''}`;
            pageBtn.textContent = i;
            pageBtn.addEventListener('click', () => onPageChange(i));
            pagesList.appendChild(pageBtn);
        }
        
        // Dernière page
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'pagination-ellipsis';
                ellipsis.textContent = '...';
                pagesList.appendChild(ellipsis);
            }
            
            const lastPage = document.createElement('button');
            lastPage.className = 'pagination-btn page';
            lastPage.textContent = totalPages;
            lastPage.addEventListener('click', () => onPageChange(totalPages));
            pagesList.appendChild(lastPage);
        }
        
        pagination.appendChild(prevBtn);
        pagination.appendChild(pagesList);
        pagination.appendChild(nextBtn);
        
        return pagination;
    }
};

// Exporter les utilitaires DOM
window.Utils = window.Utils || {};
window.Utils.dom = DOMUtils; 