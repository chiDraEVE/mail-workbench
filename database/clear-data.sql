-- WARNING: This script permanently deletes all project data in the selected
-- database while keeping the tables and schema intact.
-- Check the database name printed below before continuing.

SELECT DATABASE() AS database_being_cleared;

START TRANSACTION;

DELETE FROM email_observations;
DELETE FROM email_processing;
DELETE FROM email_imports;
DELETE FROM job_publications;
DELETE FROM jobs;
DELETE FROM company_addresses;
DELETE FROM companies;
DELETE FROM email_messages;

COMMIT;
