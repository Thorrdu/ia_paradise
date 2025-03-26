# Script d'installation guidée de CUDA et cuDNN pour le Paradis IA V2
# Spécifiquement optimisé pour Windows 11 avec RTX 4060

Write-Host "🚀 Installation guidée de CUDA et cuDNN pour le Paradis IA V2" -ForegroundColor Cyan
Write-Host "Configuration cible : Windows 11, 32-64 Go RAM, GeForce RTX 4060" -ForegroundColor Yellow

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

# Vérifier si CUDA est déjà installé
function Test-CudaInstallation {
    Write-Host "`n🔍 Vérification de l'installation CUDA existante..." -ForegroundColor Cyan
    
    $cudaInstalled = Test-Path "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"
    
    if ($cudaInstalled) {
        try {
            $nvccOutput = nvcc --version
            $nvccVersion = [regex]::Match($nvccOutput, "release (\d+\.\d+)").Groups[1].Value
            
            Write-Host "✅ CUDA $nvccVersion est déjà installé" -ForegroundColor Green
            
            if ([version]$nvccVersion -lt [version]"11.8") {
                Write-Host "⚠️ Version CUDA détectée ($nvccVersion) est inférieure à la version recommandée (11.8)" -ForegroundColor Yellow
                Write-Host "Pour des performances optimales avec PyTorch et TensorFlow, une mise à jour est recommandée" -ForegroundColor Yellow
                return $false
            } else {
                return $true
            }
        } catch {
            Write-Host "⚠️ CUDA semble être installé, mais nvcc n'est pas disponible dans le PATH" -ForegroundColor Yellow
            return $false
        }
    } else {
        Write-Host "❌ CUDA n'est pas installé" -ForegroundColor Red
        return $false
    }
}

# Guide d'installation CUDA
function Install-Cuda {
    Write-Host "`n⬇️ Installation de CUDA Toolkit 11.8 (recommandé pour PyTorch/TensorFlow)..." -ForegroundColor Cyan
    
    # Vérifier si CUDA 11.8 est la version appropriée
    Write-Host "Les versions recommandées pour les bibliothèques d'IA sont :" -ForegroundColor Yellow
    Write-Host "• CUDA 11.8 - Compatible avec PyTorch 2.0-2.1, TensorFlow 2.12-2.13" -ForegroundColor Yellow
    Write-Host "• CUDA 12.1 - Compatible avec PyTorch 2.2+, TensorFlow 2.14+" -ForegroundColor Yellow
    
    $cudaVersion = Read-Host "Quelle version de CUDA souhaitez-vous installer? (11.8/12.1) [11.8]"
    
    if ([string]::IsNullOrEmpty($cudaVersion)) {
        $cudaVersion = "11.8"
    }
    
    if ($cudaVersion -eq "11.8") {
        Start-Process "https://developer.nvidia.com/cuda-11-8-0-download-archive?target_os=Windows&target_arch=x86_64"
    } elseif ($cudaVersion -eq "12.1") {
        Start-Process "https://developer.nvidia.com/cuda-12-1-0-download-archive?target_os=Windows&target_arch=x86_64"
    } else {
        Write-Host "❌ Version non reconnue. Ouverture de la page de téléchargement générale..." -ForegroundColor Red
        Start-Process "https://developer.nvidia.com/cuda-downloads"
    }
    
    Write-Host "`n⚠️ Veuillez suivre les instructions d'installation dans votre navigateur:" -ForegroundColor Yellow
    Write-Host "1. Sélectionnez Windows, x86_64, Windows 11, et le type d'installateur (exe recommandé)" -ForegroundColor White
    Write-Host "2. Téléchargez et exécutez l'installateur" -ForegroundColor White
    Write-Host "3. Dans l'installateur, choisissez 'Express Installation' pour une configuration standard" -ForegroundColor White
    Write-Host "4. Une fois l'installation terminée, redémarrez votre ordinateur" -ForegroundColor White
    
    Write-Host "`nAppuyez sur une touche une fois l'installation de CUDA terminée..." -ForegroundColor Green
    [void][System.Console]::ReadKey($true)
    
    # Vérifier si l'installation a réussi
    if (Test-CudaInstallation) {
        Write-Host "✅ CUDA a été installé avec succès!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ L'installation de CUDA semble avoir échoué ou n'est pas correctement configurée." -ForegroundColor Yellow
        Write-Host "Vérifiez que CUDA est bien dans votre PATH système." -ForegroundColor Yellow
    }
}

