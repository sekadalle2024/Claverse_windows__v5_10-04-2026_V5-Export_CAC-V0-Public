@echo off
REM Script de deploiement Netlify en un clic
REM Double-cliquez sur ce fichier pour deployer

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   DEPLOIEMENT NETLIFY - CLARAVERSE
echo ========================================
echo.

REM Vérifier que PowerShell est disponible
where powershell >nul 2>&1
if errorlevel 1 (
    echo ERREUR: PowerShell n'est pas disponible
    pause
    exit /b 1
)

REM Aller dans le dossier deploiement-netlify
cd deploiement-netlify

REM Exécuter le script de déploiement
powershell -NoProfile -ExecutionPolicy Bypass -File "deploy.ps1" -Message "Redeploiement - %date% %time%"

REM Pause pour voir le résultat
pause

exit /b %errorlevel%
