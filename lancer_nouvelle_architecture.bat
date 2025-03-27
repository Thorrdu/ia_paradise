@echo off
setlocal enabledelayedexpansion

echo ===== Paradis IA - Nouvelle Architecture =====
echo.

REM Utiliser py au lieu d'un chemin absolu pour Python
set PYTHON_EXE=py
set PIP_EXE=py -m pip

REM Vérifier si Python est installé
where %PYTHON_EXE% >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERREUR] Python n'est pas trouvé avec la commande %PYTHON_EXE%
    echo         Installez Python depuis https://www.python.org/downloads/
    exit /b 1
)

REM Vérifier si Ollama est installé
where ollama >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERREUR] Ollama n'est pas installé ou n'est pas dans le PATH.
    echo         Installez Ollama depuis https://ollama.com/download/windows
    exit /b 1
)

REM Créer des répertoires nécessaires s'ils n'existent pas
if not exist "memory\data" mkdir memory\data
if not exist "logs" mkdir logs
if not exist "web\logs" mkdir web\logs
if not exist "web\static" mkdir web\static
if not exist "web\templates" mkdir web\templates

REM Vérifier si le dossier d'environnement virtuel existe
if not exist "venv" (
    echo Création d'un environnement virtuel Python...
    %PYTHON_EXE% -m venv venv
    
    echo Installation des dépendances...
    call venv\Scripts\activate.bat
    %PIP_EXE% install flask flask-cors requests psutil
    echo.
) else (
    call venv\Scripts\activate.bat
)

REM Vérifier si ollama est déjà en cours d'exécution
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [INFO] Ollama est déjà en cours d'exécution.
) else (
    echo [INFO] Démarrage d'Ollama...
    start "" ollama serve
    timeout /t 5 /nobreak >nul
)

REM Vérifier les modèles requis
echo [INFO] Vérification des modèles Ollama...

echo - Vérification de mixtral...
ollama list | findstr "mixtral" >nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] Téléchargement du modèle mixtral. Cette opération peut prendre du temps...
    start /wait ollama pull mixtral
)

echo - Vérification de deepseek-coder...
ollama list | findstr "deepseek-coder" >nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] Le modèle deepseek-coder n'est pas installé.
    echo [INFO] Vous pouvez l'installer manuellement avec: ollama pull deepseek-coder
)

echo.
echo [INFO] Lancement du test de la nouvelle architecture...
echo.

%PYTHON_EXE% test_new_architecture.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [AVERTISSEMENT] Certains tests ont échoué. L'application pourrait fonctionner en mode limité.
    echo.
)

echo.
echo [INFO] Démarrage du serveur web...
echo.
echo Accédez à l'interface à l'adresse: http://localhost:5000
echo.
echo Appuyez sur Ctrl+C pour arrêter le serveur.
echo.

%PYTHON_EXE% web/app.py

endlocal 