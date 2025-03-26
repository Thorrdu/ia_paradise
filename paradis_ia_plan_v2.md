# 🚀 Plan d'Action V2 : Paradis IA Haute Performance

Ce document contient les étapes optimisées pour installer un écosystème d'intelligence artificielle 100% gratuit et local sur un ordinateur puissant : **Windows 11 avec 32-64 Go de RAM et une GeForce RTX 4060**.

## 📋 Aperçu des Capacités Avancées

Avec cette configuration matérielle haut de gamme, notre Paradis IA pourra :
- Exécuter plusieurs modèles IA de grande taille simultanément
- Exploiter l'accélération GPU pour des performances optimales
- Gérer des projets de développement web/PHP complexes
- Assurer une réponse rapide et fluide des agents IA

## 🔧 Configuration Matérielle Optimale Détectée
- **Système d'exploitation** : Windows 11
- **RAM** : 32-64 Go
- **GPU** : NVIDIA GeForce RTX 4060 (8 Go VRAM)
- **Optimisations possibles** : Accélération CUDA, modèles quantifiés pour GPU

## 📁 Structure Organisationnelle du Projet

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

## 🔍 Étape 0 : Collecte et Analyse du Système

Cette étape est déjà résolue car nous connaissons la configuration : Windows 11, 32-64 Go RAM, RTX 4060.

## 🛠️ Étape 1 : Installation des Prérequis Optimisés

### Python avec Support GPU
```powershell
# Installation Python 3.10+ (version optimale pour compatibilité CUDA)
Start-Process "https://www.python.org/downloads/windows/"

# Vérification
python --version
pip --version

# Installation des packages optimisés GPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install tensorflow-gpu
```

### Ollama avec Support CUDA
```powershell
# Télécharger et installer Ollama
Start-Process "https://ollama.com/download/windows"

# Vérifier l'installation
ollama --version

# Configurer pour utilisation GPU
$ollamaConfigPath = "$env:USERPROFILE\.ollama\config.json"
$ollamaConfig = @{
    "gpu" = $true
    "cuda" = $true
}
$ollamaConfig | ConvertTo-Json | Out-File -FilePath $ollamaConfigPath
```

### LM Studio (Configuration GPU)
```powershell
# Télécharger et installer LM Studio
Start-Process "https://lmstudio.ai/"

# Après installation, configurer pour utilisation GPU dans l'interface
```

### Docker avec Support WSL2 et GPU
```powershell
# Activer WSL2
wsl --install

# Installer Docker Desktop
Start-Process "https://www.docker.com/products/docker-desktop/"

# Après installation, activer l'intégration GPU dans les paramètres de Docker Desktop
```

### CUDA Toolkit et cuDNN
```powershell
# Installer CUDA Toolkit pour optimiser les performances IA
Start-Process "https://developer.nvidia.com/cuda-downloads"

# Installer cuDNN pour accélérer les réseaux de neurones
Start-Process "https://developer.nvidia.com/cudnn"
```

## 🤖 Étape 2 : Mise en Place des IA pour le Contrôle de l'Ordinateur

### CrewAI (Optimisé pour Hautes Performances)
```powershell
# Créer un environnement virtuel Python
python -m venv crew_env
.\crew_env\Scripts\Activate

# Installer CrewAI avec dépendances GPU
pip install crewai langchain
pip install transformers accelerate bitsandbytes
```

### Installation des Modèles IA Haut de Gamme
```powershell
# Installer Mixtral 8x7B (modèle de classe mondiale)
ollama pull mixtral

# Installer Dolphin Mixtral (instructions suivies optimisées)
ollama pull dolphin-mixtral

# Installer CodeLlama 34B (modèle de code haute qualité)
ollama pull codellama:34b-instruct-q5_K_M

# Vérifier l'accélération GPU
ollama run dolphin-mixtral "Vérifie si tu utilises bien l'accélération GPU. Réponds uniquement par Oui ou Non."
```

### Script d'Automatisation Avancé

