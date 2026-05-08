"""Initial schema migration (MySQL/MariaDB).

Idempotent — safe to call on every startup. The ``schema_version`` table
tracks applied migrations so future migrations can be ordered.

All tables use ``InnoDB`` + ``utf8mb4`` for proper foreign-key + emoji
support, and follow phpMyAdmin-friendly naming conventions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.utils.logger import get_logger

if TYPE_CHECKING:
    from app.services.database_service import DatabaseService

log = get_logger(__name__)


INITIAL_SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INT PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(120) NOT NULL,
    username VARCHAR(64) NOT NULL,
    email VARCHAR(160) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS recommendations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    project_name VARCHAR(120) NOT NULL,
    project_type VARCHAR(80) NOT NULL,
    project_goal VARCHAR(80) NOT NULL,
    complexity VARCHAR(40) NOT NULL,
    team_size VARCHAR(60) NOT NULL,
    timeline VARCHAR(60) NOT NULL,
    scalability VARCHAR(40) NOT NULL,
    security VARCHAR(40) NOT NULL,
    platform VARCHAR(60) NOT NULL,
    experience VARCHAR(40) NOT NULL,

    recommended_language VARCHAR(80) NOT NULL,
    recommended_framework VARCHAR(80) NOT NULL,
    recommended_sdlc VARCHAR(80) NOT NULL,
    confidence_score INT NOT NULL,
    explanation_json LONGTEXT NOT NULL,
    alternatives_json LONGTEXT NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_recommendations_user (user_id, created_at),
    CONSTRAINT fk_recommendations_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS recommendation_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    recommendation_id INT NOT NULL,
    action VARCHAR(40) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_recommendation_history_user (user_id, created_at),
    CONSTRAINT fk_history_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_history_recommendation FOREIGN KEY (recommendation_id)
        REFERENCES recommendations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS analytics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    metric VARCHAR(80) NOT NULL,
    value DOUBLE NOT NULL,
    metadata_json LONGTEXT NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_analytics_user (user_id, metric),
    CONSTRAINT fk_analytics_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS chatbot_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    role VARCHAR(20) NOT NULL,
    content LONGTEXT NOT NULL,
    model VARCHAR(80) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_chatbot_logs_user (user_id, created_at),
    CONSTRAINT fk_chatbot_logs_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS learning_articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    slug VARCHAR(120) NOT NULL,
    category VARCHAR(60) NOT NULL,
    title VARCHAR(200) NOT NULL,
    summary TEXT NOT NULL,
    content LONGTEXT NOT NULL,
    tags VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_learning_articles_slug (slug),
    INDEX idx_learning_articles_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


def run_migrations(db: "DatabaseService") -> None:
    # Defense-in-depth: refuse to run migrations against a forbidden DB.
    # DatabaseService.script() also asserts this, but we check here too so
    # an accidental future caller of run_migrations() is equally protected.
    db._config.assert_safe_to_modify()

    db.script(INITIAL_SCHEMA)

    row = db.fetch_one("SELECT MAX(version) AS v FROM schema_version")
    current = (row["v"] if row else None) or 0

    if current < 1:
        db.execute("INSERT INTO schema_version (version) VALUES (%s)", (1,))
        log.info("Applied initial schema (v1).")
