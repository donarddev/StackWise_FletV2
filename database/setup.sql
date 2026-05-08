-- =============================================================================
-- StackWise AI — manual database setup script (MySQL / MariaDB)
-- =============================================================================
--
-- Purpose:
--   Idempotently create all tables required by StackWise AI inside the
--   `stackwise_ai` database. Safe to run multiple times.
--
-- This script is INTENTIONALLY:
--   - Non-destructive    (only CREATE TABLE IF NOT EXISTS, no DROP/TRUNCATE)
--   - Database-scoped    (USE stackwise_ai;)
--   - Self-guarding      (the first SELECT below raises a clear error if you
--                         accidentally run it inside any database other than
--                         `stackwise_ai`)
--
-- It will NEVER touch the `stackwise` (Laravel) database.
--
-- How to run in phpMyAdmin:
--   1. Open phpMyAdmin (Laragon → Menu → MySQL → phpMyAdmin).
--   2. Click on `stackwise_ai` in the left sidebar (the database must already
--      exist — create it first if needed via the "Databases" tab using
--      collation `utf8mb4_unicode_ci`).
--   3. Click the "SQL" tab at the top.
--   4. Paste this entire file and click "Go".
--
-- The first SELECT in this script will fail loudly if you somehow run it
-- while connected to the wrong database, so you cannot accidentally damage
-- another schema.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 0. SAFETY GUARD
-- -----------------------------------------------------------------------------
-- Switch to stackwise_ai. If the database doesn't exist, the USE command
-- will fail and the script will abort before any DDL runs.

USE `stackwise_ai`;

-- A second guard: this SELECT references a non-existent table when DATABASE()
-- is anything other than 'stackwise_ai', causing the script to halt before
-- any CREATE TABLE statement runs.
SELECT
    CASE
        WHEN DATABASE() = 'stackwise_ai' THEN 'OK: connected to stackwise_ai'
        ELSE (SELECT 1 FROM `__stackwise_ai_safety_stop__`)
    END AS safety_check;


-- -----------------------------------------------------------------------------
-- 1. SCHEMA VERSION
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS schema_version (
    version    INT PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 2. USERS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id            INT PRIMARY KEY AUTO_INCREMENT,
    full_name     VARCHAR(120) NOT NULL,
    username      VARCHAR(64)  NOT NULL,
    email         VARCHAR(160) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 3. RECOMMENDATIONS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recommendations (
    id                     INT PRIMARY KEY AUTO_INCREMENT,
    user_id                INT NOT NULL,

    project_name           VARCHAR(120) NOT NULL,
    project_type           VARCHAR(80)  NOT NULL,
    project_goal           VARCHAR(80)  NOT NULL,
    complexity             VARCHAR(40)  NOT NULL,
    team_size              VARCHAR(60)  NOT NULL,
    timeline               VARCHAR(60)  NOT NULL,
    scalability            VARCHAR(40)  NOT NULL,
    security               VARCHAR(40)  NOT NULL,
    platform               VARCHAR(60)  NOT NULL,
    experience             VARCHAR(40)  NOT NULL,

    recommended_language   VARCHAR(80)  NOT NULL,
    recommended_framework  VARCHAR(80)  NOT NULL,
    recommended_sdlc       VARCHAR(80)  NOT NULL,
    confidence_score       INT          NOT NULL,
    explanation_json       LONGTEXT     NOT NULL,
    alternatives_json      LONGTEXT     NOT NULL,

    created_at             TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_recommendations_user (user_id, created_at),
    CONSTRAINT fk_recommendations_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 4. RECOMMENDATION HISTORY (audit trail)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recommendation_history (
    id                INT PRIMARY KEY AUTO_INCREMENT,
    user_id           INT NOT NULL,
    recommendation_id INT NOT NULL,
    action            VARCHAR(40) NOT NULL,
    created_at        TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_recommendation_history_user (user_id, created_at),
    CONSTRAINT fk_history_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_history_recommendation FOREIGN KEY (recommendation_id)
        REFERENCES recommendations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 5. ANALYTICS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS analytics (
    id            INT PRIMARY KEY AUTO_INCREMENT,
    user_id       INT          NOT NULL,
    metric        VARCHAR(80)  NOT NULL,
    value         DOUBLE       NOT NULL,
    metadata_json LONGTEXT     NULL,
    recorded_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_analytics_user (user_id, metric),
    CONSTRAINT fk_analytics_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 6. CHATBOT LOGS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chatbot_logs (
    id         INT PRIMARY KEY AUTO_INCREMENT,
    user_id    INT          NOT NULL,
    role       VARCHAR(20)  NOT NULL,
    content    LONGTEXT     NOT NULL,
    model      VARCHAR(80)  NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_chatbot_logs_user (user_id, created_at),
    CONSTRAINT fk_chatbot_logs_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 7. LEARNING ARTICLES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_articles (
    id         INT PRIMARY KEY AUTO_INCREMENT,
    slug       VARCHAR(120) NOT NULL,
    category   VARCHAR(60)  NOT NULL,
    title      VARCHAR(200) NOT NULL,
    summary    TEXT         NOT NULL,
    content    LONGTEXT     NOT NULL,
    tags       VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_learning_articles_slug (slug),
    INDEX idx_learning_articles_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 8. CONFIRMATION
-- -----------------------------------------------------------------------------
-- Final sanity check — confirm we operated on the correct schema.
SELECT
    DATABASE() AS connected_database,
    (SELECT COUNT(*) FROM information_schema.TABLES
       WHERE TABLE_SCHEMA = 'stackwise_ai') AS tables_in_stackwise_ai;
