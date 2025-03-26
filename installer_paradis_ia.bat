@echo off
color 0A
echo =====================================================
echo    INSTALLATION PARADIS IA V2 - HAUTE PERFORMANCE
echo =====================================================
echo Configuration cible: Windows 11, RTX 4060, 32-64 GB RAM
echo.
echo Ce script va lancer l'installation du Paradis IA V2
echo avec tous ses composants optimises pour GPU.
echo.
echo IMPORTANT: Ce script doit etre execute en tant qu'administrateur.
echo.
echo [0] Verifier la compatibilite materielle (recommande)
echo [1] Installation complete (environnement + CUDA/cuDNN)
echo [2] Installation de l'environnement uniquement
echo [3] Installation et configuration CUDA/cuDNN
echo [4] Installation des modeles IA
echo [5] Test de performance GPU
echo [6] Quitter
echo.
set /p choix="Votre choix [0-6]: "

if "%choix%"=="0" (
    echo.
    echo Verification du materiel...
    powershell -ExecutionPolicy Bypass -File scripts\verifier_systeme.ps1
    echo.
    echo Verification materielle terminee.
    echo Un rapport a ete genere dans rapport_compatibilite.html
    echo.
    pause
    cls
    %0
) else if "%choix%"=="1" (
    echo.
    echo Verification preliminaire du materiel...
    powershell -ExecutionPolicy Bypass -File scripts\verifier_systeme.ps1
    echo.
    echo Lancement de l'installation complete...
    powershell -ExecutionPolicy Bypass -File scripts\setup_environment.ps1
    powershell -ExecutionPolicy Bypass -File scripts\cuda_installer.ps1
) else if "%choix%"=="2" (
    echo.
    echo Installation de l'environnement uniquement...
    powershell -ExecutionPolicy Bypass -File scripts\setup_environment.ps1
) else if "%choix%"=="3" (
    echo.
    echo Installation et configuration CUDA/cuDNN...
    powershell -ExecutionPolicy Bypass -File scripts\cuda_installer.ps1
) else if "%choix%"=="4" (
    echo.
    echo Installation des modeles IA...
    powershell -ExecutionPolicy Bypass -File scripts\installer_modeles.ps1
) else if "%choix%"=="5" (
    echo.
    echo Lancement du test de performance GPU...
    powershell -ExecutionPolicy Bypass -File scripts\test_performance.ps1
) else if "%choix%"=="6" (
    echo.
    echo Au revoir!
    goto :eof
) else (
    echo.
    echo Choix invalide. Veuillez redemarrer le script.
    goto :eof
)

echo.
echo Installation terminee!
echo Consultez le fichier suivi_etapes_paradis_ia_v2.md pour les prochaines etapes.
echo.
pause 