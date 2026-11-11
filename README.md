# Mail Workbench

<a id="top"></a>

**Languages:** English · [Deutsch](README.de.md)

## Contents

- [Motivation](#motivation)
- [Goals](#goals)
- [Planned architecture](#planned-architecture)
- [Development roadmap](#development-roadmap)
- [Development principles](#development-principles)
- [Getting started](#getting-started)
- [Tests](#tests)
- [Email import](#e-mail-import)
- [Trello integration](#trello-integration)
- [Status](#status)
- [License](#license)

**Documentation:** [Database setup (EN)](docs/database.md) · [Datenbank einrichten (DE)](docs/database.de.md) · [Testing (EN)](docs/testing.md) · [Tests (DE)](docs/testing.de.md) · [Email import (EN)](docs/email-import.en.md) · [E-Mail-Import (DE)](docs/email-import.md) · [Trello integration (EN)](docs/trello-integration.md) · [Trello-Integration (DE)](docs/trello-integration.de.md)

A local, modular automation project for processing emails and extracting useful information from different sources.

## Motivation

My inbox contains a growing number of automated emails that require manual review. Job alerts are a particular example.

Processing these emails manually involves several repetitive tasks:

- Extracting job listings and their URLs
- Identifying duplicate listings across different platforms
- Recognizing reposted or potentially outdated job advertisements
- Checking whether a listing is still available
- Collecting relevant information in a structured format
- Preparing listings for manual review and further processing

The goal of Mail Workbench is to automate the repetitive parts of this workflow while keeping important decisions under manual control.

<p align="right"><a href="#top">Back to top ↑</a></p>

## Goals

The project is intended to provide:

- **Email processing:** Read and parse locally available email data.
- **Structured storage:** Store extracted information in a relational database.
- **Duplicate detection:** Identify identical or similar listings across different sources.
- **Availability checks:** Collect information about whether a job listing is still accessible.
- **Reports:** Generate clear reports with links to the original listings.
- **Modularity:** Support different email-processing workflows through separate modules.

The initial focus is job advertisement processing. Additional modules may later handle security reports from NinjaFirewall and DMARC aggregate reports.

<p align="right"><a href="#top">Back to top ↑</a></p>

## Planned Architecture

The initial architecture is based on the following components:

| Component               | Technology                   |
|-------------------------|------------------------------|
| Email processing        | Python                       |
| Database                | MySQL                        |
| Reporting               | PHP / HTML                   |
| Version control         | Git                          |
| Development environment | Ubuntu 24.04 / IntelliJ IDEA |

The current local PHP page reports stored jobs and supports manual corrections. The processing logic remains independent of the presentation layer.

<p align="right"><a href="#top">Back to top ↑</a></p>

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
- [x] Extract job listings and their URLs from supported email templates

### Phase 3 – Job listing analysis

- [x] Normalize URLs
- [x] Recognize the same publication by its normalized URL
- [x] Merge listings with matching title and company
- [x] Track first and last observation for each publication

### Phase 4 – Reporting

- [x] Generate a database overview with one entry per job and clickable listing links
- [x] Show the subject and date of related emails as context
- [x] Add sorting and platform/time filters for manual review
- [x] Allow manual editing of title, company, location and work mode

### Phase 5 – Trello integration and optional enrichment

- [x] Read the configured Trello board's lists and cards in the reporting page
- [x] Read the API key, token and board ID from local `.env`; fetch list IDs dynamically
- [ ] Send manually selected listings to Trello boards
- [ ] Optionally fetch platform descriptions and compare listings across platforms
- [ ] Optionally check listing availability

### Future ideas

- Web-based interface
- Integration with existing job application workflows
- NinjaFirewall report processing
- DMARC aggregate report processing
- Optional AI-assisted analysis

<p align="right"><a href="#top">Back to top ↑</a></p>

## Trello integration

Phase 5 will send listings selected in the reporting page to Trello. The API
credentials, token creation steps, relevant endpoints and planned local
configuration are described in the [Trello integration guide](docs/trello-integration.md).
The [German guide](docs/trello-integration.de.md) is also available.

<p align="right"><a href="#top">Back to top ↑</a></p>

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

<p align="right"><a href="#top">Back to top ↑</a></p>

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

<p align="right"><a href="#top">Back to top ↑</a></p>
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

<p align="right"><a href="#top">Back to top ↑</a></p>

## E-Mail-Import

Configure `MAIL_SOURCE_TYPE=mbox`, `MAIL_SOURCE_PATH`, and the required
`JOB_SENDER_ALLOWLIST` in `.env` to point to one Thunderbird MBOX file and list
the exact sender addresses to import. Sender addresses are kept in the ignored
local `.env` file and are not stored in the database.

For a new database, apply the current `database/schema.sql` as described in
[Database setup](docs/database.md). If an existing database still has the
earlier email tables, apply the one-time migration from the repository root
instead:

```bash
mysql --host=localhost --user=mail-workbench --password mail-workbench < database/migrations/002_email_import.sql
```

Do not apply both scripts to the same database. The MySQL client prompts for
the password. After setting up the database, run the importer from the
repository root:

```bash
python -m python.email_import.cli
```

The importer never modifies mailbox data and performs no archive or delete
actions. It extracts supported job alerts and links each listing back to its
source email. See [Email import](docs/email-import.en.md) for Thunderbird
storage, filtering, extraction, migration, and adapter details. [Die deutsche
Fassung](docs/email-import.md) is also available.

<p align="right"><a href="#top">Back to top ↑</a></p>

## Status

<badge color="warning">Early development</badge>

The project is in early development. Local Thunderbird import, job extraction,
URL normalization, basic matching by URL or matching title and company, a PHP
reporting page with clickable links, filters and manual editing, and
read-only display of Trello lists and cards are implemented. Sending selected
jobs to Trello remains to be implemented. Links between listings and their
source emails are stored in the database.

Features and architectural decisions may change as development progresses.

<p align="right"><a href="#top">Back to top ↑</a></p>

## License

License not yet specified.

<p align="right"><a href="#top">Back to top ↑</a></p>
