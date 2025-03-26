# Script de vérification du matériel pour Paradis IA V2
# Ce script analyse votre système pour vérifier sa compatibilité avec le Paradis IA V2

Write-Host "🔍 Analyse du matériel pour Paradis IA V2 - Édition Haute Performance" -ForegroundColor Cyan
Write-Host "Configuration cible recommandée: Windows 11, RTX 4060, 32-64 Go RAM" -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------------------" -ForegroundColor Cyan

# Fonction pour créer un rapport HTML
function Create-HtmlReport {
    param(
        [string]$reportPath,
        [hashtable]$systemInfo
    )
    
    $htmlContent = @"
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de Compatibilité - Paradis IA V2</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #0066cc;
            border-bottom: 2px solid #0066cc;
            padding-bottom: 10px;
        }
        h2 {
            color: #0066cc;
            margin-top: 30px;
        }
        .section {
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .success {
            color: #2e7d32;
            background-color: #e8f5e9;
            padding: 5px;
            border-radius: 4px;
            font-weight: bold;
        }
        .warning {
            color: #ef6c00;
            background-color: #fff3e0;
            padding: 5px;
            border-radius: 4px;
            font-weight: bold;
        }
        .error {
            color: #c62828;
            background-color: #ffebee;
            padding: 5px;
            border-radius: 4px;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #0066cc;
            color: white;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .recommendation {
            background-color: #e1f5fe;
            border-left: 4px solid #0288d1;
            padding: 15px;
            margin: 20px 0;
        }
        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
        }
        .badge-optimal {
            background-color: #43a047;
            color: white;
        }
        .badge-compatible {
            background-color: #fb8c00;
            color: white;
        }
        .badge-minimal {
            background-color: #e53935;
            color: white;
        }
    </style>
</head>
<body>
    <h1>Rapport de Compatibilité - Paradis IA V2</h1>
    <p>Date du rapport: $($systemInfo.Date)</p>
    
    <div class="section">
        <h2>Résumé</h2>
        <p>Niveau de compatibilité global: <span class="badge badge-$($systemInfo.CompatibilityLevel)">$($systemInfo.CompatibilityLevelText)</span></p>
        <p>$($systemInfo.SummaryText)</p>
    </div>
    
    <div class="section">
        <h2>Spécifications système</h2>
        <table>
            <tr>
                <th>Composant</th>
                <th>Détails</th>
                <th>Statut</th>
            </tr>
            <tr>
                <td>Système d'exploitation</td>
                <td>$($systemInfo.OS)</td>
                <td class="$($systemInfo.OSStatus)">$($systemInfo.OSStatusText)</td>
            </tr>
            <tr>
                <td>CPU</td>
                <td>$($systemInfo.CPU)</td>
                <td class="$($systemInfo.CPUStatus)">$($systemInfo.CPUStatusText)</td>
            </tr>
            <tr>
                <td>Carte graphique</td>
                <td>$($systemInfo.GPU)</td>
                <td class="$($systemInfo.GPUStatus)">$($systemInfo.GPUStatusText)</td>
            </tr>
            <tr>
                <td>Mémoire RAM</td>
                <td>$($systemInfo.RAM) Go</td>
                <td class="$($systemInfo.RAMStatus)">$($systemInfo.RAMStatusText)</td>
            </tr>
            <tr>
                <td>Espace disque disponible</td>
                <td>$($systemInfo.Disk) Go</td>
                <td class="$($systemInfo.DiskStatus)">$($systemInfo.DiskStatusText)</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Environnement CUDA</h2>
        <table>
            <tr>
                <th>Composant</th>
                <th>Détails</th>
                <th>Statut</th>
            </tr>
            <tr>
                <td>Pilotes NVIDIA</td>
                <td>$($systemInfo.NVDriver)</td>
                <td class="$($systemInfo.NVDriverStatus)">$($systemInfo.NVDriverStatusText)</td>
            </tr>
            <tr>
                <td>CUDA Toolkit</td>
                <td>$($systemInfo.CUDA)</td>
                <td class="$($systemInfo.CUDAStatus)">$($systemInfo.CUDAStatusText)</td>
            </tr>
            <tr>
                <td>cuDNN</td>
                <td>$($systemInfo.cuDNN)</td>
                <td class="$($systemInfo.cuDNNStatus)">$($systemInfo.cuDNNStatusText)</td>
            </tr>
        </table>
    </div>
    
    <div class="recommendation">
        <h2>Recommandations</h2>
        <ul>
            $($systemInfo.Recommendations)
        </ul>
    </div>
    
    <p><small>Rapport généré par le script de vérification de Paradis IA V2</small></p>
</body>
</html>
"@
    
    $htmlContent | Out-File -FilePath $reportPath -Encoding utf8
    return $reportPath
}

