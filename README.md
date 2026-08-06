# 🛰️ Dashboard Réseau

Un outil de surveillance réseau local qui détecte les appareils connectés à ton wifi, garde un historique des scans, et signale les connexions inhabituelles.

## Fonctionnalités

- **Détection automatique du réseau** — plus besoin de préciser manuellement le sous-réseau, il est déduit automatiquement de ta connexion actuelle
- **Scan des appareils connectés** — combine un ping sweep (pour forcer les appareils actifs à répondre) et une lecture de la table ARP de Windows
- **Historique persistant** — chaque scan est sauvegardé dans `historique.json`
- **Détection des nouveaux appareils** — repère tout appareil jamais vu dans l'historique
- **Détection des connexions suspectes** — un appareil est marqué "suspect" s'il est à la fois nouveau ET détecté pendant une plage horaire inhabituelle (minuit-6h par défaut)
- **Interface web** — dashboard sombre et stylé, avec déclenchement manuel du scan via un bouton

## Comment ça fonctionne

1. Un ping est envoyé à toutes les adresses du sous-réseau local (ex: `192.168.100.1` à `192.168.100.254`)
2. Chaque appareil actif répond, ce qui peuple automatiquement la table ARP de Windows
3. Le script lit cette table ARP et en extrait IP + adresse MAC de chaque appareil
4. Chaque adresse MAC est comparée à l'historique pour déterminer si l'appareil est connu, nouveau, ou suspect

Cette méthode ne nécessite **aucun droit administrateur** ni de permissions réseau bas niveau (contrairement à un scan ARP actif classique, qui peut être bloqué par le pare-feu Windows).

## Technologies utilisées

- **Python** — scan réseau, logique de détection
- **Flask** — serveur web / interface
- **JSON** — stockage de l'historique (pas de base de données pour l'instant)
- **HTML / CSS / Jinja2** — interface, thème sombre avec Chart-like data en monospace

## Structure du projet

Projet_dashboard_réseau/
├── app.py # serveur Flask, routes / et /scan
├── scan.py # détection du sous-réseau, ping sweep, lecture ARP
├── alerte.py # logique de détection (nouveaux appareils, heure inhabituelle)
├── stockage.py # sauvegarde/lecture de l'historique JSON
├── historique.json # historique des scans (généré automatiquement)
├── templates/
│ └── index.html # page principale
└── static/
└── style.css # thème visuel


## Prérequis

- Python 3
- Flask (`pip install flask`)

## Installation et lancement

1. Clone ce repo :

git clone https://github.com/Frisnelle/Dashboard_reseau.git

2. Installe les dépendances :

pip install flask

3. Lance le serveur :

python app.py

4. Ouvre `http://127.0.0.1:5000` dans ton navigateur

## Utilisation

- La page principale affiche les appareils du dernier scan effectué
- Clique sur **"Scanner maintenant"** pour lancer un nouveau scan et mettre à jour la liste
- Un appareil jamais vu avant apparaît avec un badge **"Nouveau"**
- Un appareil jamais vu ET détecté entre minuit et 6h apparaît avec un badge **"Suspect"**

## Limitations connues

- Ne scanne que le réseau local auquel le PC est actuellement connecté
- Pas de scan automatique en arrière-plan — le déclenchement est manuel (via le bouton ou `python scan.py`)
- La plage horaire "inhabituelle" est une valeur fixe (minuit-6h), pas encore personnalisable depuis l'interface

## Pistes d'amélioration futures

- Scan automatique périodique en tâche de fond
- Historique visuel (graphique de l'évolution du nombre d'appareils dans le temps)
- Identification du fabricant à partir de l'adresse MAC (lookup OUI)

## Auteur

Frisnelle