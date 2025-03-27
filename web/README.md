# Interface Web Paradis IA

Cette interface web permet de gérer et d'interagir avec les agents du système Paradis IA.

## Fonctionnalités

- Tableau de bord avec statistiques du système
- Gestion des agents (visualisation, envoi de messages)
- Gestion des tâches (création, modification du statut)
- Messagerie entre agents
- Consultation des journaux (logs)

## Prérequis

- Python 3.8 ou supérieur
- Flask
- CairoSVG (pour la génération du logo)
- Autres dépendances du projet Paradis IA

## Installation

1. Assurez-vous que toutes les dépendances sont installées :

```bash
pip install flask cairosvg psutil
```

2. Assurez-vous que les répertoires nécessaires existent :

```bash
mkdir -p web/logs web/data web/static web/templates
```

## Démarrage

Vous pouvez démarrer l'interface web de deux façons :

### Option 1 : Script de démarrage

Utilisez le script de démarrage à la racine du projet :

```bash
python start_web_interface.py
```

### Option 2 : Démarrage manuel

Lancez directement le serveur Flask :

```bash
cd web
python app.py
```

L'interface sera accessible à l'adresse : http://localhost:5000

## Structure des fichiers

- `app.py` : Serveur web Flask principal
- `static/` : Fichiers statiques (CSS, JavaScript, images)
  - `app.js` : Logique JavaScript de l'interface
  - `styles.css` : Styles CSS
  - `logo.svg` : Logo vectoriel
  - `logo.png` : Logo au format PNG
- `templates/` : Templates HTML
  - `index.html` : Page principale de l'interface
- `logs/` : Journaux du serveur web
- `data/` : Données persistantes

## Utilisation

### Tableau de bord

Le tableau de bord affiche une vue d'ensemble du système :
- Nombre d'agents actifs
- Nombre de tâches en cours
- Nombre de messages échangés
- Activités récentes

### Agents

Cette section permet de visualiser tous les agents enregistrés dans le système, avec leurs capacités et actions disponibles.

### Tâches

Vous pouvez créer, visualiser et gérer les tâches assignées aux agents. Les actions disponibles sont :
- Marquer comme terminée (✓)
- Mettre en pause (⏸)
- Marquer comme échouée (✗)

### Messagerie

Cette section permet d'envoyer des messages aux agents. Vous pouvez spécifier :
- L'agent destinataire
- Le contenu du message
- La priorité du message

### Logs

Visualisez les journaux du système avec possibilité de filtrage par niveau de gravité.

## Dépannage

### Le serveur ne démarre pas

Vérifiez que :
- Les dépendances sont correctement installées
- Les répertoires nécessaires existent
- Les modules du projet Paradis IA sont accessibles

### Les agents n'apparaissent pas

Vérifiez que :
- Le gestionnaire de communication est correctement initialisé
- Les agents sont enregistrés auprès du gestionnaire de communication

### Problèmes d'affichage du logo

Si le logo ne s'affiche pas correctement :
1. Installez manuellement CairoSVG : `pip install cairosvg`
2. Exécutez le script de conversion : `python web/static/convert_logo.py`

## Développement

Pour étendre l'interface web, vous pouvez :
- Ajouter de nouvelles routes API dans `app.py`
- Étendre les fonctionnalités JavaScript dans `app.js`
- Ajouter de nouveaux composants d'interface dans `index.html`
- Modifier les styles dans `styles.css`

## License

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails. 