# Créer un objet pour stocker les informations du système
$systemInfo = @{
    Date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    CompatibilityLevel = "minimal"
    CompatibilityLevelText = "Minimal"
    SummaryText = "Analyse en cours..."
    OS = "Inconnu"
    OSStatus = "warning"
    OSStatusText = "À vérifier"
    CPU = "Inconnu"
    CPUStatus = "warning"
    CPUStatusText = "À vérifier"
    GPU = "Inconnu"
    GPUStatus = "warning"
    GPUStatusText = "À vérifier"
    RAM = 0
    RAMStatus = "warning"
    RAMStatusText = "À vérifier"
    Disk = 0
    DiskStatus = "warning"
    DiskStatusText = "À vérifier"
    NVDriver = "Non détecté"
    NVDriverStatus = "warning"
    NVDriverStatusText = "À vérifier"
    CUDA = "Non détecté"
    CUDAStatus = "warning"
    CUDAStatusText = "À vérifier"
    cuDNN = "Non détecté"
    cuDNNStatus = "warning"
    cuDNNStatusText = "À vérifier"
    Recommendations = "<li>Initialisation des recommandations...</li>"
}

# Variables pour stocker les recommandations
$recommendations = @()

# 1. Vérifier le système d'exploitation
Write-Host "`n🖥️ Vérification du système d'exploitation..." -ForegroundColor Cyan
$osInfo = Get-CimInstance Win32_OperatingSystem
$osCaption = $osInfo.Caption
$osBuild = $osInfo.BuildNumber
$osArch = $osInfo.OSArchitecture

$systemInfo.OS = "$osCaption (Build $osBuild, $osArch)"

# Vérifier si Windows 10/11
if ($osCaption -match "Windows 11") {
    $systemInfo.OSStatus = "success"
    $systemInfo.OSStatusText = "Optimal"
    Write-Host "✅ Système d'exploitation: $osCaption (Optimal)" -ForegroundColor Green
}
elseif ($osCaption -match "Windows 10") {
    $systemInfo.OSStatus = "success"
    $systemInfo.OSStatusText = "Compatible"
    Write-Host "✅ Système d'exploitation: $osCaption (Compatible)" -ForegroundColor Green
}
else {
    $systemInfo.OSStatus = "warning"
    $systemInfo.OSStatusText = "Potentiellement incompatible"
    $recommendations += "<li>Envisagez de passer à Windows 10 ou 11 pour une compatibilité optimale avec les bibliothèques IA.</li>"
    Write-Host "⚠️ Système d'exploitation: $osCaption (Compatibilité non garantie)" -ForegroundColor Yellow
}

# 2. Vérifier le CPU
Write-Host "`n🔄 Vérification du processeur..." -ForegroundColor Cyan
$cpuInfo = Get-CimInstance Win32_Processor
$cpuName = $cpuInfo.Name
$cpuCores = $cpuInfo.NumberOfCores
$cpuLogicalProcessors = $cpuInfo.NumberOfLogicalProcessors

$systemInfo.CPU = "$cpuName ($cpuCores cœurs, $cpuLogicalProcessors threads)"

