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
    
    # Migration v2: add columns to support Google OAuth users
    if current < 2:
        schema = db._config.database

        # google_id
        row = db.fetch_one(
            "SELECT COUNT(*) AS c FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s",
            (schema, "users", "google_id"),
        )
        if not row or int(row.get("c", 0)) == 0:
            db.execute("ALTER TABLE users ADD COLUMN google_id VARCHAR(255) NULL")

        # provider
        row = db.fetch_one(
            "SELECT COUNT(*) AS c FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s",
            (schema, "users", "provider"),
        )
        if not row or int(row.get("c", 0)) == 0:
            db.execute("ALTER TABLE users ADD COLUMN provider VARCHAR(50) NOT NULL DEFAULT 'local'")

        # avatar_url
        row = db.fetch_one(
            "SELECT COUNT(*) AS c FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s",
            (schema, "users", "avatar_url"),
        )
        if not row or int(row.get("c", 0)) == 0:
            db.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT NULL")

        # make password_hash nullable if currently NOT NULL
        row = db.fetch_one(
            "SELECT IS_NULLABLE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s",
            (schema, "users", "password_hash"),
        )
        if row and row.get("IS_NULLABLE") == "NO":
            db.execute("ALTER TABLE users MODIFY COLUMN password_hash VARCHAR(255) NULL")

        db.execute("INSERT INTO schema_version (version) VALUES (%s)", (2,))
        log.info("Applied migration v2 (Google OAuth columns).")

    # Migration v3: store richer recommendation request payload as JSON
    if current < 3:
        schema = db._config.database
        row = db.fetch_one(
            "SELECT COUNT(*) AS c FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s",
            (schema, "recommendations", "project_profile_json"),
        )
        if not row or int(row.get("c", 0)) == 0:
            db.execute("ALTER TABLE recommendations ADD COLUMN project_profile_json LONGTEXT NULL")
        db.execute("INSERT INTO schema_version (version) VALUES (%s)", (3,))
        log.info("Applied migration v3 (recommendation project_profile_json).")

    # Migration v4: UI theme preference per user (dark / light)
    if current < 4:
        schema = db._config.database
        row = db.fetch_one(
            "SELECT COUNT(*) AS c FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s",
            (schema, "users", "theme_mode"),
        )
        if not row or int(row.get("c", 0)) == 0:
            db.execute(
                "ALTER TABLE users ADD COLUMN theme_mode VARCHAR(16) NULL "
                "COMMENT 'UI preference: dark or light'"
            )
        db.execute("INSERT INTO schema_version (version) VALUES (%s)", (4,))
        log.info("Applied migration v4 (users.theme_mode).")

    # Migration v5: recommendation feedback (ratings on saved reports)
    if current < 5:
        db.script(
            """
            CREATE TABLE IF NOT EXISTS recommendation_feedback (
                id INT PRIMARY KEY AUTO_INCREMENT,
                recommendation_id INT NOT NULL,
                user_id INT NOT NULL,
                rating INT NOT NULL,
                comment TEXT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_feedback_user (user_id, created_at),
                INDEX idx_feedback_rec (recommendation_id),
                UNIQUE KEY uq_feedback_user_rec (user_id, recommendation_id),
                CONSTRAINT fk_feedback_user FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT fk_feedback_rec FOREIGN KEY (recommendation_id)
                    REFERENCES recommendations(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
        )
        db.execute("INSERT INTO schema_version (version) VALUES (%s)", (5,))
        log.info("Applied migration v5 (recommendation_feedback).")

    # Migration v6: soft-delete support on recommendations
    if current < 6:
        schema = db._config.database
        row = db.fetch_one(
            "SELECT COUNT(*) AS c FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s",
            (schema, "recommendations", "deleted_at"),
        )
        if not row or int(row.get("c", 0)) == 0:
            db.execute(
                "ALTER TABLE recommendations ADD COLUMN deleted_at DATETIME NULL "
                "DEFAULT NULL AFTER created_at"
            )
            db.execute(
                "CREATE INDEX idx_recommendations_user_active "
                "ON recommendations (user_id, deleted_at, created_at)"
            )
        db.execute("INSERT INTO schema_version (version) VALUES (%s)", (6,))
        log.info("Applied migration v6 (recommendations.deleted_at).")
