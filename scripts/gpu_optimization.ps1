Write-Host "🚀 Optimisation GPU RTX 4060 pour IA" -ForegroundColor Cyan

# Vérifier si on est en mode administrateur
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

# Vérifier la présence de CUDA
if (-not (Test-Path "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA")) {
    Write-Host "❌ CUDA non détecté. Installez CUDA Toolkit depuis:" -ForegroundColor Red
    Write-Host "https://developer.nvidia.com/cuda-downloads" -ForegroundColor Yellow
    
    $installCuda = Read-Host "Voulez-vous lancer l'installation de CUDA maintenant? (O/N) [O]"
    if ($installCuda -ne "N" -and $installCuda -ne "n") {
        Start-Process "https://developer.nvidia.com/cuda-downloads"
        Write-Host "Veuillez compléter l'installation de CUDA Toolkit manuellement via le navigateur" -ForegroundColor Yellow
        Write-Host "Une fois l'installation terminée, relancez ce script" -ForegroundColor Yellow
        Exit
    } else {
        Exit
    }
}

# Vérifier que le GPU est bien une RTX 4060 ou compatible
try {
    $gpuInfo = nvidia-smi --query-gpu=name --format=csv,noheader
    Write-Host "GPU détecté : $gpuInfo" -ForegroundColor Green
    
    if (-not ($gpuInfo -match "RTX")) {
        Write-Host "⚠️ Attention: Votre GPU n'est pas une RTX. Certaines optimisations pourraient ne pas être applicables." -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Impossible de détecter le GPU. Vérifiez que les pilotes NVIDIA sont correctement installés." -ForegroundColor Red
    Exit
}

Write-Host "`n🔧 Application des optimisations système pour IA..." -ForegroundColor Cyan

# Optimiser le Shader Cache pour DirectX
try {
    Write-Host "Optimisation du Shader Cache DirectX..." -ForegroundColor Yellow
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "DisableShaderCache" -Value 0 -Type DWord -ErrorAction Stop
    Write-Host "✅ Shader Cache optimisé" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Impossible d'optimiser le Shader Cache: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Activer le Game Mode pour optimiser les performances
try {
    Write-Host "Activation du Game Mode pour optimiser les performances..." -ForegroundColor Yellow
    
    if (-not (Test-Path "HKCU:\Software\Microsoft\GameBar")) {
        New-Item -Path "HKCU:\Software\Microsoft\GameBar" -Force | Out-Null
    }
    
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\GameBar" -Name "AllowAutoGameMode" -Value 1 -Type DWord -ErrorAction Stop
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\GameBar" -Name "AutoGameModeEnabled" -Value 1 -Type DWord -ErrorAction Stop
    Write-Host "✅ Game Mode activé" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Impossible d'activer le Game Mode: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Optimiser le plan d'alimentation
try {
    Write-Host "Configuration du plan d'alimentation pour performances maximales..." -ForegroundColor Yellow
    powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
    Write-Host "✅ Plan d'alimentation optimisé" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Impossible de configurer le plan d'alimentation: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Configurer NVIDIA pour performances maximales
try {
    Write-Host "Configuration du GPU NVIDIA pour performances maximales..." -ForegroundColor Yellow
    
    # Mettre le GPU en mode persistant
    nvidia-smi -pm 1
    
    # Désactiver l'auto-boost pour un contrôle plus précis
    nvidia-smi --auto-boost-default=0
    
    # Configurer les fréquences d'horloge pour performances optimales
    # Ces valeurs sont optimisées pour la RTX 4060, ajustez si nécessaire
    nvidia-smi -ac 3004,1708
    
    Write-Host "✅ Configuration NVIDIA optimisée" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Impossible de configurer les paramètres NVIDIA: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Vérifier les performances actuelles du GPU
try {
    Write-Host "`n📊 Vérification des performances GPU après optimisation:" -ForegroundColor Cyan
    $gpuPerf = nvidia-smi --query-gpu=name,clocks.current.memory,clocks.current.sm,temperature.gpu,utilization.gpu,power.draw --format=csv,noheader
    Write-Host $gpuPerf -ForegroundColor Green
} catch {
    Write-Host "⚠️ Impossible d'obtenir les informations de performance GPU" -ForegroundColor Yellow
}

Write-Host "`n✅ Optimisation GPU terminée! Votre GPU est maintenant configuré pour des performances IA optimales." -ForegroundColor Green
Write-Host "ℹ️ Note: Certains paramètres reviendront à leurs valeurs par défaut après un redémarrage." -ForegroundColor Yellow
Write-Host "   Pour une optimisation permanente, vous pouvez ajouter ce script à votre démarrage." -ForegroundColor Yellow 