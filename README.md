# FraudGuard

Détection de fraude en temps réel sur les transactions mobile money.
Chaque transaction reçoit un score de risque expliqué en une phrase claire ; un agent bancaire valide ou bloque les transactions suspectes depuis un tableau de bord.

[![ml](https://github.com/salifsw770/fraudguard/actions/workflows/ml.yml/badge.svg)](https://github.com/salifsw770/fraudguard/actions/workflows/ml.yml)

> **Statut :** sprint 1 en cours : données et modèle (release cible `v0.1.0`).

## Architecture

| Service | Technologie | Rôle |
|---|---|---|
| `backend/` | Java 21, Spring Boot 3, Spring Security (JWT), PostgreSQL, Flyway | Transactions, alertes, sécurité, audit |
| `frontend/` | Angular | Tableau de bord agent et administrateur |
| `ml-service/` | Python, XGBoost, SHAP, FastAPI | Score de risque et 3 facteurs explicatifs |
| `simulator/` | Python | Envoie des transactions PaySim à l'API |

Parcours : simulateur → `POST /api/transactions` → `POST /predict` → alerte si score ≥ seuil → décision de l'agent.
Le service IA, la base et le LLM ne sont jamais exposés à l'extérieur.

## Données

Uniquement des données simulées : [PaySim](https://www.kaggle.com/datasets/ealaxi/paysim1) (6,3 millions de transactions mobile money).
Aucune donnée client réelle. Le fichier brut n'est pas versionné.

## Hors périmètre (version 2)

- Détection de réseaux de fraudeurs par graphes
- Gestion des utilisateurs depuis l'interface (en V1 : un admin et un agent de démo créés au démarrage)
- Application mobile
- Connexion à un vrai système bancaire

## Lancement

À venir (sprint 4) : `docker compose up --build`, en une seule commande.

## Résultats du modèle

À venir (fin du sprint 1).

## Méthode

Scrum en solo : 4 sprints de 2 semaines, GitHub Projects, Conventional Commits, une pull request par issue.
Voir [CLAUDE.md](CLAUDE.md) pour les conventions et la Definition of Done, et [JOURNAL.md](JOURNAL.md) pour le suivi quotidien.

## Outils utilisés

Développement assisté par Claude (conception, revue de code, documentation). Chaque ligne fusionnée est relue, testée et comprise.
