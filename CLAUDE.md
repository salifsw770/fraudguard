# FraudGuard — contexte pour Claude Code

## Le projet
Plateforme de détection de fraude sur les transactions mobile money.
Chaque transaction reçoit un score de risque ; au-dessus d'un seuil, une alerte est créée
et un agent bancaire la valide ou la bloque depuis un tableau de bord.
Projet portfolio destiné aux banques mauritaniennes : la sécurité, les tests et la clarté
du code comptent autant que les fonctionnalités.

Données : PaySim uniquement (transactions simulées). Jamais de données réelles.

## Périmètre (décisions du 11/11/2026, complètent le plan)
- `GET /api/stats` est accessible aux rôles AGENT et ADMIN (chiffres agrégés, sans donnée personnelle ni action).
- Gestion des utilisateurs depuis l'interface : **hors périmètre (version 2)**. En V1, un admin et un agent de démo
  sont créés au démarrage à partir de `.env` (`DEMO_ADMIN_*`, `DEMO_AGENT_*`), jamais via une migration Flyway.
- Autres éléments hors périmètre (V2) : détection de réseaux par graphes, application mobile, connexion à un vrai système bancaire.

## Architecture (monorepo)
```
backend/      API Spring Boot : transactions, alertes, sécurité, audit
frontend/     Angular : tableau de bord agent
ml-service/   Python : notebooks, modèle XGBoost + SHAP, API FastAPI
simulator/    envoie des transactions PaySim à l'API
docs/         architecture.md, adr/ (décisions), images/
```
Flux : simulateur → `POST /api/transactions` (Spring) → `POST /predict` (FastAPI)
→ alerte si score ≥ seuil → l'agent décide dans Angular.
Seul le backend appelle le service IA, la base et le LLM (réseau Docker interne).

## Stack
- Backend : Java 21, Spring Boot 3, Spring Security (JWT, rôles AGENT / ADMIN), Spring Data JPA,
  PostgreSQL, Flyway, Bean Validation, springdoc-openapi, JUnit 5, Mockito, Testcontainers
- Frontend : Angular (standalone components), Vitest, ESLint, Prettier
- IA : Python 3.11+, pandas, scikit-learn, XGBoost, LightGBM, SHAP, FastAPI, pytest, Ruff
- Explication des scores en 3 niveaux via l'interface `ExplicationProvider` :
  `TemplateProvider` (par défaut), `OllamaProvider`, `ApiProvider` — choisi par `EXPLICATION_MODE` dans `.env`
- Outils : Docker Compose, GitHub Actions, SonarCloud

## Conventions de code
### Backend — organisation par fonctionnalité
```
backend/src/main/java/mr/fraudguard/
  auth/  transaction/  alerte/  audit/  parametre/  scoring/  common/
```
Chaque fonctionnalité contient : `*Controller`, `*Service`, `*Repository`, `dto/`, `entity/`, `*Mapper`.
- Les contrôleurs ne contiennent pas de logique métier ; ils renvoient des DTO, jamais des entités.
- Injection par constructeur (pas de `@Autowired` sur les champs).
- Erreurs gérées par un `@RestControllerAdvice` dans `common/`, messages sans détail technique.
- Toute modification de schéma = une nouvelle migration Flyway `V<n>__description.sql` ; ne jamais modifier une migration existante.
- Chaque action sensible (décision sur une alerte, changement de seuil, connexion) écrit dans `audit_log`.

### Python
- Notebooks numérotés dans `ml-service/notebooks/` pour explorer ; le code réutilisable va dans `ml-service/app/` et il est testé.
- Découpage entraînement / test dans le temps (colonne `step`), jamais aléatoire.
- Métriques : PR-AUC, rappel, précision sur la classe fraude. Ne pas utiliser l'accuracy.
- Fichiers de données (`data/`) jamais commités.

### Angular
- Un dossier par fonctionnalité (`alertes/`, `auth/`, `dashboard/`), services pour les appels HTTP,
  intercepteur pour le JWT, guards pour les rôles.

## Sécurité (non négociable)
- Mots de passe hachés avec BCrypt ; JWT signé, expiration 15 min + refresh token.
- `@PreAuthorize` sur chaque endpoint sensible ; refus par défaut.
- Validation de toutes les entrées (`@Valid`) ; requêtes uniquement via JPA, jamais de SQL concaténé.
- Aucun secret dans le code : tout passe par `.env` (non commité) ; `.env.example` contient des valeurs factices.
- Si le service IA ne répond pas, la transaction passe en statut `A_VERIFIER`, elle n'est jamais perdue.

## Commandes (à compléter au fil du projet)
```
docker compose up --build                 # lance tout
cd backend && ./mvnw test                 # tests backend
cd frontend && npm test                   # tests frontend
cd ml-service && pytest                   # tests service IA
cd ml-service && uvicorn app.main:app --reload
```

## Git
- `main` est protégée : une branche par issue (`feat/12-scoring-api`, `fix/27-pagination`), fusion par pull request.
- Conventional Commits : `feat(alerte): ...`, `fix(auth): ...`, `test(scoring): ...`, `docs: ...`, `refactor: ...`, `ci: ...`
- Référencer l'issue : `Closes #12` dans la PR.

## Definition of Done
- Code sur sa branche, fusionné par PR, CI verte.
- Tests unitaires pour chaque nouveau service ou endpoint.
- Aucune nouvelle alerte critique SonarCloud.
- README / Swagger / ADR mis à jour si nécessaire.
- Aucun secret ni donnée réelle.

## Comment travailler avec moi
- Réponds en français, simplement.
- Pour une tâche importante : propose d'abord un plan court, attends ma validation, puis code.
- Travaille sur une issue à la fois ; écris les tests en même temps que le code et lance-les.
- Explique les choix techniques : je dois pouvoir les défendre en entretien.
- Si une information manque, pose la question au lieu d'inventer.