# Guide d'installation cuDNN
function Install-CuDNN {
    Write-Host "`n⬇️ Installation de cuDNN (Bibliothèque NVIDIA Deep Neural Network)..." -ForegroundColor Cyan
    
    # Vérifier la version de CUDA installée
    try {
        $nvccOutput = nvcc --version
        $cudaVersion = [regex]::Match($nvccOutput, "release (\d+\.\d+)").Groups[1].Value
    } catch {
        $cudaVersion = "inconnu"
    }
    
    Write-Host "`n⚠️ L'installation de cuDNN nécessite un compte NVIDIA Developer gratuit" -ForegroundColor Yellow
    Write-Host "Voici les étapes à suivre:" -ForegroundColor White
    Write-Host "1. Accédez à la page de téléchargement de cuDNN (qui va s'ouvrir)" -ForegroundColor White
    Write-Host "2. Créez un compte ou connectez-vous à votre compte NVIDIA Developer" -ForegroundColor White
    Write-Host "3. Acceptez les termes du NVIDIA Software License Agreement" -ForegroundColor White
    Write-Host "4. Téléchargez la version de cuDNN compatible avec CUDA $cudaVersion" -ForegroundColor White
    
    Start-Process "https://developer.nvidia.com/cudnn"
    
    Write-Host "`nUne fois le fichier téléchargé, suivez ces instructions:" -ForegroundColor Cyan
    Write-Host "1. Extrayez l'archive ZIP téléchargée" -ForegroundColor White
    Write-Host "2. Copiez les fichiers suivants dans les répertoires CUDA correspondants:" -ForegroundColor White
    Write-Host "   • Copiez cudnn*.dll du dossier 'bin' vers C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v$cudaVersion\bin" -ForegroundColor White  
    Write-Host "   • Copiez cudnn*.h du dossier 'include' vers C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v$cudaVersion\include" -ForegroundColor White
    Write-Host "   • Copiez cudnn*.lib du dossier 'lib' vers C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v$cudaVersion\lib\x64" -ForegroundColor White
    
    Write-Host "`nAppuyez sur une touche une fois l'installation de cuDNN terminée..." -ForegroundColor Green
    [void][System.Console]::ReadKey($true)
    
    Write-Host "✅ Installation CUDA/cuDNN terminée!" -ForegroundColor Green
    Write-Host "Les modèles IA du Paradis IA V2 peuvent maintenant exploiter pleinement votre RTX 4060" -ForegroundColor Green
}

