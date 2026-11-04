# Mail Workbench

A local, modular automation project for processing emails and extracting useful information from different sources.

## Motivation

My inbox contains a growing number of automated emails that require manual review. Job alerts from platforms such as LinkedIn, Indeed and the German Federal Employment Agency are a particular example.

Processing these emails manually involves several repetitive tasks:

- Extracting job listings and their URLs
- Identifying duplicate listings across different platforms
- Recognizing reposted or potentially outdated job advertisements
- Checking whether a listing is still available
- Collecting relevant information in a structured format
- Preparing listings for manual review and further processing

The goal of Mail Workbench is to automate the repetitive parts of this workflow while keeping important decisions under manual control.

## Goals

The project is intended to provide:

- **Email processing:** Read and parse locally available email data.
- **Structured storage:** Store extracted information in a relational database.
- **Duplicate detection:** Identify identical or similar listings across different sources.
- **Availability checks:** Collect information about whether a job listing is still accessible.
- **Reports:** Generate clear reports with links to the original listings.
- **Modularity:** Support different email-processing workflows through separate modules.

The initial focus is job advertisement processing. Additional modules may later handle security reports from NinjaFirewall and DMARC aggregate reports.

## Planned Architecture

The initial architecture is based on the following components:

| Component               | Technology                   |
|-------------------------|------------------------------|
| Email processing        | Python                       |
| Database                | MySQL                        |
| Reporting               | HTML                         |
| Version control         | Git                          |
| Development environment | Ubuntu 24.04 / IntelliJ IDEA |

A web interface may be added later. The processing logic should remain independent of the presentation layer.

## Development Roadmap

### Phase 1 – Project foundation

- [x] Create project structure
- [x] Initialize Git repository
- [x] Configure local development environment
- [x] Connect MySQL database in IntelliJ IDEA
- [x] Define project documentation and conventions
- [x] Create initial database schema
- [x] Set up Python environment and dependencies

### Phase 2 – Email import

- [x] Inspect and understand the local email storage format
- [x] Implement read-only Thunderbird MBOX import
- [x] Extract message metadata and text/HTML content
- [x] Store imported messages with deduplication and separate status tracking
- [ ] Extract job listings and their URLs

### Phase 3 – Job listing analysis

- [ ] Normalize URLs
- [ ] Detect duplicate listings
- [ ] Compare titles, companies and descriptions
- [ ] Track when listings were first and last observed
- [ ] Collect availability information

### Phase 4 – Reporting

- [ ] Generate HTML reports
- [ ] Provide direct links to original job advertisements
- [ ] Highlight potential duplicates and unavailable listings
- [ ] Support manual classification and review

### Future ideas

- Web-based interface
- Integration with existing job application workflows
- NinjaFirewall report processing
- DMARC aggregate report processing
- Optional AI-assisted analysis

## Development Principles

This project is also a practical learning exercise. The implementation should therefore remain understandable, testable and maintainable.

The following principles guide development:

- Prefer small, incremental implementation steps.
- Keep modules loosely coupled.
- Write automated tests for important functionality.
- Document architectural decisions and relevant implementation details.
- Avoid unnecessary dependencies and complexity.
- Keep sensitive data and credentials outside version control.
- Never modify or delete original emails during import.
- Keep final job evaluation and application decisions under manual control.

## Getting started

The project contains a read-only Thunderbird MBOX importer and a MySQL database
layer. Python 3.10 or newer and a reachable MySQL 8.0-compatible server are
required. Install the MySQL command-line client if you want to apply the schema
from a terminal.

1. Create and activate a virtual environment, then install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

   Run Python commands with this virtual environment active. This ensures the
   project uses the supported `mysql-connector-python` from `requirements.txt`
   instead of an older system-installed MySQL connector (which can fail with
   `AttributeError: module 'ssl' has no attribute 'wrap_socket'`).

2. Create a local database and a user with access to it. For example, in a
   MySQL administrative session:

   ```sql
   CREATE DATABASE `mail-workbench` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'mail-workbench'@'localhost' IDENTIFIED BY 'choose-a-local-password';
   GRANT ALL PRIVILEGES ON `mail-workbench`.* TO 'mail-workbench'@'localhost';
   ```

3. Copy `.env.example` to `.env` and set `DB_HOST`, `DB_PORT`, `DB_NAME`,
   `DB_USER` and `DB_PASSWORD` for your server. `.env` is ignored by Git; never
   commit real credentials.

4. Apply the schema (the database must already exist):

   ```bash
   mysql --host=localhost --user=mail-workbench --password mail-workbench < database/schema.sql
   ```

   The command prompts for the password. The script creates tables but does
   not create the database or database user.

5. Use the connection helper from Python:

   ```python
   from python.database import connect

   connection = connect()
   try:
       with connection.cursor() as cursor:
           cursor.execute("SELECT 1")
           print(cursor.fetchone())
   finally:
       connection.close()
   ```

## Tests

Run the unit suite with the standard library test runner:

```bash
python -m unittest discover -s tests -v
```

The integration test is opt-in and uses the database configured in `.env`.
Install the schema first, then run:

```bash
RUN_DB_INTEGRATION=1 python -m unittest discover -s tests -v
```

It only performs a read-only connectivity query and checks for expected tables.
The destructive `database/drop-schema.sql` script is not used by tests; execute
it only when you intentionally want to remove all schema tables and data.

More details: [Database setup](docs/database.md) and [Testing](docs/testing.md).

## E-Mail-Import

Configure `MAIL_SOURCE_TYPE=mbox` and `MAIL_SOURCE_PATH` in `.env` to point to
one Thunderbird MBOX file. Only exact approved job-notification sender
addresses are imported; configure `JOB_SENDER_ALLOWLIST` to override the documented
defaults. For a database that already has the original schema, apply the
one-time migration from the repository root:

```bash
mysql --host=localhost --user=mail-workbench --password mail-workbench < database/migrations/002_email_import.sql
```

The MySQL client prompts for the password. After applying the schema or
migration, run the importer from the repository root:

```bash
python -m python.email_import.cli
```

The importer never modifies mailbox data and performs no archive or delete
actions. See [E-Mail-Import](docs/email-import.md) for Thunderbird storage,
filtering, migration, and adapter details.

## Status

<badge color="warning">Early development</badge>

The project is in early development. Phase 2 provides a local Thunderbird
import foundation; downstream job extraction and reporting are not implemented.

Features and architectural decisions may change as development progresses.

## License

License not yet specified.