Créer le fichier `agents/assistant_ia.py` :
```python
from crewai import Agent, Task, Crew, Process
from langchain.tools import BaseTool
from langchain.llms import Ollama
import subprocess
import os
import json
import psutil
import torch

# Configuration de l'agent avec accélération GPU
ollama_llm = Ollama(
    model="mixtral",
    temperature=0.1,
    num_gpu=1,  # Utiliser le GPU
    num_thread=8  # Utiliser 8 threads CPU
)

# Outil pour exécuter des commandes système
class CommandTool(BaseTool):
    name = "command_tool"
    description = "Exécute des commandes système"
    
    def _run(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def _arun(self, command):
        return self._run(command)

# Outil pour gérer les fichiers
class FileTool(BaseTool):
    name = "file_tool"
    description = "Gère les fichiers (lecture, écriture, liste)"
    
    def _run(self, action, path, content=None):
        try:
            if action == "list":
                files = os.listdir(path)
                return '\n'.join(files)
            elif action == "read":
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif action == "write":
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"Fichier {path} écrit avec succès"
            else:
                return f"Action {action} non reconnue"
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def _arun(self, action, path, content=None):
        return self._run(action, path, content)

# Outil pour surveiller les ressources système
class SystemMonitorTool(BaseTool):
    name = "system_monitor_tool"
    description = "Surveille les ressources système (CPU, RAM, GPU)"
    
    def _run(self, query_type="all"):
        try:
            if query_type == "cpu" or query_type == "all":
                cpu_usage = psutil.cpu_percent(interval=1)
                cpu_info = {"usage": cpu_usage, "cores": psutil.cpu_count()}
                
            if query_type == "ram" or query_type == "all":
                ram = psutil.virtual_memory()
                ram_info = {
                    "total": f"{ram.total / (1024**3):.2f} GB",
                    "available": f"{ram.available / (1024**3):.2f} GB",
                    "percent": ram.percent
                }
                
            if query_type == "gpu" or query_type == "all":
                if torch.cuda.is_available():
                    gpu_info = {
                        "name": torch.cuda.get_device_name(0),
                        "available": True,
                        "memory_allocated": f"{torch.cuda.memory_allocated(0) / (1024**3):.2f} GB",
                        "memory_reserved": f"{torch.cuda.memory_reserved(0) / (1024**3):.2f} GB"
                    }
                else:
                    gpu_info = {"available": False}
            
            result = {}
            if query_type == "cpu" or query_type == "all":
                result["cpu"] = cpu_info
            if query_type == "ram" or query_type == "all":
                result["ram"] = ram_info
            if query_type == "gpu" or query_type == "all":
                result["gpu"] = gpu_info
                
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def _arun(self, query_type="all"):
        return self._run(query_type)

# Création de l'agent assistant système
assistant = Agent(
    role="Assistant Système Avancé",
    goal="Aider à gérer l'ordinateur et automatiser des tâches complexes",
    backstory="Je suis un assistant IA puissant conçu pour l'automatisation et la gestion des tâches système sur un ordinateur haute performance.",
    verbose=True,
    tools=[CommandTool(), FileTool(), SystemMonitorTool()],
    llm=ollama_llm
)

# Exemple de tâche : analyser les performances du système
task = Task(
    description="Analyser les performances actuelles du système et générer un rapport",
    expected_output="Rapport de performance du système",
    agent=assistant
)

# Création de l'équipe (Crew)
crew = Crew(
    agents=[assistant],
    tasks=[task],
    verbose=2,
    process=Process.sequential  # Exécution séquentielle des tâches
)

# Exécution de l'équipe
result = crew.kickoff()
print(result)
```

## 💻 Étape 3 : Installation des IA pour le Développement (Optimisées)

### Modèles de Code Haute Performance
```powershell
# Code Llama 34B (version haute performance)
ollama pull codellama:34b-instruct-q5_K_M

# DeepSeek Coder (spécialisé PHP et modèle de premier ordre)
ollama pull deepseek-coder:33b-instruct-q5_K_M

# Tester les modèles de code
ollama run codellama:34b-instruct-q5_K_M "Génère une classe PHP complète pour un gestionnaire de bases de données avec PDO"
```

