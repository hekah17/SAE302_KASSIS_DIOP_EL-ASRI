@echo off
echo Lancement du serveur...

if not exist "venv\" (
    echo L'environnement n'est pas installe !
    echo Veuillez d'abord lancer 'install_windows.bat'
    pause
    exit /b
)

venv\Scripts\python serveur.py

pause