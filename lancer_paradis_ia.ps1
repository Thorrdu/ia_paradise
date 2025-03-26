# Script de lancement du Paradis IA - Version haute performance
Write-Host "🚀 Lancement du Paradis IA - Configuration haute performance" -ForegroundColor Cyan

# Fonction pour vérifier si un processus est en cours d'exécution
function Is-ProcessRunning {
    param ($processName)
    return (Get-Process | Where-Object { $_.ProcessName -eq $processName }) -ne $null
}

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

# Vérifier et lancer Ollama si nécessaire
function Start-OllamaIfNeeded {
    if (-not (Is-ProcessRunning "ollama")) {
        Write-Host "📦 Démarrage d'Ollama (mode GPU)..." -ForegroundColor Yellow
        Start-Process "ollama" -WindowStyle Hidden
        Start-Sleep -Seconds 3
    }
}

# Menu interactif avancé
function Show-Menu {
    Write-Host "`n=== 🤖 PARADIS IA - MENU PRINCIPAL (HAUTE PERFORMANCE) 🤖 ===" -ForegroundColor Cyan
    
    Show-GPUStatus
    
    Write-Host "=== 🛠️ INSTALLATION ET CONFIGURATION ===" -ForegroundColor Magenta
    Write-Host "1. 🔧 Installer les prérequis (Python, Ollama, CUDA, etc.)" -ForegroundColor Green
    Write-Host "2. 📦 Installer/Gérer les modèles IA" -ForegroundColor Green
    Write-Host "3. ⚙️ Optimiser le GPU" -ForegroundColor Green
    
    Write-Host "`n=== 💬 ASSISTANTS CONVERSATIONNELS ===" -ForegroundColor Magenta
    Write-Host "4. 🧠 Mixtral 8x7B (Modèle haut de gamme)" -ForegroundColor Green
    Write-Host "5. 🐬 Dolphin Mixtral (Instructions optimisées)" -ForegroundColor Green
    Write-Host "6. 🤖 Phi-3 Mini (Léger et rapide)" -ForegroundColor Green
    
    Write-Host "`n=== 💻 ASSISTANTS DÉVELOPPEMENT ===" -ForegroundColor Magenta
    Write-Host "7. 👨‍💻 Code Llama 34B (Code haute qualité)" -ForegroundColor Green
    Write-Host "8. 🔍 DeepSeek Coder 33B (Spécialiste PHP)" -ForegroundColor Green
    Write-Host "9. 📋 TabbyML GPU (Auto-complétion)" -ForegroundColor Green
    
    Write-Host "`n=== 🛠️ AGENTS & OUTILS ===" -ForegroundColor Magenta
    Write-Host "10. 🔧 Assistant IA (Agent système)" -ForegroundColor Green
    Write-Host "11. 📊 Rapport de performances" -ForegroundColor Green
    
    Write-Host "`n12. ❌ Quitter" -ForegroundColor Red
    Write-Host "==================================" -ForegroundColor Cyan
}

# Boucle principale
do {
    Show-Menu
    $choice = Read-Host "Choisissez une option (1-12)"
    
    switch ($choice) {
        "1" { 
            Write-Host "Lancement de l'installation des prérequis..." -ForegroundColor Yellow
            & .\scripts\setup_environment.ps1
        }
        "2" { 
            Write-Host "Lancement du gestionnaire de modèles IA..." -ForegroundColor Yellow
            & .\scripts\installer_modeles.ps1
        }
        "3" { 
            Write-Host "Optimisation du GPU..." -ForegroundColor Yellow
            & .\scripts\gpu_optimization.ps1 
        }
        "4" { 
            Start-OllamaIfNeeded
            Write-Host "Lancement de Mixtral 8x7B..." -ForegroundColor Yellow
            ollama run mixtral-optimized 
        }
        "5" { 
            Start-OllamaIfNeeded
            Write-Host "Lancement de Dolphin Mixtral..." -ForegroundColor Yellow
            ollama run dolphin-mixtral 
        }
        "6" { 
            Start-OllamaIfNeeded
            Write-Host "Lancement de Phi-3 Mini..." -ForegroundColor Yellow
            ollama run phi3:mini 
        }
        "7" { 
            Start-OllamaIfNeeded
            Write-Host "Lancement de Code Llama 34B..." -ForegroundColor Yellow
            ollama run codellama:34b-instruct-q5_K_M 
        }
        "8" { 
            Start-OllamaIfNeeded
            Write-Host "Lancement de DeepSeek Coder..." -ForegroundColor Yellow
            ollama run deepseek-coder:33b-instruct-q5_K_M 
        }
        "9" { 
            Write-Host "Lancement de TabbyML avec accélération GPU..." -ForegroundColor Yellow
            tabby serve --model TabbyML/DeepseekCoder-33B-instruct-q5_K_M --device cuda 
        }
        "10" { 
            Write-Host "Lancement de l'Assistant IA..." -ForegroundColor Yellow
            python agents/assistant_ia.py 
        }
        "11" { 
            Write-Host "Génération du rapport de performances..." -ForegroundColor Yellow
            & .\scripts\test_performance.ps1
        }
        "12" { 
            Write-Host "👋 Fermeture du Paradis IA..." -ForegroundColor Cyan
            break 
        }
        default { Write-Host "❌ Option invalide, veuillez réessayer." -ForegroundColor Red }
    }
} while ($choice -ne "12") 