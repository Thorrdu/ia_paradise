# Script de lancement du Paradis IA - Version haute performance
Write-Host "ðŸš€ Lancement du Paradis IA - Configuration haute performance" -ForegroundColor Cyan

# Fonction pour vÃ©rifier si un processus est en cours d'exÃ©cution
function Is-ProcessRunning {
    param ($processName)
    $process = Get-Process | Where-Object { $_.ProcessName -eq $processName }
    return $null -ne $process
}

# Fonction pour vÃ©rifier si Docker est installÃ©
function Test-DockerInstallation {
    try {
        $dockerVersion = docker --version
        return $true
    } catch {
        return $false
    }
}

# Fonction pour vÃ©rifier si un dossier existe
function Test-DirectoryExists {
    param ($path)
    return Test-Path -Path $path
}

# Fonction pour dÃ©marrer Ollama si nÃ©cessaire
function Start-OllamaIfNeeded {
    if (-not (Is-ProcessRunning "ollama")) {
        Write-Host "ðŸ“¦ DÃ©marrage d'Ollama (mode GPU)..." -ForegroundColor Yellow
        Start-Process "ollama" -WindowStyle Hidden
        Start-Sleep -Seconds 3
    }
}

# Fonction pour afficher la disponibilitÃ© GPU
function Show-GPUStatus {
    Write-Host "`n===== ðŸ–¥ï¸ STATUT GPU NVIDIA =====`n" -ForegroundColor Cyan
    try {
        $gpuInfo = nvidia-smi --query-gpu=name,memory.used,memory.total,temperature.gpu --format=csv,noheader
        Write-Host $gpuInfo -ForegroundColor Green
    } catch {
        Write-Host "Impossible d'obtenir les informations GPU" -ForegroundColor Red
    }
    Write-Host ""
}

# Menu interactif avancÃ©
function Show-Menu {
    Write-Host "`n=== ðŸ¤– PARADIS IA - MENU PRINCIPAL (HAUTE PERFORMANCE) ðŸ¤– ===" -ForegroundColor Cyan
    
    Show-GPUStatus
    
    Write-Host "=== ðŸ’¬ ASSISTANTS CONVERSATIONNELS ===" -ForegroundColor Magenta
    Write-Host "1. ðŸ§  Mixtral 8x7B (ModÃ¨le haut de gamme)" -ForegroundColor Green
    Write-Host "2. ðŸ¬ Dolphin Mixtral (Instructions optimisÃ©es)" -ForegroundColor Green
    
    Write-Host "`n=== ðŸ’» ASSISTANTS DÃ‰VELOPPEMENT ===" -ForegroundColor Magenta
    Write-Host "3. ðŸ‘¨â€ðŸ’» Code Llama 34B (Code haute qualitÃ©)" -ForegroundColor Green
    Write-Host "4. ðŸ” DeepSeek Coder 33B (SpÃ©cialiste PHP)" -ForegroundColor Green
    Write-Host "5. ðŸ“‹ TabbyML GPU (Auto-complÃ©tion)" -ForegroundColor Green
    Write-Host "6. ðŸš€ OpenDevin (DÃ©veloppement autonome)" -ForegroundColor Green
    
    Write-Host "`n=== ðŸ¤ MODE COLLABORATION ===" -ForegroundColor Magenta
    Write-Host "7. ðŸ”„ Mode Collaboration IA" -ForegroundColor Green
    
    Write-Host "`n=== ðŸ› ï¸ AGENTS ET OUTILS ===" -ForegroundColor Magenta
    Write-Host "8. ðŸ”§ Assistant IA (Agent systÃ¨me)" -ForegroundColor Green
    Write-Host "9. ðŸ“Š Rapport de performances" -ForegroundColor Green
    Write-Host "10. âš™ï¸ Optimisation GPU" -ForegroundColor Green
    
    Write-Host "`n11. âŒ Quitter" -ForegroundColor Red
    Write-Host "==================================" -ForegroundColor Cyan
}

# VÃ©rifier et dÃ©marrer Ollama si nÃ©cessaire
Start-OllamaIfNeeded

# Activation de l'environnement virtuel CrewAI
Write-Host "ðŸ¤– Activation de l'environnement CrewAI..." -ForegroundColor Yellow
.\crew_env\Scripts\Activate

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
            Write-Host "Lancement de TabbyML avec accÃ©lÃ©ration GPU..." -ForegroundColor Yellow
            tabby serve --model TabbyML/DeepseekCoder-33B-instruct-q5_K_M --device cuda 
        }
        "6" { 
            if (-not (Test-DockerInstallation)) {
                Write-Host "âŒ Docker n'est pas installÃ©. Veuillez installer Docker Desktop depuis:" -ForegroundColor Red
                Write-Host "https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
                continue
            }
            
            $openDevinPath = "OpenDevin"
            if (-not (Test-DirectoryExists $openDevinPath)) {
                Write-Host "âŒ Le dossier OpenDevin n'existe pas. Clonage du dÃ©pÃ´t..." -ForegroundColor Yellow
                git clone https://github.com/OpenDevin/OpenDevin.git
            }
            
            Set-Location $openDevinPath
            $env:OPENDEVIN_GPU_ACCELERATION = "true"
            $env:OPENDEVIN_MODEL = "codellama:34b-instruct-q5_K_M"
            docker compose -f docker-compose.yml -f docker-compose.gpu.yml up
            Set-Location ..
        }
        "7" {
            Write-Host "`n=== ðŸ¤ MODE COLLABORATION IA ===" -ForegroundColor Cyan
            Write-Host "Ce mode permet aux agents IA de collaborer pour rÃ©soudre des tÃ¢ches complexes."
            Write-Host "Exemple: CrÃ©er un fichier PHP, analyser un site web, etc."
            $task = Read-Host "`nEntrez la tÃ¢che Ã  accomplir"
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
            Write-Host "GÃ©nÃ©ration du rapport de performances..." -ForegroundColor Yellow
            python scripts/test_performance.ps1
        }
        "10" { 
            Write-Host "Optimisation du GPU..." -ForegroundColor Yellow
            .\scripts\gpu_optimization.ps1 
        }
        "11" { 
            Write-Host "ðŸ‘‹ Fermeture du Paradis IA..." -ForegroundColor Cyan
            break 
        }
        default { Write-Host "âŒ Option invalide, veuillez rÃ©essayer." -ForegroundColor Red }
    }
} while ($choice -ne "11")

# DÃ©sactivation de l'environnement virtuel
deactivate
