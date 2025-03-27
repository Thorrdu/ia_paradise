@echo off
SETLOCAL

REM Définir le chemin vers Python explicitement
SET PYTHON_PATH=C:\Users\utilisateur\AppData\Local\Programs\Python\Python312\python.exe

echo ===== Interface Web Paradis IA =====
echo.

REM Vérifier si Python existe au chemin spécifié
IF EXIST "%PYTHON_PATH%" (
    echo Python trouvé: %PYTHON_PATH%
) ELSE (
    echo Python non trouvé au chemin spécifié.
    echo Essai avec la commande Python standard...
    WHERE python >nul 2>nul
    IF %ERRORLEVEL% EQU 0 (
        SET PYTHON_PATH=python
        echo Python trouvé dans le PATH système.
    ) ELSE (
        echo ERREUR: Python n'est pas accessible.
        echo Veuillez installer Python ou corriger le chemin dans ce script.
        pause
        exit /b 1
    )
)

echo.
echo Lancement de l'interface web...
echo.

REM Lancer l'interface web
"%PYTHON_PATH%" start_web_interface.py

REM Si l'exécution échoue, essayer avec py
IF %ERRORLEVEL% NEQ 0 (
    echo Tentative avec la commande py...
    py start_web_interface.py
)

pause 