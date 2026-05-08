# StackWise AI

> An AI-powered Decision Support System for choosing the right **programming language**, **framework**, and **SDLC model** for your next project.

StackWise AI is a Flet-based, SaaS-grade desktop/web application that behaves like an **AI software architect assistant**. It analyzes your project profile (type, goals, complexity, team size, timeline, scalability, security, experience, target platform) and produces **explainable, intelligent recommendations** with confidence scoring, trade-off analysis, and educational guidance.

---

## Highlights

- **AI-powered recommendations** — hybrid scoring engine + Ollama LLM explanations
- **Explainable results** — confidence score, reasoning, alternatives, and trade-offs
- **Conversational AI** — built-in Ollama-powered chatbot for software engineering questions
- **Recommendation history** — review, compare, and regenerate past decisions
- **Learning Hub** — curated educational content on languages, frameworks, and SDLC models
- **Premium UI/UX** — dark mode, glassmorphism, floating cards, smooth motion (Vercel / Linear / Notion inspired)
- **Clean architecture** — MVC + Service Pattern + Repository Pattern + Request Validation
- **MySQL/MariaDB** — production-ready relational backend (Laragon-friendly defaults)

---

## Architecture

```
stackwise_ai/
├── app/
│   ├── controllers/   # Page coordination, navigation, state wiring
│   ├── services/      # Business logic (recommendation, AI, auth, analytics)
│   ├── requests/      # Validation classes for user inputs
│   ├── models/        # Pure data entities
│   ├── repositories/  # Database access layer
│   ├── helpers/       # Hashing, dates, IDs
│   ├── core/          # Session, router, app state, DI container
│   ├── config/        # App / DB / AI configuration
│   └── utils/         # Constants, logger, generic validators
│
├── ui/
│   ├── pages/         # Top-level pages (dashboard, recommendation, ...)
│   ├── layouts/       # App + auth shells (sidebar, header)
│   ├── components/    # Reusable UI atoms
│   ├── widgets/       # Composite domain widgets
│   ├── dialogs/       # Modal dialogs
│   ├── themes/        # Theme tokens, palette, typography
│   └── animations/    # Motion helpers
│
├── database/
│   ├── migrations/    # MySQL schema migrations (idempotent)
│   └── seeders/       # Default content (Learning Hub)
│
├── assets/            # Icons, images, fonts
├── tests/             # Smoke + integration tests
├── main.py            # Application entrypoint
└── requirements.txt
```

### Architectural rules (strictly enforced)

| Layer | Allowed | Forbidden |
|---|---|---|
| **Models** | Data shape only | Business logic, UI, DB queries |
| **Repositories** | DB access | Business logic, UI |
| **Services** | Business logic | UI, direct DB queries |
| **Controllers** | Routing, page flow, state wiring | Business logic, DB access |
| **Views (pages/components)** | UI rendering | Business logic, DB queries |
| **Requests** | Input validation & sanitization | Business logic, DB |

---

## Getting started

### 1. Prerequisites

- Python **3.10+**
- **Laragon** (or any MySQL/MariaDB 8+ server) — start MySQL via Laragon
- **Ollama** with the **`llama3.2`** model:
  ```bash
  ollama pull llama3.2
  ollama serve
  ```
  StackWise AI runs perfectly without Ollama — it gracefully falls back to deterministic, rule-based explanations.

### 2. Database setup (Laragon + phpMyAdmin)

> **Database safety guarantee.** StackWise AI ships with a hard-coded
> safety stop: if `STACKWISE_DB_NAME` is ever set to **`stackwise`**, the
> application aborts immediately with the message
> *"Safety stop: The `stackwise` database belongs to the Laravel project
> and must not be modified."* StackWise also never issues `DROP DATABASE`,
> `DROP TABLE`, or `TRUNCATE` against your production database — the
> migration is append-only (`CREATE TABLE IF NOT EXISTS`).

You don't need to do anything manual — StackWise creates the database and tables on first launch using its migration system.

If you'd rather create the database manually first:

1. Start **MySQL** in Laragon.
2. Open **phpMyAdmin** (Laragon → Menu → MySQL → phpMyAdmin, or `http://localhost/phpmyadmin/`).
3. Click **Databases** → enter **`stackwise_ai`** → set collation to **`utf8mb4_unicode_ci`** → **Create**.
4. Click on **`stackwise_ai`** in the sidebar → **SQL** tab → paste the contents of [`database/setup.sql`](database/setup.sql) → **Go**. This is fully idempotent and only runs `CREATE TABLE IF NOT EXISTS`. You should end up with the following tables under `stackwise_ai`:

   - `users`
   - `recommendations`
   - `recommendation_history`
   - `analytics`
   - `chatbot_logs`
   - `learning_articles`
   - `schema_version`

You can also skip step 4 entirely — running `python main.py` will execute the same migration automatically.

The default Laragon credentials are already wired in (`root` / empty password / `localhost:3306`). Override per-environment with these vars if needed:

| Variable | Default | Description |
|---|---|---|
| `STACKWISE_DB_DRIVER` | `mysql` | `mysql` or `mariadb` |
| `STACKWISE_DB_HOST` | `localhost` | MySQL host |
| `STACKWISE_DB_PORT` | `3306` | MySQL port |
| `STACKWISE_DB_USER` | `root` | MySQL user |
| `STACKWISE_DB_PASSWORD` | *(empty)* | MySQL password |
| `STACKWISE_DB_NAME` | `stackwise_ai` | Database name (refuses `stackwise`) |
| `STACKWISE_DB_AUTO_CREATE` | `true` | Set to `false` to require the DB to already exist |
| `STACKWISE_OLLAMA_URL` | `http://localhost:11434` | Ollama base URL |
| `STACKWISE_OLLAMA_MODEL` | `llama3.2` | Ollama model name |

