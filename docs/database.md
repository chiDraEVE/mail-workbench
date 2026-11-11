# Database setup

**Languages:** English · [Deutsch](database.de.md) · [German README](../README.de.md)

Mail Workbench uses MySQL and the tables defined in [`../database/schema.sql`](../database/schema.sql).
Use Python 3.10 or newer, a MySQL 8.0-compatible server and the dependencies in
[`../requirements.txt`](../requirements.txt).

## Configure credentials

Copy `.env.example` to `.env` in the repository root. Set these values:

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `DB_NAME` | Yes | — | Existing database name |
| `DB_USER` | Yes | — | MySQL account |
| `DB_PASSWORD` | Yes | — | Account password |
| `DB_HOST` | No | `localhost` | MySQL server host |
| `DB_PORT` | No | `3306` | MySQL server port |

Environment variables already exported by the process take precedence over
values in `.env`. Keep `.env` private; Git ignores it.

## Create the database and apply the schema

Create an empty database and an account permitted to use it, then follow the
root-level [Getting started](../README.md#getting-started) instructions to
apply the schema. Run the documented shell commands from the repository root;
the MySQL client prompts for the password. The schema file creates tables in
the selected database and does not create the database itself. Running it a
second time will fail when its tables already exist.

## Connect from Python

```python
from python.database import connect

connection = connect()
try:
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT 1")
        print(cursor.fetchone())
    finally:
        cursor.close()
finally:
    connection.close()
```

`connect()` raises a `RuntimeError` listing any missing required settings. It
does not log or include credential values in errors. Close both cursors and
connections when finished.

## Local job overview

The project-root `index.php` uses the same `DB_HOST`, `DB_PORT`, `DB_NAME`,
`DB_USER` and `DB_PASSWORD` settings. Apache environment variables take
precedence; PHP can fall back to `.env` only when the web-server user can read
that file. The overview displays jobs and their source links, supports sorting
and platform/time filters, and lets you manually correct a job's title,
company, location and work mode. Those corrections update the existing rows in
`jobs` and `companies`.

Listing-specific URLs, platforms and external IDs are stored in
`job_publications`. The external ID is derived from a known URL query parameter
(such as Indeed's `jk`) or the last path component when an email is processed.

`database/drop-schema.sql` drops all project tables and their contents. It is
destructive; use it only after confirming the selected database is the intended
development database.

To delete the data while keeping the schema, use
[`../database/clear-data.sql`](../database/clear-data.sql). The script first
prints the selected database name, then deletes all email, job and company data.
Check the database name before running it. You do not need to apply
`schema.sql` again afterward.
