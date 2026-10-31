
-- Mail Workbench
-- Initial database schema: v1
-- Execute this script in the mail-workbench database.

CREATE TABLE companies (
                           id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                           name VARCHAR(255) NOT NULL,
                           normalized_name VARCHAR(255) NULL,
                           website VARCHAR(500) NULL,
                           created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                           updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                               ON UPDATE CURRENT_TIMESTAMP,

                           INDEX idx_companies_name (name),
                           INDEX idx_companies_normalized_name (normalized_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE company_addresses (
                                   id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                                   company_id BIGINT UNSIGNED NOT NULL,
                                   address_type VARCHAR(50) NOT NULL DEFAULT 'general',
                                   street VARCHAR(255) NULL,
                                   postal_code VARCHAR(20) NULL,
                                   city VARCHAR(150) NULL,
                                   region VARCHAR(150) NULL,
                                   country VARCHAR(100) NOT NULL DEFAULT 'Deutschland',
                                   is_primary BOOLEAN NOT NULL DEFAULT FALSE,
                                   source_url VARCHAR(500) NULL,
                                   verified_at DATETIME NULL,
                                   created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                   updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                                       ON UPDATE CURRENT_TIMESTAMP,

                                   CONSTRAINT fk_company_addresses_company
                                       FOREIGN KEY (company_id) REFERENCES companies(id)
                                           ON DELETE CASCADE,

                                   INDEX idx_company_addresses_company (company_id),
                                   INDEX idx_company_addresses_type (address_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE jobs (
                      id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                      title VARCHAR(500) NOT NULL,
                      employer_company_id BIGINT UNSIGNED NULL,
                      recruiter_company_id BIGINT UNSIGNED NULL,
                      location VARCHAR(255) NULL,
                      description LONGTEXT NULL,
                      employment_type VARCHAR(100) NULL,
                      work_mode VARCHAR(50) NULL,
                      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                          ON UPDATE CURRENT_TIMESTAMP,

                      CONSTRAINT fk_jobs_employer
                          FOREIGN KEY (employer_company_id) REFERENCES companies(id)
                              ON DELETE SET NULL,

                      CONSTRAINT fk_jobs_recruiter
                          FOREIGN KEY (recruiter_company_id) REFERENCES companies(id)
                              ON DELETE SET NULL,

                      INDEX idx_jobs_title (title),
                      INDEX idx_jobs_employer (employer_company_id),
                      INDEX idx_jobs_recruiter (recruiter_company_id),
                      INDEX idx_jobs_location (location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE job_publications (
                                  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                                  job_id BIGINT UNSIGNED NOT NULL,
                                  platform VARCHAR(100) NOT NULL,
                                  external_id VARCHAR(255) NULL,
                                  url TEXT NOT NULL,
                                  normalized_url TEXT NULL,
                                  link_text VARCHAR(500) NULL,
                                  published_at DATETIME NULL,
                                  first_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                  last_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                  checked_at DATETIME NULL,
                                  availability_status VARCHAR(50) NOT NULL DEFAULT 'unknown',
                                  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                                      ON UPDATE CURRENT_TIMESTAMP,

                                  CONSTRAINT fk_job_publications_job
                                      FOREIGN KEY (job_id) REFERENCES jobs(id)
                                          ON DELETE CASCADE,

                                  INDEX idx_job_publications_job (job_id),
                                  INDEX idx_job_publications_platform (platform),
                                  INDEX idx_job_publications_external_id (external_id),
                                  INDEX idx_job_publications_status (availability_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE email_messages (
                                id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                                message_id VARCHAR(500) NULL,
                                sender VARCHAR(500) NULL,
                                subject VARCHAR(1000) NULL,
                                received_at DATETIME NULL,
                                content_hash CHAR(64) NULL,
                                imported_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

                                UNIQUE KEY uq_email_messages_message_id (message_id),
                                INDEX idx_email_messages_received_at (received_at),
                                INDEX idx_email_messages_content_hash (content_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE email_observations (
                                    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                                    email_id BIGINT UNSIGNED NOT NULL,
                                    publication_id BIGINT UNSIGNED NOT NULL,
                                    observed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

                                    CONSTRAINT fk_email_observations_email
                                        FOREIGN KEY (email_id) REFERENCES email_messages(id)
                                            ON DELETE CASCADE,

                                    CONSTRAINT fk_email_observations_publication
                                        FOREIGN KEY (publication_id) REFERENCES job_publications(id)
                                            ON DELETE CASCADE,

                                    UNIQUE KEY uq_email_publication (email_id, publication_id),
                                    INDEX idx_email_observations_publication (publication_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
