
-- WARNING: This script deletes all tables and their data.
-- Execute only against the intended development database.

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS email_observations;
DROP TABLE IF EXISTS email_processing;
DROP TABLE IF EXISTS email_imports;
DROP TABLE IF EXISTS email_messages;
DROP TABLE IF EXISTS job_description_snapshots;
DROP TABLE IF EXISTS job_publications;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS company_addresses;
DROP TABLE IF EXISTS companies;

SET FOREIGN_KEY_CHECKS = 1;