if ($cpuCores -ge 8) {
    $systemInfo.CPUStatus = "success"
    $systemInfo.CPUStatusText = "Optimal"
    Write-Host "✅ Processeur: $cpuName" -ForegroundColor Green
    Write-Host "   $cpuCores cœurs, $cpuLogicalProcessors threads (Optimal)" -ForegroundColor Green
}
elseif ($cpuCores -ge 4) {
    $systemInfo.CPUStatus = "success"
    $systemInfo.CPUStatusText = "Compatible"
    Write-Host "✅ Processeur: $cpuName" -ForegroundColor Green
    Write-Host "   $cpuCores cœurs, $cpuLogicalProcessors threads (Compatible)" -ForegroundColor Green
}
else {
    $systemInfo.CPUStatus = "warning"
    $systemInfo.CPUStatusText = "Performances limitées"
    $recommendations += "<li>Votre CPU dispose de peu de cœurs ($cpuCores). Les modèles les plus légers sont recommandés.</li>"
    Write-Host "⚠️ Processeur: $cpuName" -ForegroundColor Yellow
    Write-Host "   $cpuCores cœurs, $cpuLogicalProcessors threads (Performances potentiellement limitées)" -ForegroundColor Yellow
}

# 3. Vérifier la carte graphique
Write-Host "`n🎮 Vérification de la carte graphique..." -ForegroundColor Cyan
try {
    $gpuInfo = nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
    
    if ($gpuInfo) {
        $gpuParts = $gpuInfo.Split(",").Trim()
        $gpuName = $gpuParts[0]
        $gpuMemory = [math]::Round([int]($gpuParts[1].Split(" ")[0]) / 1024)
        $gpuDriver = $gpuParts[2]
        
        $systemInfo.GPU = "$gpuName ($gpuMemory Go)"
        $systemInfo.NVDriver = $gpuDriver
        
        # Vérifier si c'est une RTX 4060 ou équivalent/supérieur
        if ($gpuName -match "RTX 40|RTX 30|RTX A|Tesla|A100|H100") {
            $systemInfo.GPUStatus = "success"
            $systemInfo.GPUStatusText = "Optimal"
            $systemInfo.NVDriverStatus = "success"
            $systemInfo.NVDriverStatusText = "Détecté ($gpuDriver)"
            Write-Host "✅ GPU: $gpuName ($gpuMemory Go) - Optimal pour Paradis IA" -ForegroundColor Green
            Write-Host "   Pilote NVIDIA: $gpuDriver" -ForegroundColor Green
        }
        elseif ($gpuName -match "RTX 20|GTX 16|GTX 1[6-9]") {
            $systemInfo.GPUStatus = "success"
            $systemInfo.GPUStatusText = "Compatible"
            $systemInfo.NVDriverStatus = "success"
            $systemInfo.NVDriverStatusText = "Détecté ($gpuDriver)"
            $recommendations += "<li>Votre GPU ($gpuName) est compatible mais des ajustements de quantification peuvent être nécessaires pour les grands modèles.</li>"
            Write-Host "✅ GPU: $gpuName ($gpuMemory Go) - Compatible avec Paradis IA" -ForegroundColor Green
            Write-Host "   Pilote NVIDIA: $gpuDriver" -ForegroundColor Green
        }
        else {
            $systemInfo.GPUStatus = "warning"
            $systemInfo.GPUStatusText = "Limité"
            $systemInfo.NVDriverStatus = "success"
            $systemInfo.NVDriverStatusText = "Détecté ($gpuDriver)"
            $recommendations += "<li>Votre GPU ($gpuName) a des capacités limitées pour l'IA. Utilisez des modèles quantifiés et plus légers.</li>"
            Write-Host "⚠️ GPU: $gpuName ($gpuMemory Go) - Capacités limitées pour l'IA" -ForegroundColor Yellow
            Write-Host "   Pilote NVIDIA: $gpuDriver" -ForegroundColor Green
        }
        
        # Vérifier la version du pilote
        if ([version]$gpuDriver -lt [version]"530.0") {
            $systemInfo.NVDriverStatus = "warning"
            $systemInfo.NVDriverStatusText = "Mise à jour recommandée"
            $recommendations += "<li>Mettez à jour vos pilotes NVIDIA (actuellement $gpuDriver) vers la version 530+ pour de meilleures performances.</li>"
            Write-Host "⚠️ Version du pilote NVIDIA ($gpuDriver) antérieure à 530. Mise à jour recommandée." -ForegroundColor Yellow
        }
    } else {
        throw "Impossible de détecter les informations GPU"
    }
}
catch {
    $systemInfo.GPU = "Aucun GPU NVIDIA détecté"
    $systemInfo.GPUStatus = "error"
    $systemInfo.GPUStatusText = "Non compatible"
    $systemInfo.NVDriverStatus = "error"
    $systemInfo.NVDriverStatusText = "Non détecté"
    $recommendations += "<li>Aucun GPU NVIDIA détecté. L'accélération GPU ne sera pas disponible, ce qui limitera fortement les performances.</li>"
    
    # Essayer de détecter toute carte graphique
    $displayAdapter = Get-CimInstance Win32_VideoController
    
    if ($displayAdapter) {
        $gpuName = $displayAdapter.Name
        $systemInfo.GPU = "$gpuName (Non NVIDIA)"
        Write-Host "❌ GPU: $gpuName - Non NVIDIA, incompatible avec l'accélération CUDA" -ForegroundColor Red
    } else {
        Write-Host "❌ GPU: Aucun GPU détecté" -ForegroundColor Red
    }
    
    Write-Host "❌ Pilotes NVIDIA: Non détectés" -ForegroundColor Red
}

