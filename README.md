# SecureVault -  un coffre-fort local sécurisé pour la gestion de mots de passe 
8INF874 -Cryptographie – Été 2026

SecureVault est un outil de sécurité avancé démontrant le chiffrement AES-256 et l'intégrité des données via SHA-256. Projet pédagogique pour illustrer les concepts cryptographiques fondamentaux.

##  Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| **Coffre sécurisé** | Protection par mot de passe maître (jamais stocké en clair) |
| **Ajout de mots de passe** | Stockage chiffré des identifiants par site/service |
| **Affichage masqué** | Visualisation avec bouton œil (masqué par défaut) |
| **Copie rapide** | Copie des mots de passe dans le presse-papier |
| **Générateur intégré** | Mots de passe robustes (94 caractères possibles) |
| **Recherche** | Filtrage par nom de site/service |
| **Suppression** | Gestion complète des entrées |
| **Détection corruption** | Tag GCM vérifie l'intégrité des données |
| **Analyse sécurité** | Panneau détaillé des résistances et performances |

## Démonstration clé

L'application prouve deux concepts fondamentaux :

1. **Aucun mot de passe en clair** : Stockage via hash + salt
2. **Détection d'altération** : Modification d'un fichier → Hash différent → Alerte

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

## Installation rapide

```bash
# Cloner le dépôt
git clone https://github.com/Fullabba/SecureVault.git
cd SecureVault

# Installer les dépendances
pip install customtkinter pycryptodome pillow

# Lancer l'application
python securevault.py
