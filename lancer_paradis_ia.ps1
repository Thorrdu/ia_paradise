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
    
    Write-Host "`n=== 🤝 MODE COLLABORATION ===" -ForegroundColor Magenta
    Write-Host "7. 🔄 Mode Collaboration IA" -ForegroundColor Green
    
    Write-Host "`n=== 🛠️ AGENTS & OUTILS ===" -ForegroundColor Magenta
    Write-Host "8. 🔧 Assistant IA (Agent système)" -ForegroundColor Green
    Write-Host "9. 📊 Rapport de performances" -ForegroundColor Green
    Write-Host "10. ⚙️ Optimisation GPU" -ForegroundColor Green
    
    Write-Host "`n11. ❌ Quitter" -ForegroundColor Red
    Write-Host "==================================" -ForegroundColor Cyan
}

# Boucle principale
do {
    Show-Menu
    $choice = Read-Host "Choisissez une option (1-11)"
    
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
            Write-Host "`n=== 🤝 MODE COLLABORATION IA ===" -ForegroundColor Cyan
            Write-Host "Ce mode permet aux agents IA de collaborer pour résoudre des tâches complexes."
            Write-Host "Exemple: Créer un fichier PHP, analyser un site web, etc."
            $task = Read-Host "`nEntrez la tâche à accomplir"
            if ($task) {
                Write-Host "`nLancement du mode collaboration..." -ForegroundColor Yellow
                python agents/assistant_ia.py --mode collaboration --task $task
            }
        }
        "8" { 
            Write-Host "Lancement de l'Assistant IA..." -ForegroundColor Yellow
            python agents/assistant_ia.py --mode system
        }
        "9" { 
            Write-Host "Génération du rapport de performances..." -ForegroundColor Yellow
            python scripts/test_performance.ps1
        }
        "10" { 
            Write-Host "Optimisation du GPU..." -ForegroundColor Yellow
            .\scripts\gpu_optimization.ps1 
        }
        "11" { 
            Write-Host "👋 Fermeture du Paradis IA..." -ForegroundColor Cyan
            break 
        }
        default { Write-Host "❌ Option invalide, veuillez réessayer." -ForegroundColor Red }
    }
} while ($choice -ne "11")

# Désactivation de l'environnement virtuel
deactivate