# 4. Vérifier la RAM
Write-Host "`n🧠 Vérification de la mémoire RAM..." -ForegroundColor Cyan
$ramInfo = Get-CimInstance Win32_ComputerSystem
$ramTotalGB = [math]::Round($ramInfo.TotalPhysicalMemory / 1GB, 2)

$systemInfo.RAM = $ramTotalGB

if ($ramTotalGB -ge 32) {
    $systemInfo.RAMStatus = "success"
    $systemInfo.RAMStatusText = "Optimal"
    Write-Host "✅ Mémoire RAM: $ramTotalGB Go (Optimal)" -ForegroundColor Green
}
elseif ($ramTotalGB -ge 16) {
    $systemInfo.RAMStatus = "success"
    $systemInfo.RAMStatusText = "Compatible"
    $recommendations += "<li>Votre système dispose de $ramTotalGB Go de RAM. Certains modèles plus grands pourraient être limités.</li>"
    Write-Host "✅ Mémoire RAM: $ramTotalGB Go (Compatible)" -ForegroundColor Green
}
else {
    $systemInfo.RAMStatus = "warning"
    $systemInfo.RAMStatusText = "Limitée"
    $recommendations += "<li>Votre système ne dispose que de $ramTotalGB Go de RAM. Limitez-vous aux modèles légers et à une seule instance à la fois.</li>"
    Write-Host "⚠️ Mémoire RAM: $ramTotalGB Go (Limitée pour certains modèles)" -ForegroundColor Yellow
}

# 5. Vérifier l'espace disque
Write-Host "`n💾 Vérification de l'espace disque..." -ForegroundColor Cyan
$diskInfo = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
$diskFreeGB = [math]::Round($diskInfo.FreeSpace / 1GB, 2)

$systemInfo.Disk = $diskFreeGB

if ($diskFreeGB -ge 100) {
    $systemInfo.DiskStatus = "success"
    $systemInfo.DiskStatusText = "Optimal"
    Write-Host "✅ Espace disque disponible: $diskFreeGB Go (Optimal)" -ForegroundColor Green
}
elseif ($diskFreeGB -ge 50) {
    $systemInfo.DiskStatus = "success"
    $systemInfo.DiskStatusText = "Compatible"
    Write-Host "✅ Espace disque disponible: $diskFreeGB Go (Compatible)" -ForegroundColor Green
}
else {
    $systemInfo.DiskStatus = "warning"
    $systemInfo.DiskStatusText = "Limité"
    $recommendations += "<li>Vous n'avez que $diskFreeGB Go d'espace libre. Libérez de l'espace ou installez sur un autre disque.</li>"
    Write-Host "⚠️ Espace disque disponible: $diskFreeGB Go (Possiblement insuffisant)" -ForegroundColor Yellow
}

# 6. Vérifier CUDA
Write-Host "`n⚡ Vérification de l'installation CUDA..." -ForegroundColor Cyan
$cudaInstalled = Test-Path "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"

