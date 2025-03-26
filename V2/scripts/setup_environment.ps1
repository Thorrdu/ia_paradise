# Script d'installation automatisée des prérequis pour le Paradis IA V2
# Configuration cible : Windows 11, 32-64 Go RAM, GeForce RTX 4060

Write-Host "🚀 Installation des prérequis pour le Paradis IA V2 - Édition Haute Performance" -ForegroundColor Cyan
Write-Host "Configuration cible : Windows 11, 32-64 Go RAM, GeForce RTX 4060" -ForegroundColor Yellow
Write-Host "Ce script va installer et configurer tous les composants nécessaires pour votre Paradis IA" -ForegroundColor Yellow

# Fonction pour vérifier si on est en mode administrateur
function Test-Administrator {
    $user = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal $user
    return $principal.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

# Vérifier les privilèges d'administrateur
if (-not (Test-Administrator)) {
    Write-Host "❌ Ce script nécessite des privilèges d'administrateur pour fonctionner correctement." -ForegroundColor Red
    Write-Host "Veuillez relancer PowerShell en tant qu'administrateur et réexécuter ce script." -ForegroundColor Red
    Exit
}

# Créer la structure de dossiers du projet
function Create-ProjectStructure {
    Write-Host "`n📁 Création de la structure de dossiers du projet..." -ForegroundColor Cyan
    
    if (-not (Test-Path "../modeles")) { mkdir -p "../modeles/modelfiles" | Out-Null }
    if (-not (Test-Path "../agents")) { mkdir -p "../agents" | Out-Null }
    if (-not (Test-Path "../config")) { mkdir -p "../config" | Out-Null }
    if (-not (Test-Path "../scripts")) { mkdir -p "../scripts" | Out-Null }
    
    Write-Host "✅ Structure de dossiers créée avec succès" -ForegroundColor Green
}

# Vérifier et installer les dépendances Python
function Install-PythonDependencies {
    Write-Host "`n🐍 Installation et configuration de Python..." -ForegroundColor Cyan
    
    # Vérifier si Python est installé
    $pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
    
    if (-not $pythonInstalled) {
        Write-Host "⬇️ Téléchargement et installation de Python 3.10..." -ForegroundColor Yellow
        $pythonUrl = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
        $pythonInstaller = "$env:TEMP\python-3.10.11-amd64.exe"
        
        try {
            Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
            Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
            Remove-Item $pythonInstaller
            
            # Rafraîchir le PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            
            Write-Host "✅ Python installé avec succès" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Échec de l'installation automatique de Python" -ForegroundColor Red
            Write-Host "Veuillez installer Python manuellement depuis: https://www.python.org/downloads/windows/" -ForegroundColor Yellow
            Write-Host "Assurez-vous de cocher 'Add Python to PATH' lors de l'installation" -ForegroundColor Yellow
            return $false
        }
    }
    else {
        $pythonVersion = python --version
        Write-Host "✅ $pythonVersion déjà installé" -ForegroundColor Green
    }
    
    # Installer les packages Python optimisés GPU
    Write-Host "⬇️ Installation des packages Python pour GPU..." -ForegroundColor Yellow
    
    python -m pip install --upgrade pip
    
    # Créer l'environnement virtuel pour CrewAI s'il n'existe pas déjà
    if (-not (Test-Path "../crew_env")) {
        python -m venv ../crew_env
        Write-Host "✅ Environnement virtuel 'crew_env' créé" -ForegroundColor Green
    }
    
    # Activer l'environnement virtuel et installer les packages
    & ../crew_env/Scripts/Activate.ps1
    
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    pip install tensorflow-gpu
    pip install crewai langchain
    pip install transformers accelerate bitsandbytes
    pip install psutil
    
    Write-Host "✅ Packages Python installés avec succès" -ForegroundColor Green
    deactivate
    
    return $true
}

# Vérifier et installer Ollama
function Install-Ollama {
    Write-Host "`n🧠 Installation et configuration d'Ollama..." -ForegroundColor Cyan
    
    # Vérifier si Ollama est installé
    $ollamaInstalled = Get-Command ollama -ErrorAction SilentlyContinue
    
    if (-not $ollamaInstalled) {
        Write-Host "⬇️ Téléchargement et installation d'Ollama..." -ForegroundColor Yellow
        Start-Process "https://ollama.com/download/windows"
        
        Write-Host "⚠️ Veuillez compléter l'installation d'Ollama manuellement via le navigateur" -ForegroundColor Yellow
        Write-Host "Une fois l'installation terminée, appuyez sur une touche pour continuer..." -ForegroundColor Yellow
        [void][System.Console]::ReadKey($true)
        
        # Rafraîchir le PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
    else {
        Write-Host "✅ Ollama déjà installé" -ForegroundColor Green
    }
    
    # Configurer Ollama pour utilisation GPU
    Write-Host "⚙️ Configuration d'Ollama pour utilisation GPU..." -ForegroundColor Yellow
    
    $ollamaConfigPath = "$env:USERPROFILE\.ollama\config.json"
    $ollamaConfigDir = [System.IO.Path]::GetDirectoryName($ollamaConfigPath)
    
    if (-not (Test-Path $ollamaConfigDir)) {
        New-Item -ItemType Directory -Path $ollamaConfigDir -Force | Out-Null
    }
    
    $ollamaConfig = @{
        "gpu" = $true
        "cuda" = $true
    }
    
    $ollamaConfig | ConvertTo-Json | Out-File -FilePath $ollamaConfigPath -Force
    
    Write-Host "✅ Ollama configuré pour utilisation GPU" -ForegroundColor Green
    
    # Créer le fichier modèle optimisé pour Mixtral
    $modelfilesDir = "../modeles/modelfiles"
    if (-not (Test-Path $modelfilesDir)) {
        New-Item -ItemType Directory -Path $modelfilesDir -Force | Out-Null
    }
    
    @"
FROM mixtral
PARAMETER num_ctx 16384
PARAMETER num_gpu 1
PARAMETER num_thread 8
PARAMETER temperature 0.7
PARAMETER stop "<|im_end|>"
PARAMETER stop "</answer>"
"@ | Out-File -FilePath "$modelfilesDir/mixtral-optimized" -Force
    
    Write-Host "✅ Fichier modèle Mixtral optimisé créé" -ForegroundColor Green
}

# Vérifier et installer CUDA Toolkit
function Install-CudaToolkit {
    Write-Host "`n⚡ Vérification et installation de CUDA Toolkit..." -ForegroundColor Cyan
    
    # Vérifier si CUDA est installé
    $cudaInstalled = Test-Path "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"
    
    if (-not $cudaInstalled) {
        Write-Host "CUDA Toolkit n'est pas installé" -ForegroundColor Yellow
        Write-Host "Ouverture de la page de téléchargement de CUDA Toolkit..." -ForegroundColor Yellow
        Start-Process "https://developer.nvidia.com/cuda-downloads"
        
        Write-Host "⚠️ Veuillez installer CUDA Toolkit manuellement via le navigateur" -ForegroundColor Yellow
        Write-Host "Une fois l'installation terminée, appuyez sur une touche pour continuer..." -ForegroundColor Yellow
        [void][System.Console]::ReadKey($true)
    }
    else {
        Write-Host "✅ CUDA Toolkit déjà installé" -ForegroundColor Green
        
        # Vérifier la version de CUDA
        try {
            $nvccVersion = nvcc --version
            Write-Host "Version CUDA: $nvccVersion" -ForegroundColor Green
        }
        catch {
            Write-Host "⚠️ CUDA est installé mais nvcc n'est pas dans le PATH" -ForegroundColor Yellow
        }
    }
    
    # Vérifier si cuDNN est mentionné
    Write-Host "`n⚠️ N'oubliez pas d'installer cuDNN manuellement (nécessite un compte NVIDIA)" -ForegroundColor Yellow
    Write-Host "Téléchargez-le depuis: https://developer.nvidia.com/cudnn" -ForegroundColor Yellow
}

# Vérifier et installer Docker avec support WSL2
function Install-Docker {
    Write-Host "`n🐳 Vérification et installation de Docker..." -ForegroundColor Cyan
    
    # Vérifier si Docker est installé
    $dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
    
    if (-not $dockerInstalled) {
        # Vérifier si WSL2 est installé
        $wsl2Installed = Get-Command wsl -ErrorAction SilentlyContinue
        
        if (-not $wsl2Installed) {
            Write-Host "⬇️ Installation de WSL2..." -ForegroundColor Yellow
            try {
                wsl --install
                Write-Host "✅ WSL2 installé. Un redémarrage peut être nécessaire." -ForegroundColor Green
                Write-Host "⚠️ Si vous venez de redémarrer, veuillez continuer." -ForegroundColor Yellow
                Write-Host "⚠️ Sinon, veuillez redémarrer l'ordinateur et relancer ce script." -ForegroundColor Yellow
            }
            catch {
                Write-Host "❌ Échec de l'installation de WSL2. Veuillez l'installer manuellement." -ForegroundColor Red
            }
        }
        else {
            Write-Host "✅ WSL2 déjà installé" -ForegroundColor Green
        }
        
        # Télécharger et installer Docker Desktop
        Write-Host "⬇️ Téléchargement et installation de Docker Desktop..." -ForegroundColor Yellow
        Start-Process "https://www.docker.com/products/docker-desktop/"
        
        Write-Host "⚠️ Veuillez compléter l'installation de Docker Desktop manuellement via le navigateur" -ForegroundColor Yellow
        Write-Host "Une fois l'installation terminée, assurez-vous d'activer l'intégration WSL2 et GPU dans les paramètres" -ForegroundColor Yellow
        Write-Host "Appuyez sur une touche pour continuer..." -ForegroundColor Yellow
        [void][System.Console]::ReadKey($true)
    }
    else {
        Write-Host "✅ Docker déjà installé" -ForegroundColor Green
        
        # Vérifier la version de Docker
        $dockerVersion = docker --version
        Write-Host "Version Docker: $dockerVersion" -ForegroundColor Green
    }
}

# Vérifier et installer LM Studio
function Install-LMStudio {
    Write-Host "`n🔍 Vérification et installation de LM Studio..." -ForegroundColor Cyan
    
    # Vérifier si LM Studio est installé (en vérifiant le répertoire d'installation courant)
    $lmStudioInstalled = Test-Path "C:\Program Files\LM Studio" -or Test-Path "C:\Program Files (x86)\LM Studio"
    
    if (-not $lmStudioInstalled) {
        Write-Host "⬇️ Téléchargement et installation de LM Studio..." -ForegroundColor Yellow
        Start-Process "https://lmstudio.ai/"
        
        Write-Host "⚠️ Veuillez compléter l'installation de LM Studio manuellement via le navigateur" -ForegroundColor Yellow
        Write-Host "Une fois l'installation terminée, appuyez sur une touche pour continuer..." -ForegroundColor Yellow
        [void][System.Console]::ReadKey($true)
    }
    else {
        Write-Host "✅ LM Studio déjà installé" -ForegroundColor Green
    }
    
    Write-Host "⚠️ Après installation, n'oubliez pas d'activer l'accélération GPU dans les paramètres de LM Studio" -ForegroundColor Yellow
}

# Créer les scripts d'optimisation GPU
function Create-OptimizationScripts {
    Write-Host "`n⚙️ Création des scripts d'optimisation..." -ForegroundColor Cyan
    
    # Script d'optimisation GPU
    @"
# Script d'optimisation GPU RTX 4060 pour IA
Write-Host "🚀 Optimisation GPU RTX 4060 pour IA" -ForegroundColor Cyan

# Vérifier la présence de CUDA
if (-not (Test-Path "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA")) {
    Write-Host "❌ CUDA non détecté. Installez CUDA Toolkit depuis:" -ForegroundColor Red
    Write-Host "https://developer.nvidia.com/cuda-downloads" -ForegroundColor Yellow
    Exit
}

# Vérifier que les privilèges administrateur sont disponibles
`$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not `$currentPrincipal.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
    Write-Host "❌ Ce script nécessite des privilèges d'administrateur" -ForegroundColor Red
    Exit
}

# Optimiser le Shader Cache pour DirectX
try {
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "DisableShaderCache" -Value 0 -Type DWord
    Write-Host "✅ Shader Cache optimisé" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Impossible d'optimiser le Shader Cache: `$_" -ForegroundColor Yellow
}

# Activer le Game Mode pour optimiser les performances
try {
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\GameBar" -Name "AllowAutoGameMode" -Value 1 -Type DWord
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\GameBar" -Name "AutoGameModeEnabled" -Value 1 -Type DWord
    Write-Host "✅ Game Mode activé pour optimiser les performances" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Impossible d'activer le Game Mode: `$_" -ForegroundColor Yellow
}

# Configurer NVIDIA pour performances maximales
try {
    # Activer le mode persistant (préserve les paramètres entre les redémarrages)
    nvidia-smi -pm 1
    
    # Désactiver l'auto-boost pour un contrôle plus précis
    nvidia-smi --auto-boost-default=0
    
    # Configurer les fréquences d'horloge optimales pour l'IA (mémoire et GPU)
    # Note: Ces valeurs sont pour une RTX 4060, ajustez si nécessaire
    nvidia-smi -ac 3004,1708
    
    Write-Host "✅ Paramètres NVIDIA optimisés pour performances IA" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Impossible d'optimiser les paramètres NVIDIA: `$_" -ForegroundColor Yellow
    Write-Host "Vérifiez que nvidia-smi est disponible et que vous avez les privilèges administrateur" -ForegroundColor Yellow
}

Write-Host "✅ Optimisation GPU terminée!" -ForegroundColor Green
"@ | Out-File -FilePath "../scripts/gpu_optimization.ps1" -Force
    
    # Script de test de performance
    @"
# Script de test de performance du Paradis IA
Write-Host "📊 Test de performance des modèles IA" -ForegroundColor Cyan

`$outputFile = "../rapport_performance.txt"

# Tester chaque modèle avec un prompt standard
`$testPrompt = "Explique le concept de programmation orientée objet en PHP en 5 phrases concises."

# Fonction pour tester un modèle
function Test-Model {
    param(`$modelName, `$modelParam)
    
    Write-Host "Test du modèle `$modelName..." -ForegroundColor Yellow
    
    # Mesurer le temps de démarrage
    `$startTime = Get-Date
    `$result = ollama run `$modelParam -q "`$testPrompt"
    `$endTime = Get-Date
    `$duration = (`$endTime - `$startTime).TotalSeconds
    
    # Écrire les résultats
    "=== Test de `$modelName ===" | Out-File -FilePath `$outputFile -Append
    "Temps de réponse: `$duration secondes" | Out-File -FilePath `$outputFile -Append
    "Réponse: `$result" | Out-File -FilePath `$outputFile -Append
    "`n" | Out-File -FilePath `$outputFile -Append
    
    return @{
        Model = `$modelName
        Duration = `$duration
        ResponseLength = `$result.Length
    }
}

# Collecter les informations système
`$gpuInfo = try { nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader } catch { "Information GPU non disponible" }
`$cpuInfo = Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors
`$ramInfo = Get-CimInstance Win32_ComputerSystem | ForEach-Object { [math]::Round(`$_.TotalPhysicalMemory / 1GB, 2) }

# Préparer le fichier de sortie
"RAPPORT DE PERFORMANCE DES MODÈLES IA" | Out-File -FilePath `$outputFile
"Date: `$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath `$outputFile -Append
"Système: Windows `$(Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty Caption)" | Out-File -FilePath `$outputFile -Append
"GPU: `$gpuInfo" | Out-File -FilePath `$outputFile -Append
"CPU: `$(`$cpuInfo.Name) - `$(`$cpuInfo.NumberOfCores) cœurs / `$(`$cpuInfo.NumberOfLogicalProcessors) threads" | Out-File -FilePath `$outputFile -Append
"RAM: `$ramInfo GB" | Out-File -FilePath `$outputFile -Append
"`n" | Out-File -FilePath `$outputFile -Append

# Vérifier quels modèles sont installés
`$availableModels = ollama list

# Tester tous les modèles disponibles
`$results = @()

Write-Host "Vérification des modèles disponibles..." -ForegroundColor Cyan

if (`$availableModels -match "mixtral-optimized") {
    `$results += Test-Model -modelName "Mixtral 8x7B (optimisé)" -modelParam "mixtral-optimized"
} elseif (`$availableModels -match "mixtral") {
    `$results += Test-Model -modelName "Mixtral 8x7B" -modelParam "mixtral"
}

if (`$availableModels -match "dolphin-mixtral") {
    `$results += Test-Model -modelName "Dolphin Mixtral" -modelParam "dolphin-mixtral"
}

if (`$availableModels -match "codellama:34b") {
    `$results += Test-Model -modelName "CodeLlama 34B" -modelParam "codellama:34b-instruct-q5_K_M"
}

if (`$availableModels -match "deepseek-coder:33b") {
    `$results += Test-Model -modelName "DeepSeek Coder" -modelParam "deepseek-coder:33b-instruct-q5_K_M"
}

if (`$results.Count -eq 0) {
    Write-Host "❌ Aucun modèle IA n'a été trouvé. Veuillez d'abord installer les modèles avec:" -ForegroundColor Red
    Write-Host "ollama pull mixtral" -ForegroundColor Yellow
    Write-Host "ollama pull dolphin-mixtral" -ForegroundColor Yellow
    Write-Host "ollama pull codellama:34b-instruct-q5_K_M" -ForegroundColor Yellow
    Write-Host "ollama pull deepseek-coder:33b-instruct-q5_K_M" -ForegroundColor Yellow
    Exit
}

# Générer un résumé
"=== RÉSUMÉ DES PERFORMANCES ===" | Out-File -FilePath `$outputFile -Append
`$results | Sort-Object Duration | ForEach-Object {
    "`$(`$_.Model): `$(`$_.Duration) secondes, `$(`$_.ResponseLength) caractères" | Out-File -FilePath `$outputFile -Append
}

Write-Host "✅ Rapport de performance généré dans `$outputFile" -ForegroundColor Green
Write-Host "Ouvrir le rapport maintenant? (O/N)" -ForegroundColor Cyan
`$openReport = Read-Host

if (`$openReport -eq "O" -or `$openReport -eq "o") {
    Invoke-Item `$outputFile
}
"@ | Out-File -FilePath "../scripts/test_performance.ps1" -Force
    
    Write-Host "✅ Scripts d'optimisation et de test créés avec succès" -ForegroundColor Green
}

# Exécuter les fonctions d'installation
function Run-Installation {
    Create-ProjectStructure
    $pythonSuccess = Install-PythonDependencies
    
    if ($pythonSuccess) {
        Install-Ollama
        Install-CudaToolkit
        Install-Docker
        Install-LMStudio
        Create-OptimizationScripts
        
        Write-Host "`n🎉 Installation des prérequis terminée avec succès!" -ForegroundColor Cyan
        Write-Host "`nProchaines étapes recommandées:" -ForegroundColor Yellow
        Write-Host "1. Téléchargez les modèles IA haute performance:" -ForegroundColor Yellow
        Write-Host "   ollama pull mixtral" -ForegroundColor Green
        Write-Host "   ollama pull dolphin-mixtral" -ForegroundColor Green
        Write-Host "   ollama pull codellama:34b-instruct-q5_K_M" -ForegroundColor Green
        Write-Host "   ollama pull deepseek-coder:33b-instruct-q5_K_M" -ForegroundColor Green
        Write-Host "`n2. Créez le modèle Mixtral optimisé:" -ForegroundColor Yellow
        Write-Host "   ollama create mixtral-optimized -f modeles/modelfiles/mixtral-optimized" -ForegroundColor Green
        Write-Host "`n3. Optimisez votre GPU pour l'IA:" -ForegroundColor Yellow
        Write-Host "   .\scripts\gpu_optimization.ps1" -ForegroundColor Green
        Write-Host "`n4. Lancez le script d'intégration quand tout est prêt" -ForegroundColor Yellow
    }
    else {
        Write-Host "`n⚠️ L'installation de certains composants n'a pas pu être complétée" -ForegroundColor Red
        Write-Host "Veuillez résoudre les problèmes signalés et réessayer" -ForegroundColor Red
    }
}

# Exécuter l'installation
Run-Installation 