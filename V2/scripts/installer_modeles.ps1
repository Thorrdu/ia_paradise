# Script d'installation des modèles IA optimisés pour Paradis IA V2
# Configuration cible : RTX 4060, 32-64 Go RAM

Write-Host "🚀 Installation des modèles IA pour le Paradis IA V2" -ForegroundColor Cyan
Write-Host "Configuration cible : RTX 4060, 32-64 Go RAM" -ForegroundColor Yellow

# Vérifier si Ollama est installé
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Ollama n'est pas installé. Veuillez d'abord exécuter le script setup_environment.ps1" -ForegroundColor Red
    Exit
}

# Menu principal
function Show-Menu {
    Write-Host "`n=== 🧠 INSTALLATION DES MODÈLES IA ===" -ForegroundColor Cyan
    Write-Host "1. Installer tous les modèles recommandés (~ 30 Go)" -ForegroundColor White
    Write-Host "2. Installer uniquement Mixtral 8x7B optimisé (~ 9 Go)" -ForegroundColor White
    Write-Host "3. Installer uniquement DeepSeek Coder (~ 7 Go)" -ForegroundColor White
    Write-Host "4. Installer uniquement Phi-3 Mini (~ 2 Go)" -ForegroundColor White
    Write-Host "5. Créer un modèle personnalisé" -ForegroundColor White
    Write-Host "6. Quitter" -ForegroundColor White
    Write-Host "===================================" -ForegroundColor Cyan
    
    $choice = Read-Host "Choisissez une option (1-6)"
    
    switch ($choice) {
        "1" { Install-AllModels; Show-Menu }
        "2" { Install-MixtralOptimized; Show-Menu }
        "3" { Install-DeepSeekCoder; Show-Menu }
        "4" { Install-Phi3Mini; Show-Menu }
        "5" { Create-CustomModel; Show-Menu }
        "6" { 
            Write-Host "`n🎉 Installation des modèles terminée!" -ForegroundColor Green
            Exit
        }
        default { 
            Write-Host "❌ Option invalide, veuillez réessayer." -ForegroundColor Red
            Show-Menu
        }
    }
}

# Fonction pour installer tous les modèles recommandés
function Install-AllModels {
    Write-Host "`n⬇️ Installation de tous les modèles recommandés..." -ForegroundColor Cyan
    Write-Host "⚠️ Cette opération nécessite environ 30 Go d'espace disque" -ForegroundColor Yellow
    Write-Host "Temps d'installation estimé : 15-30 minutes selon votre connexion" -ForegroundColor Yellow
    
    $confirm = Read-Host "Confirmer l'installation de tous les modèles? (O/N) [O]"
    
    if ($confirm -ne "N" -and $confirm -ne "n") {
        # Mixtral 8x7B (Optimisé)
        Install-MixtralOptimized
        
        # DeepSeek Coder
        Install-DeepSeekCoder
        
        # Phi-3 Mini
        Install-Phi3Mini
        
        # Modèles supplémentaires
        Write-Host "`n⬇️ Installation de CodeLlama 34B (quantifié)..." -ForegroundColor Yellow
        ollama pull codellama:34b-instruct-q5_K_M
        
        Write-Host "`n⬇️ Installation de Dolphin Mixtral..." -ForegroundColor Yellow
        ollama pull dolphin-mixtral
        
        Write-Host "✅ Tous les modèles ont été installés avec succès!" -ForegroundColor Green
    }
}