#### Verify with phpMyAdmin (read-only SQL)

Run these in phpMyAdmin's **SQL** tab to inspect state without modifying anything:

```sql
-- Does stackwise_ai exist?
SHOW DATABASES LIKE 'stackwise_ai';

-- Confirm stackwise (Laravel) is a separate, untouched database:
SHOW DATABASES LIKE 'stackwise';

-- Side-by-side count of tables in each database:
SELECT TABLE_SCHEMA AS db, COUNT(*) AS table_count
FROM information_schema.TABLES
WHERE TABLE_SCHEMA IN ('stackwise', 'stackwise_ai')
GROUP BY TABLE_SCHEMA;

-- List tables created by StackWise AI:
SELECT TABLE_NAME, TABLE_ROWS, ENGINE, CREATE_TIME, UPDATE_TIME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'stackwise_ai'
ORDER BY TABLE_NAME;

-- List tables in the Laravel `stackwise` database (read-only — proves StackWise AI never touched it):
SELECT TABLE_NAME, CREATE_TIME, UPDATE_TIME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'stackwise'
ORDER BY TABLE_NAME;
```

#### Confirming only `stackwise_ai` was affected

1. Click the **phpMyAdmin home** icon (top-left) and watch the sidebar database list.
2. Click on **`stackwise`** → **Structure** tab. Note the `CREATE_TIME` and `UPDATE_TIME` of every table — they should reflect your Laravel project's last activity, never StackWise AI's runs.
3. Click on **`stackwise_ai`** → **Structure** tab. You should see the seven tables listed above. The `CREATE_TIME` of these tables corresponds to the first time you launched StackWise AI (or ran `setup.sql`).
4. (Optional) Compare counts before/after a launch:
   ```sql
   SELECT TABLE_NAME, TABLE_ROWS, UPDATE_TIME
   FROM information_schema.TABLES
   WHERE TABLE_SCHEMA = 'stackwise';
   ```
   Run before launching StackWise AI, then again after — the `stackwise` rows should be **identical**.

#### Troubleshooting: *"phpMyAdmin says `stackwise_ai` already exists, but I don't see it in the sidebar"*

This is almost always **phpMyAdmin's sidebar cache** rather than a real problem. Try, in order:

1. Click the **phpMyAdmin home icon** (top-left, the little house) — this fully refreshes the navigation panel.
2. Press **F5** (or Ctrl+F5) on the phpMyAdmin page.
3. Run `SHOW DATABASES LIKE 'stackwise_ai';` in the SQL tab. If it returns one row, the database genuinely exists and only the sidebar was stale.
4. Click the small **gear/refresh icon** at the top of the navigation panel ("Reload navigation panel").
5. Log out and back into phpMyAdmin.

If `SHOW DATABASES` confirms it exists, you're done — you can either let StackWise AI re-use it (safe; `CREATE DATABASE IF NOT EXISTS` is a no-op when the DB already exists) or run `database/setup.sql` against it.

### 3. Install Python dependencies

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Create `.env` from template

Copy the provided template and adjust values for your local setup:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS/Linux
cp .env.example .env
```

Use the `stackwise_ai` database for this app. Do **not** use the old Laravel database named `stackwise`.

### 5. Run

```bash
python main.py
```

On first launch StackWise will:

1. Connect to MySQL (creating the `stackwise_ai` database if it doesn't exist).
2. Run migrations (creates all tables).
3. Seed the Learning Hub with 15 curated articles.
4. Open the login screen — register an account, then explore.

### 6. Run the tests (optional)

```bash
python -m unittest discover -s tests -v
```

The tests use a separate database (`stackwise_ai_test`) so they never touch your production data. They skip cleanly if MySQL is not reachable.

---

## AI / Ollama

The chatbot calls Ollama at:

- **Endpoint**: `http://localhost:11434/api/generate`
- **Model**: `llama3.2`
- **Streaming**: supported (the page uses non-streaming by default for now; switch by calling `ChatbotService.stream()`)

If Ollama is offline, the chatbot displays a clean fallback message and the app continues to work fully.

Every chat turn (both user and assistant) is persisted to the `chatbot_logs` MySQL table, scoped to the logged-in user.

---

## Recommendation engine

StackWise AI uses a **hybrid recommendation engine**:

1. **Scoring engine** — each language / framework / SDLC has a typed profile. Profiles are scored against the user's project request along multiple weighted dimensions (complexity fit, team-size fit, timeline fit, scalability, security, learning curve, platform support, project-type alignment).
2. **Confidence scoring** — measures the margin between the top result and its closest alternatives, normalized to a 0–100 score.
3. **Explanation engine** — produces structured, human-readable rationale: *why this*, *why not the alternatives*, and *trade-offs*.
4. **Optional LLM enrichment** — Ollama can rewrite the explanation in a friendlier, more pedagogical voice (toggleable).

This design keeps recommendations **deterministic, explainable, and fast**, while still allowing AI augmentation. Every generated recommendation is persisted to the `recommendations` table, with an audit trail in `recommendation_history`.

---

## Tech stack

- **UI**: Flet 0.24
- **Storage**: MySQL/MariaDB via PyMySQL (Laragon-friendly)
- **Auth**: bcrypt password hashing, persistent client-storage session
- **AI**: Ollama (`/api/generate`, model `llama3.2`), with graceful fallback
- **Lang**: Python 3.10+, type hints, dataclasses

---

## License

MIT
