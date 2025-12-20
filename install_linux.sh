#!/bin/bash

set -e 

if [ -d "venv" ]; then
    echo "L'environnement virtuel existe déjà."
else
    echo "Création de l'environnement virtuel..."
    sudo apt update
    sudo apt install -y python3-venv
    
    python3 -m venv venv
    echo "Installation des dépendances..."
    ./venv/bin/pip install -r requirements.txt
fi

echo "Succès de l'installation !"
echo "Vous pouvez commencer à travailler !"
echo "Pour lancer l'application, exécutez './lancer_app_linux.sh'"