@echo off
title Installation automatique de Ollama pour WellBeing
color 0A

echo ===============================================
echo     INSTALLATION AUTOMATIQUE WELLBEING IA
echo ===============================================
echo.

REM ————————————————————————————————
REM 1) Vérifier si WSL est installé
REM ————————————————————————————————
echo 🔍 Vérification WSL...
wsl --status >nul 2>&1
if %errorlevel% neq 0 (
    echo ❗ WSL n'est pas installé. Installation en cours...
    wsl --install
    echo ✅ WSL installé. Veuillez redémarrer votre PC puis relancer ce fichier.
    pause
    exit /b
)

echo ✅ WSL déjà installé.
echo.

REM ————————————————————————————————
REM 2) Vérifier si Ubuntu existe
REM ————————————————————————————————
echo 🔍 Vérification Ubuntu...
wsl -l -v | find "Ubuntu" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❗ Ubuntu non trouvé. Installation...
    wsl --install -d Ubuntu
    echo ✅ Ubuntu installé. Veuillez redémarrer votre PC puis relancer ce fichier.
    pause
    exit /b
)

echo ✅ Ubuntu disponible.
echo.

REM ————————————————————————————————
REM 3) Installer Ollama dans WSL
REM ————————————————————————————————
echo 🔧 Installation de Ollama dans WSL...
wsl -d Ubuntu -e sh -c "curl -fsSL https://ollama.com/install.sh | sh"

echo ✅ Ollama installé dans Ubuntu.
echo.

REM ————————————————————————————————
REM 4) Télécharger le modèle IA
REM ————————————————————————————————
echo 📥 Téléchargement du modèle Vision...
wsl -d Ubuntu -e ollama pull llava-phi3:latest

echo ✅ Modèle téléchargé !
echo.

REM ————————————————————————————————
REM 5) Lancer Ollama en arrière-plan
REM ————————————————————————————————
echo 🚀 Lancement du serveur Ollama...
start wsl -d Ubuntu -e ollama serve

echo ===============================================
echo   🎉 Installation terminée ! 
echo   Vous pouvez maintenant lancer WellBeing.
echo ===============================================

pause
exit /b

