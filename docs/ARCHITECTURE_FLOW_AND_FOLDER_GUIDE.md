# Architecture Flow & Root Folders Guide

This file describes the backend architecture flow for StackWise-Flet and explains the purpose of the project's core root folders so you can concisely explain them during a presentation or defense.

## Architecture Flow (high level)

Flet UI / Pages
→ Controllers
→ Services (Business Logic)
→ Repositories
→ Database (MySQL)
→ Response back to UI

Notes:
- UI: collects user input and displays results.
- Controllers: validate and translate UI input, call services, manage navigation and session state.
- Services: contain core business logic (recommendation scoring, AI orchestration, explanation generation).
- Repositories: SQL and persistence operations; return domain model objects.
- Database: MySQL handled via `DatabaseService` with migrations and seeders.

### Architecture Diagram

```mermaid
flowchart LR
  UI[Flet UI / Pages] --> CTRL[Controllers]
  CTRL --> SVC[Services (business logic)]
  SVC --> REP[Repositories (persistence)]
  REP --> DB[(MySQL via DatabaseService)]
  SVC --> AI[AI / Ollama Services]
  AI --> SVC
  CORE[Core (router & container)] --> CTRL
  UI --> UIComp[UI Components]
  CTRL --> SESSION[Session & Navigation]
  SESSION --> UI
```

## How a typical request flows

1. User completes a form in the UI (e.g. Recommendation form).
2. UI calls a controller handler (e.g. `on_generate` in `app/controllers/recommendation_controller.py`).
3. The controller maps form data to an engine request and calls the service entry (e.g. `generate_recommendation_from_request`).
4. The service executes business logic (scoring, compatibility checks, alternatives) in `app/services/recommendation_service.py`.
5. If persistence is needed, the service or a persistence helper calls a repository function (e.g. `RecommendationRepository.create`).
6. Repository uses `DatabaseService` to execute SQL against MySQL.
7. Controller receives service result, stores session values, and navigates to the result page which reads saved data and renders it.

## Core root folders — purpose and what to point to

- `app/controllers/` — Bridge between UI and backend logic. Handles user actions, session updates, and page navigation.
  - Example files: [app/controllers/recommendation_controller.py](../app/controllers/recommendation_controller.py), [app/controllers/recommendation_result_controller.py](../app/controllers/recommendation_result_controller.py)
  - Example functions/classes to mention: `RecommendationController.on_generate`, `generate_recommendation_from_request`, `_store_recommendation_session`.

- `app/core/` — Application wiring, routing, and dependency container.
  - Example files: [app/core/router.py](../app/core/router.py), [app/core/container.py](../app/core/container.py)
  - Purpose: declare routes, construct controllers and services, and provide per-page singletons.

- `app/config/` — Configuration dataclasses for AI, DB, and app settings.
  - Example files: [app/config/ai_config.py](../app/config/ai_config.py), [app/config/database_config.py](../app/config/database_config.py)

- `app/services/` — Business logic layer. Recommendation engine, orchestrator, AI wrappers, DB helpers.
  - Example files: [app/services/recommendation_service.py](../app/services/recommendation_service.py), [app/services/research_support_service.py](../app/services/research_support_service.py), [app/services/chatbot_service.py](../app/services/chatbot_service.py)
  - What to point out: `RecommendationService.generate_full_recommendation`, `calculate_scores`, `generate_alternative_stacks`, `ResearchSupportService.generate_ai_research_support`.

- `app/repositories/` — Persistence layer with raw SQL statements or DB-specific queries.
  - Example files: [app/repositories/recommendation_repository.py](../app/repositories/recommendation_repository.py)
  - What to point out: `create`, `find_by_id`, `add_history`, `latest_for_user`.

- `app/models/` — Domain model classes representing DB rows and in-memory entities.
  - Example files: [app/models/recommendation.py](../app/models/recommendation.py)

- `app/schemas/` — Validation and request schema objects (data validation, typed requests).
  - Example files: [app/schemas/recommendation_schema.py](../app/schemas/recommendation_schema.py)

- `app/requests/` — Request DTOs and helpers used by controllers and services.
  - Example files: [app/requests/recommendation_request.py](../app/requests/recommendation_request.py)

- `app/helpers/` (or `app/utils/`) — Utility helpers and small adapters.
  - Example files: [app/helpers/recommendation_engine_compat.py](../app/helpers/recommendation_engine_compat.py), [app/utils/hash_helper.py](../app/utils/hash_helper.py)

- `ui/pages/` and `ui/components/` — Flet views and reusable UI components.
  - Example files: [ui/pages/recommendation_page.py](../ui/pages/recommendation_page.py), [ui/pages/recommendation_result_page.py](../ui/pages/recommendation_result_page.py)

- `database/` — SQL setup, migrations, and seeders for initializing MySQL schema and example data.
  - Example files: [database/setup.sql](../database/setup.sql), [database/migrations/initial_migration.py](../database/migrations/initial_migration.py)

- `tests/` — Automated tests for engine behavior and integration points.
  - Example files: [test_recommendation_engine.py](../test_recommendation_engine.py)

- `assets/`, `ui/`, `fonts/`, `images/` — Static assets for the UI (icons, fonts, images, themes).

## Short purpose summary (one-liners)

- Controllers: coordinate UI ↔ services.
- Services: business rules and domain logic.
- Repositories: SQL and persistence.
- Models/Schemas/Requests: typed data and validation.
- Core: app wiring and routing.
- Database: storage and migrations.

## How to present this in 60 seconds

"The app follows a standard layered architecture: Flet UI pages call controllers which validate input and call services. Services hold the business logic — the recommendation engine lives in `RecommendationService`. Persistence is isolated in repositories that call `DatabaseService` to run SQL against MySQL. AI features (chat and research) are provided by dedicated services that call a local Ollama instance; if Ollama is unavailable, the app falls back cleanly. The core wiring and DI lives in `app/core/container.py` and routes are declared in `app/core/router.py`."

## Common defense questions and quick answers

- Q: Where is the main business logic? — A: `app/services/recommendation_service.py` (`generate_full_recommendation`).
- Q: Where do you save results? — A: `app/repositories/recommendation_repository.py` (`create`).
- Q: Where does Ollama live? — A: `app/services/ollama_service.py` and used via `chatbot_service` and `research_support_service`.
- Q: Why separate layers? — A: Separation of concerns makes code easier to test, maintain, and explain.

---
Feel free to ask for examples of the flow as a diagram, a shortened one-page slide, or expanded folder descriptions for any particular directory.
