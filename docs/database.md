# Database setup

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

`database/drop-schema.sql` drops all project tables and their contents. It is
destructive; use it only after confirming the selected database is the intended
development database.