# Vérification des pilotes NVIDIA
function Check-NvidiaDrivers {
    Write-Host "`n🔍 Vérification des pilotes NVIDIA..." -ForegroundColor Cyan
    
    try {
        $nvidiaOutput = nvidia-smi
        
        if ($nvidiaOutput -match "Driver Version: (\d+\.\d+)") {
            $driverVersion = $matches[1]
            Write-Host "✅ Pilote NVIDIA version $driverVersion détecté" -ForegroundColor Green
            
            if ([version]$driverVersion -lt [version]"530.0") {
                Write-Host "⚠️ Version de pilote ($driverVersion) peut être obsolète pour l'IA" -ForegroundColor Yellow
                Write-Host "Une mise à jour vers la dernière version est recommandée pour des performances optimales" -ForegroundColor Yellow
                
                $updateDrivers = Read-Host "Souhaitez-vous visiter la page de téléchargement des pilotes NVIDIA? (O/N) [O]"
                if ($updateDrivers -ne "N" -and $updateDrivers -ne "n") {
                    Start-Process "https://www.nvidia.fr/Download/index.aspx?lang=fr"
                }
            }
        } else {
            Write-Host "⚠️ Impossible de déterminer la version du pilote NVIDIA" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Pilotes NVIDIA non détectés ou nvidia-smi n'est pas disponible" -ForegroundColor Red
        Write-Host "Veuillez installer les pilotes NVIDIA appropriés pour votre RTX 4060" -ForegroundColor Yellow
        
        $installDrivers = Read-Host "Souhaitez-vous visiter la page de téléchargement des pilotes NVIDIA? (O/N) [O]"
        if ($installDrivers -ne "N" -and $installDrivers -ne "n") {
            Start-Process "https://www.nvidia.fr/Download/index.aspx?lang=fr"
        }
    }
}

# Installation de PyTorch avec CUDA
function Install-PyTorchCuda {
    Write-Host "`n🔧 Installation de PyTorch avec support CUDA..." -ForegroundColor Cyan
    
    try {
        # Obtenir la version de CUDA
        $nvccOutput = nvcc --version
        $cudaVersion = [regex]::Match($nvccOutput, "release (\d+\.\d+)").Groups[1].Value
        
        if ([version]$cudaVersion -ge [version]"12.0") {
            Write-Host "Installation de PyTorch avec CUDA 12.1..." -ForegroundColor Yellow
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
        } elseif ([version]$cudaVersion -ge [version]"11.8") {
            Write-Host "Installation de PyTorch avec CUDA 11.8..." -ForegroundColor Yellow
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        } else {
            Write-Host "⚠️ Version CUDA $cudaVersion non optimale pour PyTorch" -ForegroundColor Yellow
            Write-Host "Installation de PyTorch avec la version CUDA la plus proche disponible (11.8)..." -ForegroundColor Yellow
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        }
        
        # Vérifier l'installation
        Write-Host "Vérification de l'installation de PyTorch avec CUDA..." -ForegroundColor Yellow
        python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA disponible:', torch.cuda.is_available()); print('Périphérique CUDA:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
        
        Write-Host "✅ PyTorch avec support CUDA installé avec succès" -ForegroundColor Green
    } catch {
        Write-Host "❌ Erreur lors de l'installation de PyTorch: $_" -ForegroundColor Red
    }
}

# Menu principal
function Show-Menu {
    Write-Host "`n=== 🛠️ MENU D'INSTALLATION CUDA/cuDNN ===" -ForegroundColor Cyan
    Write-Host "1. Vérifier les pilotes NVIDIA" -ForegroundColor White
    Write-Host "2. Installer/Mettre à jour CUDA Toolkit" -ForegroundColor White
    Write-Host "3. Guide d'installation cuDNN" -ForegroundColor White
    Write-Host "4. Installer PyTorch avec support CUDA" -ForegroundColor White
    Write-Host "5. Quitter" -ForegroundColor White
    Write-Host "===================================" -ForegroundColor Cyan
    
    $choice = Read-Host "Choisissez une option (1-5)"
    
    switch ($choice) {
        "1" { Check-NvidiaDrivers; Show-Menu }
        "2" { Install-Cuda; Show-Menu }
        "3" { Install-CuDNN; Show-Menu }
        "4" { Install-PyTorchCuda; Show-Menu }
        "5" { 
            Write-Host "`n🎉 Installation terminée! Votre système est maintenant prêt pour le Paradis IA V2." -ForegroundColor Green
            Write-Host "Retournez au script d'installation principal pour poursuivre la configuration du Paradis IA." -ForegroundColor Yellow
            Exit
        }
        default { 
            Write-Host "❌ Option invalide, veuillez réessayer." -ForegroundColor Red
            Show-Menu
        }
    }
}

# Point d'entrée principal
Write-Host "`n💡 Ce script vous guidera dans l'installation et la configuration de CUDA et cuDNN," -ForegroundColor Cyan
Write-Host "composants essentiels pour que votre RTX 4060 puisse exécuter efficacement les modèles d'IA." -ForegroundColor Cyan

Write-Host "`nRecommandations pour le Paradis IA V2 :" -ForegroundColor Yellow
Write-Host "• CUDA 11.8+ : Compatible avec tous les modèles d'IA du Paradis IA" -ForegroundColor White
Write-Host "• cuDNN correspondant à votre version CUDA" -ForegroundColor White
Write-Host "• Pilotes NVIDIA récents (530+)" -ForegroundColor White

# Commence par vérifier les pilotes, puis montre le menu
Check-NvidiaDrivers
Show-Menu 