if ($cudaInstalled) {
    try {
        $nvccOutput = nvcc --version
        $cudaVersion = [regex]::Match($nvccOutput, "release (\d+\.\d+)").Groups[1].Value
        
        $systemInfo.CUDA = "Version $cudaVersion"
        
        if ([version]$cudaVersion -ge [version]"11.8") {
            $systemInfo.CUDAStatus = "success"
            $systemInfo.CUDAStatusText = "Installé ($cudaVersion)"
            Write-Host "✅ CUDA Toolkit: Version $cudaVersion (Compatible)" -ForegroundColor Green
        } else {
            $systemInfo.CUDAStatus = "warning"
            $systemInfo.CUDAStatusText = "Version obsolète"
            $recommendations += "<li>Votre version CUDA ($cudaVersion) est obsolète. Installez la version 11.8+ pour une compatibilité optimale.</li>"
            Write-Host "⚠️ CUDA Toolkit: Version $cudaVersion (Mise à jour recommandée vers 11.8+)" -ForegroundColor Yellow
        }
    } catch {
        $systemInfo.CUDA = "Installé (Version inconnue)"
        $systemInfo.CUDAStatus = "warning"
        $systemInfo.CUDAStatusText = "Version inconnue"
        $recommendations += "<li>CUDA semble être installé mais la version n'a pas pu être détectée. Vérifiez la configuration PATH.</li>"
        Write-Host "⚠️ CUDA Toolkit: Installé mais version non détectable" -ForegroundColor Yellow
    }
} else {
    $systemInfo.CUDA = "Non installé"
    $systemInfo.CUDAStatus = "error"
    $systemInfo.CUDAStatusText = "Non installé"
    $recommendations += "<li>CUDA n'est pas installé. Installez CUDA Toolkit 11.8+ pour activer l'accélération GPU.</li>"
    Write-Host "❌ CUDA Toolkit: Non installé" -ForegroundColor Red
}

# 7. Vérifier cuDNN (difficile à vérifier automatiquement)
Write-Host "`n🧩 Vérification de cuDNN..." -ForegroundColor Cyan
$potentialCuDNNPaths = @(
    "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v*\include\cudnn.h",
    "C:\Program Files\NVIDIA\CUDNN\v*\include\cudnn.h"
)

$cuDNNFound = $false
foreach ($path in $potentialCuDNNPaths) {
    if (Test-Path $path) {
        $cuDNNFound = $true
        break
    }
}

if ($cuDNNFound) {
    $systemInfo.cuDNN = "Installé"
    $systemInfo.cuDNNStatus = "success"
    $systemInfo.cuDNNStatusText = "Détecté"
    Write-Host "✅ cuDNN: Installé" -ForegroundColor Green
} else {
    $systemInfo.cuDNN = "Non détecté"
    $systemInfo.cuDNNStatus = "warning"
    $systemInfo.cuDNNStatusText = "Non détecté"
    $recommendations += "<li>cuDNN n'a pas été détecté. Il est recommandé pour des performances optimales avec les réseaux de neurones.</li>"
    Write-Host "⚠️ cuDNN: Non détecté (installation recommandée)" -ForegroundColor Yellow
}

# 8. Calculer le niveau de compatibilité global
$compatibilityScore = 0
$maxScore = 7

# OS
if ($systemInfo.OSStatus -eq "success") { $compatibilityScore++ }

# CPU
if ($systemInfo.CPUStatus -eq "success") { $compatibilityScore++ }

# GPU
if ($systemInfo.GPUStatus -eq "success") { $compatibilityScore++ }

# RAM
if ($systemInfo.RAMStatus -eq "success") { $compatibilityScore++ }

# Disk
if ($systemInfo.DiskStatus -eq "success") { $compatibilityScore++ }

# CUDA
if ($systemInfo.CUDAStatus -eq "success") { $compatibilityScore++ }

# cuDNN
if ($systemInfo.cuDNNStatus -eq "success") { $compatibilityScore++ }

# Déterminer le niveau global
$compatibilityPercent = [math]::Round(($compatibilityScore / $maxScore) * 100)

