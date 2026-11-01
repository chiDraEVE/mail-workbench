"""Unit and opt-in integration tests for database access."""

from __future__ import annotations

import os
import unittest
from unittest.mock import MagicMock, patch

from python import database


class ConnectUnitTests(unittest.TestCase):
    """Verify configuration validation and MySQL connection arguments."""

    def setUp(self) -> None:
        """Remove database settings so each test controls its configuration."""
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.dotenv = patch.object(database, "load_dotenv")
        self.dotenv.start()
        self.addCleanup(self.dotenv.stop)

    def test_required_settings_are_reported_without_exposing_values(self) -> None:
        """Reject incomplete settings with the names of missing fields."""
        with self.assertRaisesRegex(RuntimeError, "DB_NAME, DB_USER, DB_PASSWORD"):
            database.connect()

    @patch.dict(os.environ, {
        "DB_NAME": "sample", "DB_USER": "reader", "DB_PASSWORD": "secret"
    }, clear=True)
    @patch("mysql.connector.connect", create=True)
    def test_connection_uses_required_values_and_default_host_port(
        self, connector: MagicMock
    ) -> None:
        """Pass credentials and default network settings to Connector/Python."""
        database.connect()
        connector.assert_called_once_with(
            host="localhost", port=3306, database="sample", user="reader",
            password="secret",
        )


@unittest.skipUnless(
    os.getenv("RUN_DB_INTEGRATION") == "1",
    "Set RUN_DB_INTEGRATION=1 to run tests against the configured MySQL database.",
)
class DatabaseIntegrationTests(unittest.TestCase):
    """Check connectivity and expected schema tables in configured MySQL."""

    def test_database_connection_and_schema(self) -> None:
        """Run a harmless query and confirm the initial schema is installed."""
        connection = database.connect()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT 1")
                self.assertEqual(cursor.fetchone(), (1,))
                cursor.execute("SHOW TABLES")
                tables = {row[0] for row in cursor.fetchall()}
                self.assertTrue(
                    {"companies", "jobs", "job_publications", "email_messages"}
                    <= tables
                )
            finally:
                cursor.close()
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