# Fonction pour installer Mixtral optimisé
function Install-MixtralOptimized {
    Write-Host "`n⬇️ Installation de Mixtral 8x7B optimisé pour RTX 4060..." -ForegroundColor Yellow
    
    # Vérifier si le fichier modelfile existe, sinon le créer
    $modelfilePath = "..\modeles\modelfiles\mixtral-optimized"
    
    if (-not (Test-Path $modelfilePath)) {
        Write-Host "Création du fichier de modèle optimisé pour la RTX 4060..." -ForegroundColor Yellow
        
        @"
FROM mixtral
PARAMETER num_ctx 16384
PARAMETER num_gpu 1
PARAMETER num_thread 8
PARAMETER temperature 0.7
PARAMETER repeat_penalty 1.1
PARAMETER stop "<|im_end|>"
PARAMETER stop "</answer>"
"@ | Out-File -FilePath $modelfilePath -Force
        
        Write-Host "✅ Fichier de modèle créé avec succès" -ForegroundColor Green
    }
    
    # Télécharger Mixtral base s'il n'est pas déjà présent
    $ollamaList = ollama list
    
    if (-not ($ollamaList -match "mixtral:latest")) {
        Write-Host "⬇️ Téléchargement du modèle Mixtral base..." -ForegroundColor Yellow
        ollama pull mixtral
    }
    
    # Créer le modèle optimisé
    Write-Host "⚙️ Création du modèle Mixtral optimisé pour la RTX 4060..." -ForegroundColor Yellow
    ollama create mixtral-optimized -f $modelfilePath
    
    Write-Host "✅ Mixtral optimisé a été installé avec succès!" -ForegroundColor Green
    Write-Host "Pour utiliser ce modèle: ollama run mixtral-optimized" -ForegroundColor Green
}

# Fonction pour installer DeepSeek Coder
function Install-DeepSeekCoder {
    Write-Host "`n⬇️ Installation de DeepSeek Coder (modèle de programmation)..." -ForegroundColor Yellow
    
    # Vérifier si DeepSeek Coder est déjà installé
    $ollamaList = ollama list
    
    if (-not ($ollamaList -match "deepseek-coder")) {
        Write-Host "⬇️ Téléchargement de DeepSeek Coder quantifié..." -ForegroundColor Yellow
        ollama pull deepseek-coder:33b-instruct-q5_K_M
    } else {
        Write-Host "✅ DeepSeek Coder est déjà installé" -ForegroundColor Green
    }
    
    Write-Host "✅ DeepSeek Coder a été installé avec succès!" -ForegroundColor Green
    Write-Host "Pour utiliser ce modèle: ollama run deepseek-coder:33b-instruct-q5_K_M" -ForegroundColor Green
}

# Fonction pour installer Phi-3 Mini
function Install-Phi3Mini {
    Write-Host "`n⬇️ Installation de Phi-3 Mini (modèle léger de Microsoft)..." -ForegroundColor Yellow
    
    # Vérifier si Phi-3 Mini est déjà installé
    $ollamaList = ollama list
    
    if (-not ($ollamaList -match "phi3:mini")) {
        Write-Host "⬇️ Téléchargement de Phi-3 Mini..." -ForegroundColor Yellow
        ollama pull phi3:mini
    } else {
        Write-Host "✅ Phi-3 Mini est déjà installé" -ForegroundColor Green
    }
    
    Write-Host "✅ Phi-3 Mini a été installé avec succès!" -ForegroundColor Green
    Write-Host "Pour utiliser ce modèle: ollama run phi3:mini" -ForegroundColor Green
}