### TabbyML avec Accélération GPU
```powershell
# Installer TabbyML
curl -fsSL https://get.tabbyml.com/install.sh | bash

# Lancer TabbyML avec modèle haut de gamme et accélération GPU
tabby serve --model TabbyML/DeepseekCoder-33B-instruct-q5_K_M --device cuda

# Installer l'extension TabbyML pour VS Code ou PHPStorm
```

### OpenDevin avec configuration avancée
```powershell
# Cloner le dépôt
git clone https://github.com/OpenDevin/OpenDevin.git
cd OpenDevin

# Configurer OpenDevin pour utilisation GPU
$env:OPENDEVIN_GPU_ACCELERATION = "true"
$env:OPENDEVIN_MODEL = "codellama:34b-instruct-q5_K_M"

# Démarrer avec Docker et accélération GPU
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up
```

## 🔧 Étape 4 : Configuration Avancée pour GPU RTX 4060

### Optimisation des Modèles pour le GPU
```powershell
# Créer un dossier pour les Modelfiles personnalisés
mkdir -p modeles/modelfiles

# Créer un Modelfile optimisé pour Mixtral avec configuration GPU
@"
FROM mixtral
PARAMETER num_ctx 16384
PARAMETER num_gpu 1
PARAMETER num_thread 8
PARAMETER temperature 0.7
PARAMETER stop "<|im_end|>"
PARAMETER stop "</answer>"
"@ | Out-File -FilePath "modeles/modelfiles/mixtral-optimized"

# Créer et exécuter le modèle optimisé
ollama create mixtral-optimized -f modeles/modelfiles/mixtral-optimized
```

### Optimisation du GPU avec CUDA
```powershell
# Créer le script pour optimisation GPU
@"
Write-Host "🚀 Optimisation GPU RTX 4060 pour IA" -ForegroundColor Cyan

# Vérifier la présence de CUDA
if (-not (Test-Path "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA")) {
    Write-Host "❌ CUDA non détecté. Installez CUDA Toolkit depuis:" -ForegroundColor Red
    Write-Host "https://developer.nvidia.com/cuda-downloads" -ForegroundColor Yellow
    Exit
}

# Optimiser le Shader Cache pour DirectX
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "DisableShaderCache" -Value 0 -Type DWord

# Activer le Game Mode pour optimiser les performances
Set-ItemProperty -Path "HKCU:\Software\Microsoft\GameBar" -Name "AllowAutoGameMode" -Value 1 -Type DWord
Set-ItemProperty -Path "HKCU:\Software\Microsoft\GameBar" -Name "AutoGameModeEnabled" -Value 1 -Type DWord

# Configurer NVIDIA pour performances maximales
nvidia-smi -pm 1
nvidia-smi --auto-boost-default=0
nvidia-smi -ac 3004,1708

Write-Host "✅ Optimisation GPU terminée!" -ForegroundColor Green
"@ | Out-File -FilePath "scripts/gpu_optimization.ps1"
```

## 🔄 Étape 5 : Configuration Multi-Agents Avancée

### Script de Lancement avec Menu Étendu

