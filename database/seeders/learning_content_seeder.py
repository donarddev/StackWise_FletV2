"""Seed the Learning Hub with curated educational articles.

Idempotent: only inserts rows whose slug isn't already present.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.utils.logger import get_logger

if TYPE_CHECKING:
    from app.services.database_service import DatabaseService

log = get_logger(__name__)


ARTICLES: list[dict] = [
    # ---------- Languages ----------
    {
        "slug": "language-python",
        "category": "Languages",
        "title": "Python — The Versatile Generalist",
        "summary": "Readable, batteries-included, and unbeatable for AI, data science, scripting, and rapid web back-ends.",
        "tags": "language,backend,ai,scripting",
        "content": (
            "Python emphasizes readability and developer velocity. Its strengths are a vast ecosystem "
            "(NumPy, Pandas, FastAPI, Django, PyTorch), an interactive REPL culture, and a low-friction "
            "syntax that lets teams ship features fast.\n\n"
            "**Best fit for:** AI/ML, data analytics, prototypes, automation, internal tooling, REST APIs.\n\n"
            "**Trade-offs:** GIL limits CPU-bound multithreading; runtime is slower than compiled languages. "
            "For high-throughput systems, pair Python with Rust/Go services or use Cython/numba for hotspots."
        ),
    },
    {
        "slug": "language-javascript",
        "category": "Languages",
        "title": "JavaScript / TypeScript — The Web's Lingua Franca",
        "summary": "Single language across browser, server, and mobile. TypeScript adds the type-safety modern teams need.",
        "tags": "language,web,frontend,backend",
        "content": (
            "JavaScript runs everywhere a browser does. Node.js extends it to servers, and TypeScript adds "
            "static types without changing the runtime. The ecosystem is the largest on Earth (npm).\n\n"
            "**Best fit for:** Web apps, full-stack SaaS, real-time apps, BFFs, serverless.\n\n"
            "**Trade-offs:** Ecosystem churn is real — pick stable defaults (Next.js, Nest, Express). "
            "Without TypeScript, large codebases drift quickly."
        ),
    },
    {
        "slug": "language-go",
        "category": "Languages",
        "title": "Go — The Concurrency-First Backend Language",
        "summary": "Tiny syntax, fast compile times, first-class concurrency, and a single static binary you can deploy anywhere.",
        "tags": "language,backend,cloud,devops",
        "content": (
            "Go was built at Google for cloud infrastructure. Goroutines and channels make concurrency approachable, "
            "and its standard library covers HTTP, JSON, crypto, and more out of the box.\n\n"
            "**Best fit for:** APIs, microservices, CLI tooling, DevOps platforms (Kubernetes, Terraform are written in Go).\n\n"
            "**Trade-offs:** Generics are recent; the language is intentionally minimal which can feel verbose."
        ),
    },
    {
        "slug": "language-rust",
        "category": "Languages",
        "title": "Rust — Memory Safety Without a Garbage Collector",
        "summary": "Use Rust when correctness and performance matter more than time-to-market.",
        "tags": "language,systems,performance",
        "content": (
            "Rust's ownership model eliminates whole classes of bugs at compile time. It produces small, fast, "
            "predictable binaries — a great fit for systems software, performance-critical services, and WASM.\n\n"
            "**Best fit for:** High-performance services, embedded, browsers/engines, security-sensitive code.\n\n"
            "**Trade-offs:** Steeper learning curve, slower iteration speed for plain CRUD work."
        ),
    },
    {
        "slug": "language-java",
        "category": "Languages",
        "title": "Java — The Enterprise Standard",
        "summary": "Mature, statically typed, and battle-tested in regulated industries.",
        "tags": "language,backend,enterprise",
        "content": (
            "Java powers banks, airlines, and the Android ecosystem. The JVM is one of the most optimized runtimes ever built, "
            "and the ecosystem (Spring, Hibernate) covers virtually every enterprise need.\n\n"
            "**Best fit for:** Large enterprise systems, regulated industries, Android (with Kotlin), big-data pipelines.\n\n"
            "**Trade-offs:** Verbosity (mitigated by Kotlin), heavier tooling than scripting languages."
        ),
    },
    # ---------- Frameworks ----------
    {
        "slug": "framework-django",
        "category": "Frameworks",
        "title": "Django — Batteries-Included Python Web Framework",
        "summary": "ORM, admin, auth, and migrations out of the box. Perfect for content-heavy and CRUD-heavy products.",
        "tags": "framework,python,backend,web",
        "content": (
            "Django ships with a full ORM, admin panel, authentication, and migrations. It's opinionated in the "
            "best way — teams stop bikeshedding and start shipping.\n\n"
            "**Best fit for:** Content sites, marketplaces, internal tools, MVPs that may grow.\n\n"
            "**Trade-offs:** Less ideal for real-time/streaming workloads; FastAPI may suit those better."
        ),
    },
    {
        "slug": "framework-fastapi",
        "category": "Frameworks",
        "title": "FastAPI — Modern Async Python APIs",
        "summary": "Type-driven, async-first, with auto-generated OpenAPI docs. The default choice for new Python APIs.",
        "tags": "framework,python,backend,api",
        "content": (
            "FastAPI uses Python type hints to validate requests, serialize responses, and generate OpenAPI/Swagger docs "
            "automatically. It's async-first, performant, and a joy to write.\n\n"
            "**Best fit for:** APIs, microservices, AI/ML inference servers.\n\n"
            "**Trade-offs:** Lighter on built-ins than Django (no admin, no ORM by default — use SQLAlchemy)."
        ),
    },
    {
        "slug": "framework-nextjs",
        "category": "Frameworks",
        "title": "Next.js — The React Framework for Production",
        "summary": "Server components, edge rendering, file-system routing, and outstanding DX.",
        "tags": "framework,javascript,web,frontend",
        "content": (
            "Next.js gives you the full React experience plus server-side rendering, edge functions, "
            "image optimization, and a powerful router. It's the default choice for new SaaS web apps.\n\n"
            "**Best fit for:** Marketing sites, dashboards, full-stack web apps, AI front-ends.\n\n"
            "**Trade-offs:** Server-component mental model has a learning curve; vendor-affinity to Vercel."
        ),
    },
    {
        "slug": "framework-spring-boot",
        "category": "Frameworks",
        "title": "Spring Boot — Enterprise Java, Productive Again",
        "summary": "Convention over configuration, production-grade defaults, deep ecosystem.",
        "tags": "framework,java,backend,enterprise",
        "content": (
            "Spring Boot makes Java productive: starter dependencies, auto-config, and a vast ecosystem (Security, Data, "
            "Cloud) cover enterprise concerns out of the box.\n\n"
            "**Best fit for:** Large back-ends, regulated industries, microservices at scale.\n\n"
            "**Trade-offs:** Heavier startup; build/deploy cycle slower than scripting frameworks."
        ),
    },
    {
        "slug": "framework-flutter",
        "category": "Frameworks",
        "title": "Flutter — One Codebase, Every Screen",
        "summary": "Dart-powered cross-platform UI for iOS, Android, web, and desktop.",
        "tags": "framework,mobile,cross-platform",
        "content": (
            "Flutter uses a single rendering engine across platforms, giving identical UI on iOS, Android, web, and desktop. "
            "Tooling (hot reload, devtools) is excellent.\n\n"
            "**Best fit for:** Cross-platform mobile apps, design-driven products, MVPs that need to run everywhere.\n\n"
            "**Trade-offs:** Dart language, larger app sizes than native, native-platform integrations sometimes need plugins."
        ),
    },
    # ---------- SDLC ----------
    {
        "slug": "sdlc-agile-scrum",
        "category": "SDLC",
        "title": "Agile / Scrum — Iterative Delivery",
        "summary": "Time-boxed sprints, working software every iteration, continuous customer feedback.",
        "tags": "sdlc,methodology,agile",
        "content": (
            "Scrum organizes work into 1–4 week sprints. Roles (Product Owner, Scrum Master, Team), artifacts "
            "(Backlog, Sprint Backlog, Increment), and ceremonies (Planning, Daily, Review, Retro) create predictability.\n\n"
            "**Best fit for:** Product teams shipping continuously, evolving requirements, small-to-medium teams.\n\n"
            "**Trade-offs:** Requires discipline; risk of cargo-culting ceremonies without agile mindset."
        ),
    },
    {
        "slug": "sdlc-kanban",
        "category": "SDLC",
        "title": "Kanban — Continuous Flow",
        "summary": "Visualize work, limit WIP, optimize for throughput. Great for support and ops-heavy teams.",
        "tags": "sdlc,methodology,lean",
        "content": (
            "Kanban replaces sprints with a continuous flow of work, capped by Work-In-Progress (WIP) limits. "
            "Teams optimize for cycle time and throughput rather than story-point velocity.\n\n"
            "**Best fit for:** Maintenance, ops, support teams, smaller teams with steady inflow.\n\n"
            "**Trade-offs:** Less ceremony means less explicit alignment; pair with regular reviews."
        ),
    },
    {
        "slug": "sdlc-waterfall",
        "category": "SDLC",
        "title": "Waterfall — Sequential, Specification-First",
        "summary": "Phase-gated delivery: requirements → design → implementation → verification → maintenance.",
        "tags": "sdlc,methodology,traditional",
        "content": (
            "Waterfall is sequential and document-heavy. It excels when requirements are stable and contractually fixed.\n\n"
            "**Best fit for:** Regulated industries, fixed-scope contracts, hardware-coupled software.\n\n"
            "**Trade-offs:** Late integration of feedback; expensive late-stage changes."
        ),
    },
    {
        "slug": "sdlc-devops",
        "category": "SDLC",
        "title": "DevOps — Continuous Delivery as a Practice",
        "summary": "Automated pipelines, infra-as-code, observability — ship reliably, often.",
        "tags": "sdlc,methodology,devops",
        "content": (
            "DevOps unifies development and operations behind shared metrics (lead time, change-failure rate, MTTR). "
            "Automation (CI/CD, IaC) and observability are the core enablers.\n\n"
            "**Best fit for:** Cloud-native products, SaaS at scale, teams shipping multiple times per day.\n\n"
            "**Trade-offs:** Up-front investment in pipelines and culture before value compounds."
        ),
    },
    {
        "slug": "concept-mvp",
        "category": "Concepts",
        "title": "Building an MVP That Survives Contact With Reality",
        "summary": "Pick boring tech, narrow the surface area, and ship something users can actually use.",
        "tags": "concept,mvp,planning",
        "content": (
            "An MVP is the smallest product that lets you learn whether your hypothesis is correct. "
            "Cut features ruthlessly, prefer boring/proven tech, and instrument everything so you can learn fast.\n\n"
            "**Tip:** Don't optimize for scale before you have users; optimize for learning speed."
        ),
    },
]


def seed_learning_content(db: "DatabaseService") -> None:
    inserted = 0
    for art in ARTICLES:
        row = db.fetch_one(
            "SELECT id FROM learning_articles WHERE slug = %s",
            (art["slug"],),
        )
        if row is not None:
            continue
        db.execute(
            "INSERT INTO learning_articles (slug, category, title, summary, content, tags) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                art["slug"],
                art["category"],
                art["title"],
                art["summary"],
                art["content"],
                art["tags"],
            ),
        )
        inserted += 1

    if inserted:
        log.info("Seeded %d learning articles.", inserted)
