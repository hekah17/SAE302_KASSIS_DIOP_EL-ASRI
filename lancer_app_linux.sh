#!/bin/bash
set -e

if [ ! -d "venv" ]; then
    echo "Erreur : L'environnement virtuel n'existe pas."
    echo "Veuillez d'abord lancer './install_linux.sh'"
    exit 1
fi

echo "Lancement du serveur..."

./venv/bin/python serveur.py