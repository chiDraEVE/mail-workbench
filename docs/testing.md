# Testing

Tests use Python's built-in `unittest` runner; no extra test framework is needed.
Install project dependencies and run unit tests using the commands in the
[README](../README.md#getting-started) and [Tests](../README.md#tests) sections.
Run shell commands from the repository root with the project virtual
environment active.

Unit tests cover connection configuration, exact sender matching, MIME
extraction, malformed metadata and the read-only Thunderbird MBOX adapter.
Fixtures in `tests/fixtures/` are synthetic and use reserved `.invalid`
addresses; they contain no mailbox data.

## Integration test

Integration tests are skipped unless `RUN_DB_INTEGRATION=1` is set. They check
the schema and import the anonymized fixture into MySQL, verifying sender
filtering and a repeated import. The import test removes only the rows it created.
Create the database and apply the current `database/schema.sql` for a new
database. Use migration `002_email_import.sql` only when upgrading a database
that still has the earlier email schema; do not apply both. Then run the
integration test command in the [README](../README.md#tests), from the repository
root.

The configured database must be dedicated to development or testing. The
integration test never runs `database/drop-schema.sql` and never reads the
configured real Thunderbird mailbox.
