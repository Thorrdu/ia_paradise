# 🚀 Paradis IA V2 - Édition Haute Performance 🧠

## Bienvenue dans votre écosystème d'IA local optimisé pour matériel puissant

Ce projet crée un environnement complet d'intelligence artificielle tirant pleinement parti de votre matériel haut de gamme : Windows 11, 32-64 Go de RAM et GeForce RTX 4060. Le "Paradis IA" V2 combine des technologies open-source optimisées pour vous offrir des capacités d'IA de niveau professionnel, 100% gratuites et locales.

## 🖥️ Configuration Matérielle Optimale

Cette version est spécialement optimisée pour :
- **Système d'exploitation** : Windows 11
- **RAM** : 32-64 Go
- **GPU** : NVIDIA GeForce RTX 4060 (8 Go VRAM)
- **Optimisations** : Accélération CUDA, modèles quantifiés pour GPU

## 🌟 Capacités Avancées

Avec votre configuration matérielle haut de gamme, ce Paradis IA offre :

- **🔥 Modèles IA de Grande Taille** - Exécution de modèles puissants comme Mixtral 8x7B et CodeLlama 34B
- **⚡ Accélération GPU Complète** - Performances optimisées via CUDA et cuDNN
- **🧠 Assistants Multi-Agents** - Système d'agents spécialisés pour différentes tâches
- **💼 Développement PHP Professionnel** - Support avancé avec DeepSeek Coder et CodeLlama 34B
- **📈 Monitoring de Performance** - Outils spécifiques pour optimiser l'utilisation des ressources

## 📂 Structure Organisationnelle

Le projet est organisé de manière modulaire pour une meilleure maintenance :

```
Paradis_IA/
├── .env                        # Variables d'environnement
├── README.md                   # Documentation principale
├── collecter_infos_systeme.ps1 # Script diagnostic système
├── lancer_paradis_ia.ps1       # Script de lancement principal
│
├── modeles/                    # Répertoire des modèles IA
│   └── modelfiles/             # Configurations personnalisées de modèles
│
├── agents/                     # Agents IA spécialisés
│   ├── assistant_ia.py         # Agent principal d'automatisation
│   ├── dev_php_agent.py        # Agent spécialisé PHP
│   └── system_agent.py         # Agent de gestion système
│
├── config/                     # Fichiers de configuration
│   ├── ollama_config.json      # Configuration d'Ollama
│   └── tabby_config.json       # Configuration de TabbyML
│
└── scripts/                    # Scripts utilitaires
    ├── setup_environment.ps1   # Installation des prérequis
    ├── gpu_optimization.ps1    # Optimisation pour GPU NVIDIA
    └── test_performance.ps1    # Tests de performance
```

## 🚀 Guide de Démarrage Rapide

1. **Créez la structure de dossiers**
   ```powershell
   mkdir -p Paradis_IA/{modeles/modelfiles,agents,config,scripts}
   cd Paradis_IA
   ```

2. **Installez les prérequis optimisés GPU**
   
   Suivez les instructions détaillées dans `suivi_etapes_paradis_ia_v2.md` pour installer :
   - Python 3.10+ avec support CUDA
   - CUDA Toolkit et cuDNN
   - Ollama configuré pour l'accélération GPU
   - Docker Desktop avec WSL2 et intégration GPU

3. **Lancez l'installation des modèles IA haute performance**
   ```powershell
   # Après installation des prérequis
   ollama pull mixtral
   ollama pull dolphin-mixtral
   ollama pull codellama:34b-instruct-q5_K_M
   ollama pull deepseek-coder:33b-instruct-q5_K_M
   ```

4. **Optimisez votre GPU pour l'IA**
   ```powershell
   .\scripts\gpu_optimization.ps1
   ```

5. **Démarrez le Paradis IA**
   ```powershell
   .\lancer_paradis_ia.ps1
   ```
   Un menu interactif s'affichera avec toutes les options disponibles.

## 🧩 Composants Optimisés pour Hautes Performances

### Modèles IA Conversationnels
- **Mixtral 8x7B Optimisé** - Modèle multilingue de classe mondiale avec configuration GPU optimisée
- **Dolphin Mixtral** - Version optimisée pour suivre des instructions précises

### Modèles de Code et Développement PHP
- **CodeLlama 34B** - Version quantifiée pour GPU offrant une qualité de code exceptionnelle
- **DeepSeek Coder 33B** - Spécialiste de la génération de code PHP avec documentation

### Outils de Développement
- **TabbyML GPU** - Auto-complétion de code en local avec accélération GPU
- **OpenDevin GPU** - Environnement de développement autonome accéléré

### Agents d'Automatisation
- **CrewAI avec accelération** - Agents spécialisés pour l'automatisation des tâches
- **Monitoring Système** - Surveillance des performances GPU/CPU en temps réel

## 🛠️ Optimisations GPU Spécifiques

Cette version inclut des optimisations spécifiques pour votre NVIDIA RTX 4060 :

- Configuration CUDA optimisée pour les modèles IA
- Paramètres personnalisés pour les modèles (taille de contexte, threads, etc.)
- Optimisation des timings GPU pour maximiser les performances
- Monitoring de l'utilisation VRAM et température GPU

## ⚡ Tests de Performance

Pour évaluer les performances des modèles sur votre matériel :

```powershell
.\scripts\test_performance.ps1
```

Ce script testera tous les modèles installés et générera un rapport détaillé de leurs performances sur votre système.

## 📚 Ressources et Documentation

- [Optimisation NVIDIA pour l'IA](https://developer.nvidia.com/deep-learning-performance-training-inference)
- [Guide d'optimisation CUDA pour Windows 11](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html)
- [Documentation Ollama pour GPU](https://github.com/ollama/ollama/blob/main/docs/gpu.md)
- [Documentation CrewAI pour accélération](https://docs.crewai.com/how-to/Using-LLMs/)

## 🔮 Prochaines Améliorations

Votre configuration matérielle permettra d'ajouter ultérieurement :
- Support multimodal texte+image avec LLaVA-NeXT
- Tableau de bord web de monitoring en temps réel
- Fine-tuning local de modèles pour des tâches spécifiques
- Utilisation avancée de Langchain et LangGraph pour des workflows complexes

## 📃 Licence

Ce projet est sous licence MIT. Vous êtes libre de l'utiliser, le modifier et le distribuer.

---

Créé avec ❤️ pour exploiter pleinement votre matériel haut de gamme sans dépendre de services cloud payants. 