# Fonction pour créer un modèle personnalisé
function Create-CustomModel {
    Write-Host "`n🔧 Création d'un modèle personnalisé..." -ForegroundColor Cyan
    
    # Demander le modèle base
    Write-Host "`nModèles de base disponibles:" -ForegroundColor Yellow
    Write-Host "1. mixtral (recommandé pour tâches générales)" -ForegroundColor White
    Write-Host "2. llama3 (modèle Meta récent)" -ForegroundColor White
    Write-Host "3. deepseek-coder (spécialisé programmation)" -ForegroundColor White
    Write-Host "4. phi3:mini (léger et rapide)" -ForegroundColor White
    Write-Host "5. Autre (spécifier)" -ForegroundColor White
    
    $baseModelChoice = Read-Host "Choisissez un modèle de base (1-5)"
    
    switch ($baseModelChoice) {
        "1" { $baseModel = "mixtral" }
        "2" { $baseModel = "llama3" }
        "3" { $baseModel = "deepseek-coder" }
        "4" { $baseModel = "phi3:mini" }
        "5" { 
            $baseModel = Read-Host "Entrez le nom du modèle de base"
            # Vérifier si le modèle est disponible, sinon proposer de le télécharger
            $ollamaList = ollama list
            if (-not ($ollamaList -match $baseModel)) {
                $downloadModel = Read-Host "Ce modèle n'est pas disponible localement. Voulez-vous le télécharger? (O/N) [O]"
                if ($downloadModel -ne "N" -and $downloadModel -ne "n") {
                    ollama pull $baseModel
                }
            }
        }
        default { 
            Write-Host "❌ Option invalide, utilisation de mixtral par défaut." -ForegroundColor Red
            $baseModel = "mixtral" 
        }
    }
    
    # Demander le nom du modèle personnalisé
    $customModelName = Read-Host "Entrez un nom pour votre modèle personnalisé"
    
    if ([string]::IsNullOrEmpty($customModelName)) {
        $customModelName = "$baseModel-custom"
        Write-Host "Utilisation du nom par défaut: $customModelName" -ForegroundColor Yellow
    }
    
    # Demander les paramètres
    Write-Host "`nConfiguration des paramètres du modèle (appuyez sur Entrée pour utiliser les valeurs par défaut)" -ForegroundColor Yellow
    
    $numCtx = Read-Host "Taille du contexte (4096-32768) [16384]"
    if ([string]::IsNullOrEmpty($numCtx)) { $numCtx = "16384" }
    
    $numGpu = Read-Host "Nombre de GPU à utiliser (0-1) [1]"
    if ([string]::IsNullOrEmpty($numGpu)) { $numGpu = "1" }
    
    $numThread = Read-Host "Nombre de threads CPU (4-16) [8]"
    if ([string]::IsNullOrEmpty($numThread)) { $numThread = "8" }
    
    $temperature = Read-Host "Température (0.1-1.0) [0.7]"
    if ([string]::IsNullOrEmpty($temperature)) { $temperature = "0.7" }
    
    $repeatPenalty = Read-Host "Pénalité de répétition (1.0-1.5) [1.1]"
    if ([string]::IsNullOrEmpty($repeatPenalty)) { $repeatPenalty = "1.1" }
    
    # Créer le fichier de modèle personnalisé
    $customModelfilePath = "..\modeles\modelfiles\$customModelName"
    
    @"
FROM $baseModel
PARAMETER num_ctx $numCtx
PARAMETER num_gpu $numGpu
PARAMETER num_thread $numThread
PARAMETER temperature $temperature
PARAMETER repeat_penalty $repeatPenalty
PARAMETER stop "<|im_end|>"
PARAMETER stop "</answer>"
"@ | Out-File -FilePath $customModelfilePath -Force
    
    Write-Host "✅ Fichier de modèle personnalisé créé avec succès" -ForegroundColor Green
    
    # Créer le modèle
    Write-Host "⚙️ Création du modèle personnalisé $customModelName..." -ForegroundColor Yellow
    ollama create $customModelName -f $customModelfilePath
    
    Write-Host "✅ Modèle personnalisé $customModelName créé avec succès!" -ForegroundColor Green
    Write-Host "Pour utiliser ce modèle: ollama run $customModelName" -ForegroundColor Green
}

# Vérifier la configuration recommandée
Write-Host "`n🔍 Vérification de la compatibilité RTX 4060..." -ForegroundColor Cyan

try {
    $gpuInfo = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    
    if ($gpuInfo -match "4060") {
        Write-Host "✅ GPU RTX 4060 détecté - Configuration idéale pour les modèles recommandés" -ForegroundColor Green
    } else {
        Write-Host "⚠️ RTX 4060 non détectée. Configuration GPU actuelle:" -ForegroundColor Yellow
        Write-Host "$gpuInfo" -ForegroundColor White
        Write-Host "Les performances peuvent varier selon votre GPU" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Impossible de détecter le GPU - Assurez-vous que NVIDIA drivers et CUDA sont installés" -ForegroundColor Yellow
}

# Point d'entrée principal
Write-Host "`n💡 Ce script vous guidera dans l'installation des modèles IA optimisés pour la RTX 4060" -ForegroundColor Cyan
Write-Host "Les modèles seront configurés pour une performance optimale avec votre matériel" -ForegroundColor Cyan

# Afficher le menu principal
Show-Menu 