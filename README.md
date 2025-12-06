# Projet_l2
🌱 WellBeing – Assistant Santé avec IA Locale (Ollama + LLava-Phi3)

WellBeing est une application Python permettant :

de gérer un profil utilisateur

de suivre un score de santé basé sur l’IMC, l’âge et l’activité

d’afficher un graphique d’évolution du score

d’analyser un repas à partir d’une image grâce à un modèle d’IA locale (LLava-Phi3 via Ollama)

L’application fonctionne entièrement en local grâce à Ollama, aucun envoi de données sur Internet.

Installation Prérequis :
✔ Python 3.9+
✔ MySQL installé

Crée une base nommée wellbeing (elle sera auto-remplie).

✔ Ollama installé

Télécharger ici : https://ollama.com/download

Vérifier qu’il fonctionne :

ollama --version

Installation automatique (Windows)

Un fichier setup.bat est fourni pour faciliter l’installation.

Double-clique simplement sur :

setup.bat


Il va :

installer les dépendances Python

télécharger le modèle IA

préparer l’environnement

Installation manuelle

Si vous préférez installer vous-même :

1️) Installer les librairies Python
pip install -r requirements.txt

2️) Télécharger le modèle IA
ollama pull llava-phi3

 Lancer l’application
--> python wellbeing.py


L’interface graphique CustomTkinter va s’ouvrir automatiquement.

Fonctionnement de l’IA

Le projet utilise le modèle LLava-Phi3 pour analyser des images d’aliments.

Pourquoi Ollama ?

Exécution 100% locale

Pas besoin d’API externe (pas de clé API)

Plus rapide après installation

Idéal pour un projet scolaire (fonctionne sans Internet)

Pourquoi WSL (si Windows) ?

Sur Windows, certains modèles ont besoin d’un environnement Linux pour fonctionner correctement.
Ollama utilise WSL2 en arrière-plan pour charger certains modèles.

Fonctionnalités principales
✔ Profil utilisateur

âge, poids, taille, genre, activité

mise à jour en temps réel

✔ Score santé

Calcul basé sur IMC + âge + activité
Affichage :

smiley dynamique

couleur selon le niveau

score /100

✔ Graphique d’historique

Barres colorées selon la qualité du score.

✔ Analyse d’image (IA)

détecte les aliments

estime les calories

donne un conseil nutritionnel

réponse structurée en JSON

 Structure du projet
WellBeing/
│
├── wellbeing.py           # Point d'entrée principal
├── interface.py           # Page de connexion / création compte
├── interface_acc.py       # Dashboard après connexion
├── utils.py               # IA, MySQL, calcul santé, outils
│
├── requirements.txt       # Dépendances Python
├── setup.bat              # Installation rapide
└── README.md              # Ce fichier

🎓 Destiné aux enseignants / évaluateurs

✔ IA locale → aucune donnée envoyée en ligne
✔ Code clair et documenté
✔ Interface graphique professionnelle
✔ Fonctionne sur n’importe quel PC Windows avec Ollama installé



Projet développé par Malika et Naila, étudiant MIASHS – MIAGE.