Créer le fichier `lancer_paradis_ia.ps1` :
```powershell
# Script de lancement du Paradis IA - Version haute performance
Write-Host "🚀 Lancement du Paradis IA - Configuration haute performance" -ForegroundColor Cyan

# Fonction pour vérifier si un processus est en cours d'exécution
function Is-ProcessRunning {
    param ($processName)
    return (Get-Process | Where-Object { $_.ProcessName -eq $processName }) -ne $null
}

# Vérifier et lancer Ollama si nécessaire
if (-not (Is-ProcessRunning "ollama")) {
    Write-Host "📦 Démarrage d'Ollama (mode GPU)..." -ForegroundColor Yellow
    Start-Process "ollama" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# Activation de l'environnement virtuel CrewAI
Write-Host "🤖 Activation de l'environnement CrewAI..." -ForegroundColor Yellow
.\crew_env\Scripts\Activate

# Fonction pour afficher la disponibilité GPU
function Show-GPUStatus {
    Write-Host "`n===== 🖥️ STATUT GPU NVIDIA =====`n" -ForegroundColor Cyan
    try {
        $gpuInfo = nvidia-smi --query-gpu=name,memory.used,memory.total,temperature.gpu --format=csv,noheader
        Write-Host $gpuInfo -ForegroundColor Green
    } catch {
        Write-Host "Impossible d'obtenir les informations GPU" -ForegroundColor Red
    }
    Write-Host ""
}

# Menu interactif avancé
function Show-Menu {
    Write-Host "`n=== 🤖 PARADIS IA - MENU PRINCIPAL (HAUTE PERFORMANCE) 🤖 ===" -ForegroundColor Cyan
    
    Show-GPUStatus
    
    Write-Host "=== 💬 ASSISTANTS CONVERSATIONNELS ===" -ForegroundColor Magenta
    Write-Host "1. 🧠 Mixtral 8x7B (Modèle haut de gamme)" -ForegroundColor Green
    Write-Host "2. 🐬 Dolphin Mixtral (Instructions optimisées)" -ForegroundColor Green
    
    Write-Host "`n=== 💻 ASSISTANTS DÉVELOPPEMENT ===" -ForegroundColor Magenta
    Write-Host "3. 👨‍💻 Code Llama 34B (Code haute qualité)" -ForegroundColor Green
    Write-Host "4. 🔍 DeepSeek Coder 33B (Spécialiste PHP)" -ForegroundColor Green
    Write-Host "5. 📋 TabbyML GPU (Auto-complétion)" -ForegroundColor Green
    Write-Host "6. 🚀 OpenDevin (Développement autonome)" -ForegroundColor Green
    
    Write-Host "`n=== 🛠️ AGENTS & OUTILS ===" -ForegroundColor Magenta
    Write-Host "7. 🔧 Assistant IA (Agent système)" -ForegroundColor Green
    Write-Host "8. 📊 Rapport de performances" -ForegroundColor Green
    Write-Host "9. ⚙️ Optimisation GPU" -ForegroundColor Green
    
    Write-Host "`n10. ❌ Quitter" -ForegroundColor Red
    Write-Host "==================================" -ForegroundColor Cyan
}

# Boucle principale
do {
    Show-Menu
    $choice = Read-Host "Choisissez une option (1-10)"
    
    switch ($choice) {
        "1" { ollama run mixtral-optimized }
        "2" { ollama run dolphin-mixtral }
        "3" { ollama run codellama:34b-instruct-q5_K_M }
        "4" { ollama run deepseek-coder:33b-instruct-q5_K_M }
        "5" { 
            Write-Host "Lancement de TabbyML avec accélération GPU..." -ForegroundColor Yellow
            tabby serve --model TabbyML/DeepseekCoder-33B-instruct-q5_K_M --device cuda 
        }
        "6" { 
            Set-Location OpenDevin
            $env:OPENDEVIN_GPU_ACCELERATION = "true"
            docker compose -f docker-compose.yml -f docker-compose.gpu.yml up
            Set-Location ..
        }
        "7" { 
            Write-Host "Lancement de l'Assistant IA..." -ForegroundColor Yellow
            python agents/assistant_ia.py 
        }
        "8" { 
            Write-Host "Génération du rapport de performances..." -ForegroundColor Yellow
            python scripts/test_performance.ps1
        }
        "9" { 
            Write-Host "Optimisation du GPU..." -ForegroundColor Yellow
            .\scripts\gpu_optimization.ps1 
        }
        "10" { 
            Write-Host "👋 Fermeture du Paradis IA..." -ForegroundColor Cyan
            break 
        }
        default { Write-Host "❌ Option invalide, veuillez réessayer." -ForegroundColor Red }
    }
} while ($choice -ne "10")

