@echo off

if exist "venv\" (
    echo L'environnement virtuel existe deja.
) else (
    echo Creation de l'environnement virtuel...
    python -m venv venv
    
    echo Installation des dependances...
    venv\Scripts\pip install -r requirements.txt
)

echo.
echo Succès de l'installation !
echo Vous pouvez commencer a travailler.
echo Pour lancer l'application, éxécutez le fichier './lancer_app_windows.bat'
pause