if ($compatibilityPercent -ge 80) {
    $systemInfo.CompatibilityLevel = "optimal"
    $systemInfo.CompatibilityLevelText = "Optimal ($compatibilityPercent%)"
    
    $systemInfo.SummaryText = "Votre système est parfaitement compatible avec Paradis IA V2. Vous pourrez exécuter tous les modèles d'IA sans limitation."
    
    Write-Host "`n✅ Compatibilité globale: OPTIMALE ($compatibilityPercent%)" -ForegroundColor Green
    Write-Host "Votre système est parfaitement adapté pour Paradis IA V2." -ForegroundColor Green
}
elseif ($compatibilityPercent -ge 60) {
    $systemInfo.CompatibilityLevel = "compatible"
    $systemInfo.CompatibilityLevelText = "Compatible ($compatibilityPercent%)"
    
    $systemInfo.SummaryText = "Votre système est compatible avec Paradis IA V2. Quelques ajustements peuvent être nécessaires pour optimiser les performances."
    
    Write-Host "`n✅ Compatibilité globale: COMPATIBLE ($compatibilityPercent%)" -ForegroundColor Green
    Write-Host "Votre système est compatible avec Paradis IA V2 avec quelques limitations." -ForegroundColor Green
}
else {
    $systemInfo.CompatibilityLevel = "minimal"
    $systemInfo.CompatibilityLevelText = "Limité ($compatibilityPercent%)"
    
    $systemInfo.SummaryText = "Votre système présente des limitations importantes pour Paradis IA V2. Des ajustements significatifs seront nécessaires."
    
    Write-Host "`n⚠️ Compatibilité globale: LIMITÉE ($compatibilityPercent%)" -ForegroundColor Yellow
    Write-Host "Votre système présente des limitations pour Paradis IA V2." -ForegroundColor Yellow
}

# 9. Afficher les recommandations
if ($recommendations.Count -gt 0) {
    Write-Host "`n📋 Recommandations:" -ForegroundColor Cyan
    
    $systemInfo.Recommendations = $recommendations -join "`n"
    
    foreach ($rec in $recommendations) {
        # Extraire le texte à l'intérieur des balises <li>
        $recText = $rec -replace "<li>|</li>", ""
        Write-Host "• $recText" -ForegroundColor Yellow
    }
} else {
    $systemInfo.Recommendations = "<li>Aucune recommandation spécifique - votre système est prêt pour Paradis IA V2.</li>"
    
    Write-Host "`n📋 Recommandations:" -ForegroundColor Cyan
    Write-Host "• Aucune recommandation spécifique - votre système est prêt pour Paradis IA V2." -ForegroundColor Green
}

# 10. Générer le rapport HTML
$reportPath = "..\rapport_compatibilite.html"
$fullReportPath = Create-HtmlReport -reportPath $reportPath -systemInfo $systemInfo

Write-Host "`n📊 Rapport généré: $fullReportPath" -ForegroundColor Cyan
Write-Host "Vous pouvez consulter ce rapport pour plus de détails et recommandations." -ForegroundColor Cyan

# 11. Mettre à jour le fichier de suivi des étapes
try {
    $trackingFile = "..\suivi_etapes_paradis_ia_v2.md"
    if (Test-Path $trackingFile) {
        $trackingContent = Get-Content $trackingFile -Raw
        
        # Mettre à jour le statut de la première étape
        $updatedContent = $trackingContent -replace "1. Vérification matériel \| À faire \|", "1. Vérification matériel | Complété |"
        
        # Ajouter la date de complétion
        $completionDate = Get-Date -Format "yyyy-MM-dd"
        $updatedContent = $updatedContent -replace "1. Vérification matériel \| Complété \| \|", "1. Vérification matériel | Complété | $completionDate |"
        
        $updatedContent | Out-File $trackingFile -Encoding utf8
        
        Write-Host "`n✅ Fichier de suivi mis à jour avec succès!" -ForegroundColor Green
    }
}
catch {
    Write-Host "`n⚠️ Impossible de mettre à jour le fichier de suivi: $_" -ForegroundColor Yellow
}

# Conclusion
Write-Host "`n🚀 Vérification système terminée!" -ForegroundColor Cyan
Write-Host "Vous pouvez maintenant procéder à l'installation de Paradis IA V2" -ForegroundColor Cyan
Write-Host "en suivant les recommandations adaptées à votre matériel." -ForegroundColor Cyan 