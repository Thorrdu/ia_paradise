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
"Système: Windows 11, RTX 4060, $(Get-WmiObject Win32_ComputerSystem | Select-Object -ExpandProperty TotalPhysicalMemory) / 1GB GB RAM" | Out-File -FilePath $outputFile -Append
"`n" | Out-File -FilePath $outputFile -Append

# Vérifier quels modèles sont disponibles
$availableModels = ollama list
$models = @()

# Ajouter les modèles disponibles au test
if ($availableModels -match "mixtral-optimized") {
    $models += @{Name = "Mixtral 8x7B (Optimisé)"; Param = "mixtral-optimized"}
}
if ($availableModels -match "dolphin-mixtral") {
    $models += @{Name = "Dolphin Mixtral"; Param = "dolphin-mixtral"}
}
if ($availableModels -match "codellama:34b-instruct") {
    $models += @{Name = "CodeLlama 34B"; Param = "codellama:34b-instruct-q5_K_M"}
}
if ($availableModels -match "deepseek-coder:33b-instruct") {
    $models += @{Name = "DeepSeek Coder 33B"; Param = "deepseek-coder:33b-instruct-q5_K_M"}
}
if ($availableModels -match "phi3:mini") {
    $models += @{Name = "Phi-3 Mini"; Param = "phi3:mini"}
}

# Si aucun modèle trouvé, informer l'utilisateur
if ($models.Count -eq 0) {
    Write-Host "❌ Aucun modèle disponible pour les tests. Veuillez d'abord installer des modèles." -ForegroundColor Red
    Exit
}

# Tester tous les modèles disponibles
$results = @()
foreach ($model in $models) {
    $results += Test-Model -modelName $model.Name -modelParam $model.Param
}

# Générer un résumé
"=== RÉSUMÉ DES PERFORMANCES ===" | Out-File -FilePath $outputFile -Append
$results | Sort-Object Duration | ForEach-Object {
    "$($_.Model): $($_.Duration) secondes, $($_.ResponseLength) caractères" | Out-File -FilePath $outputFile -Append
}

# Information sur le GPU
try {
    $gpuInfo = nvidia-smi --query-gpu=name,memory.used,memory.total,temperature.gpu --format=csv,noheader
    "`nINFORMATIONS GPU:" | Out-File -FilePath $outputFile -Append
    $gpuInfo | Out-File -FilePath $outputFile -Append
} catch {
    "`nImpossible d'obtenir les informations GPU" | Out-File -FilePath $outputFile -Append
}

Write-Host "✅ Rapport de performance généré dans $outputFile" -ForegroundColor Green
Write-Host "📄 Ouverture du rapport..." -ForegroundColor Cyan
notepad $outputFile 