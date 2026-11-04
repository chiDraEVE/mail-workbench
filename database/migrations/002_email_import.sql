-- Mail Workbench migration 002: message content and source import tracking.
-- Apply once to a database created from the original schema.sql.

ALTER TABLE email_messages
    ADD COLUMN recipients TEXT NULL AFTER sender,
    ADD COLUMN text_body LONGTEXT NULL AFTER received_at,
    ADD COLUMN html_body LONGTEXT NULL AFTER text_body,
    ADD UNIQUE KEY uq_email_messages_content_hash (content_hash);

ALTER TABLE email_messages
    DROP INDEX idx_email_messages_content_hash;

CREATE TABLE email_imports (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email_id BIGINT UNSIGNED NULL,
    source_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(1000) NOT NULL,
    source_fingerprint CHAR(64) NOT NULL,
    source_key CHAR(64) NOT NULL,
    import_status VARCHAR(30) NOT NULL,
    error_detail TEXT NULL,
    imported_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_email_imports_email
        FOREIGN KEY (email_id) REFERENCES email_messages(id) ON DELETE SET NULL,
    UNIQUE KEY uq_email_import_source (source_type, source_fingerprint, source_key),
    INDEX idx_email_imports_status (import_status),
    INDEX idx_email_imports_email (email_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE email_processing (
    email_id BIGINT UNSIGNED PRIMARY KEY,
    processing_status VARCHAR(30) NOT NULL DEFAULT 'pending',
    error_detail TEXT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_email_processing_email
        FOREIGN KEY (email_id) REFERENCES email_messages(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
