"""Unit tests for the source-independent email import pipeline."""

from __future__ import annotations

import mailbox
import os
import unittest
import uuid
from pathlib import Path

from python.email_import.importer import sender_is_allowed
from python.email_import.parser import parse_message
from python.email_import.thunderbird import ThunderbirdMboxSource
from python.email_import.importer import EmailImporter


FIXTURE = Path(__file__).parent / "fixtures" / "thunderbird_sample.mbox"
TEST_ALLOWED_SENDERS = ("jobs@example.invalid", "alerts@example.invalid")


class SenderFilterTests(unittest.TestCase):
    """Check safe exact-domain and subdomain matching."""

    def test_accepts_known_exact_sender_with_display_name(self) -> None:
        """Accept exact job alert addresses regardless of display name."""
        self.assertTrue(sender_is_allowed("Job Alerts <jobs@example.invalid>", TEST_ALLOWED_SENDERS))
        self.assertTrue(sender_is_allowed("alerts@example.invalid", TEST_ALLOWED_SENDERS))

    def test_rejects_lookalike_and_non_job_addresses(self) -> None:
        """Reject unknown addresses on approved platforms and unrelated senders."""
        for sender in (
            "unknown@example.invalid", "friend@example.net", "no-address", None
        ):
            with self.subTest(sender=sender):
                self.assertFalse(sender_is_allowed(sender, TEST_ALLOWED_SENDERS))


class MessageParserTests(unittest.TestCase):
    """Cover metadata, multipart bodies and incomplete messages."""

    def setUp(self) -> None:
        """Read one anonymized multipart message from the fixture."""
        box = mailbox.mbox(FIXTURE, create=False)
        try:
            messages = list(box)
        finally:
            box.close()
        self.multipart = messages[2].as_bytes()
        self.incomplete = messages[3].as_bytes()

    def test_extracts_metadata_and_both_mime_alternatives(self) -> None:
        """Decode sender, recipients, date, plain text and HTML content."""
        record = parse_message(self.multipart)
        self.assertEqual(record.message_id, "<fixture-job-003@example.invalid>")
        self.assertEqual(record.sender, "jobs@example.invalid")
        self.assertEqual(record.recipients, ("candidate@example.invalid", "copy@example.invalid"))
        self.assertIn("Plain text", record.text_body or "")
        self.assertIn("<html>", record.html_body or "")
        self.assertIsNotNone(record.received_at)
        self.assertEqual(len(record.content_hash), 64)

    def test_missing_message_id_and_date_are_recoverable(self) -> None:
        """Retain an otherwise valid job message and report absent metadata."""
        record = parse_message(self.incomplete)
        self.assertIsNone(record.message_id)
        self.assertIsNone(record.received_at)
        self.assertTrue(any("Message-ID" in defect for defect in record.defects))
        self.assertTrue(any("Date" in defect for defect in record.defects))


class ThunderbirdSourceTests(unittest.TestCase):
    """Ensure the adapter reads mailbox messages without writing to them."""

    def test_reads_all_fixture_messages(self) -> None:
        """Expose each message as raw RFC bytes from the configured MBOX."""
        source = ThunderbirdMboxSource(FIXTURE)
        self.assertEqual(source.source_type, "thunderbird_mbox")
        self.assertEqual(len(list(source.iter_raw_messages())), 4)


@unittest.skipUnless(
    os.getenv("RUN_DB_INTEGRATION") == "1",
    "Set RUN_DB_INTEGRATION=1 to run against the configured MySQL database.",
)
class EmailImportIntegrationTests(unittest.TestCase):
    """Exercise fixture import, filtering, deduplication and cleanup in MySQL."""

    def test_fixture_import_is_filtered_and_idempotent(self) -> None:
        """Persist anonymized job messages only and safely repeat the same source."""
        from python.database import connect

        source = ThunderbirdMboxSource(FIXTURE)
        source.source_id = f"{source.source_id}#integration-{uuid.uuid4()}"
        connection = connect()
        cursor = connection.cursor()
        try:
            first = EmailImporter(connection, TEST_ALLOWED_SENDERS).import_source(source)
            self.assertEqual((first.scanned, first.filtered, first.imported), (4, 1, 3))
            second = EmailImporter(connection, TEST_ALLOWED_SENDERS).import_source(source)
            self.assertEqual(second.imported, 0)
            self.assertEqual(second.duplicates, 3)

            cursor.execute(
                "SELECT email_id, import_status FROM email_imports WHERE source_id=%s",
                (source.source_id,),
            )
            linked = cursor.fetchall()
            self.assertEqual(len(linked), 3)
            self.assertTrue(all(email_id is not None for email_id, _ in linked))
        finally:
            cursor.execute(
                "SELECT email_id, import_status FROM email_imports WHERE source_id=%s",
                (source.source_id,),
            )
            owned_ids = {
                email_id for email_id, status in cursor.fetchall()
                if email_id is not None and status != "duplicate"
            }
            cursor.execute("DELETE FROM email_imports WHERE source_id=%s", (source.source_id,))
            if owned_ids:
                placeholders = ",".join(["%s"] * len(owned_ids))
                cursor.execute(
                    f"DELETE FROM email_processing WHERE email_id IN ({placeholders})",
                    tuple(owned_ids),
                )
                cursor.execute(
                    f"DELETE FROM email_messages WHERE id IN ({placeholders})",
                    tuple(owned_ids),
                )
            connection.commit()
            cursor.close()
            connection.close()