# Désactivation de l'environnement virtuel
deactivate
```

## 📊 Étape 6 : Tests de Performance et Optimisation

### Script de Test de Performance

Créer le fichier `scripts/test_performance.ps1` :
```powershell
# Script de test de performance du Paradis IA
Write-Host "📊 Test de performance des modèles IA" -ForegroundColor Cyan

$outputFile = "rapport_performance.txt"

# Tester chaque modèle avec un prompt standard
$testPrompt = "Explique le concept de programmation orientée objet en PHP en 5 phrases concises."

# Fonction pour tester un modèle
function Test-Model {
    param($modelName, $modelParam)
    
    Write-Host "Test du modèle $modelName..." -ForegroundColor Yellow
    
    # Mesurer le temps de démarrage
    $startTime = Get-Date
    $result = ollama run $modelParam -q "$testPrompt"
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    # Écrire les résultats
    "=== Test de $modelName ===" | Out-File -FilePath $outputFile -Append
    "Temps de réponse: $duration secondes" | Out-File -FilePath $outputFile -Append
    "Réponse: $result" | Out-File -FilePath $outputFile -Append
    "`n" | Out-File -FilePath $outputFile -Append
    
    return @{
        Model = $modelName
        Duration = $duration
        ResponseLength = $result.Length
    }
}

# Préparer le fichier de sortie
"RAPPORT DE PERFORMANCE DES MODÈLES IA" | Out-File -FilePath $outputFile
"Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath $outputFile -Append
"Système: Windows 11, RTX 4060, $(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB GB RAM" | Out-File -FilePath $outputFile -Append
"`n" | Out-File -FilePath $outputFile -Append

# Tester tous les modèles
$results = @()
$results += Test-Model -modelName "Mixtral 8x7B" -modelParam "mixtral-optimized"
$results += Test-Model -modelName "Dolphin Mixtral" -modelParam "dolphin-mixtral"
$results += Test-Model -modelName "CodeLlama 34B" -modelParam "codellama:34b-instruct-q5_K_M"
$results += Test-Model -modelName "DeepSeek Coder" -modelParam "deepseek-coder:33b-instruct-q5_K_M"

# Générer un résumé
"=== RÉSUMÉ DES PERFORMANCES ===" | Out-File -FilePath $outputFile -Append
$results | Sort-Object Duration | ForEach-Object {
    "$($_.Model): $($_.Duration) secondes, $($_.ResponseLength) caractères" | Out-File -FilePath $outputFile -Append
}

Write-Host "✅ Rapport de performance généré dans $outputFile" -ForegroundColor Green
```

## 🏁 Étape 7 : Premier Lancement et Tests de Validation

```powershell
# Exécution du script d'optimisation GPU
.\scripts\gpu_optimization.ps1

# Lancement du Paradis IA
.\lancer_paradis_ia.ps1
```

## 📚 Ressources et Documentation

- [Optimisation NVIDIA pour l'IA](https://developer.nvidia.com/deep-learning-performance-training-inference)
- [Guide d'optimisation CUDA pour Windows 11](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html)
- [Documentation Ollama pour GPU](https://github.com/ollama/ollama/blob/main/docs/gpu.md)
- [Documentation CrewAI pour accélération](https://docs.crewai.com/how-to/Using-LLMs/)

## ⚠️ Résolution des Problèmes Courants

### CUDA Out of Memory
Si vous rencontrez cette erreur, essayez de diminuer la taille du contexte ou d'utiliser un modèle quantifié plus léger :
```powershell
# Utiliser un modèle mieux quantifié
ollama pull codellama:34b-instruct-q6_K
```

### Performances GPU sous-optimales
Assurez-vous que les pilotes NVIDIA sont à jour et que votre système n'exécute pas d'autres processus gourmands en GPU.

## 🔮 Prochaines Améliorations Possibles

- Intégration de modèles multimodaux (texte + image) comme LLaVA-NeXT
- Création d'un tableau de bord web pour le monitoring des performances
- Fine-tuning des modèles pour des tâches spécifiques en PHP/développement
- Intégration avec des API externes via LangGraph 