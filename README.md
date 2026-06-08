# SecureVault -  un coffre-fort local sécurisé pour la gestion de mots de passe 
8INF874 -Cryptographie – Été 2026

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey)

SecureVault est une application de sécurité avancée démontrant le chiffrement AES-256 et l'intégrité des données via SHA-256. Projet pédagogique pour illustrer les concepts cryptographiques fondamentaux.

## ✨ Fonctionnalités

- 🔐 **Chiffrement/Déchiffrement AES-256-CBC** pour fichiers sensibles
- 🔑 **Démonstration d'intégrité** avec comparaison de hash SHA-256
- 👥 **Gestion utilisateur sécurisée** (stockage hashé + salt)
- 🛡️ **Détection automatique d'altération** des fichiers
- 💻 **Interface moderne** avec CustomTkinter

## 🎯 Démonstration clé

L'application prouve deux concepts fondamentaux :

1. **Aucun mot de passe en clair** : Stockage via hash + salt
2. **Détection d'altération** : Modification d'un fichier → Hash différent → Alerte

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

## 🚀 Installation rapide

```bash
# Cloner le dépôt
git clone https://github.com/votre-username/SecureVault.git
cd SecureVault

# Installer les dépendances
pip install customtkinter pycryptodome pillow

# Lancer l'application
python securevault.py
