# Testing

Tests use Python's built-in `unittest` runner; no extra test framework is needed.
Install project dependencies from the repository root and run unit tests:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Unit tests isolate the connection helper from MySQL and verify configuration
validation and connection arguments.

## Integration test

The integration test is skipped unless `RUN_DB_INTEGRATION=1` is set. It opens
the MySQL database configured in `.env`, issues `SELECT 1`, and checks that
several initial schema tables exist. It does not create, update or delete data.
Create the database and apply `database/schema.sql` before running:

```bash
RUN_DB_INTEGRATION=1 python -m unittest discover -s tests -v
```

The configured database must be dedicated to development or testing. The
integration test never runs `database/drop-schema.sql`.
