"""Source-independent filtering, parsing, deduplication and persistence."""

from __future__ import annotations

import hashlib
import json
import logging
from email.utils import parseaddr
from typing import Iterable

from .models import EmailRecord, ImportSource, ImportSummary
from .parser import parse_message

LOGGER = logging.getLogger(__name__)

def sender_is_allowed(sender: str | None, allowed_senders: Iterable[str]) -> bool:
    """Return whether a sender mailbox exactly matches an approved address."""
    address = parseaddr(sender or "")[1].lower()
    return bool(address and address in {item.strip().lower() for item in allowed_senders})


def _existing_email(cursor, record: EmailRecord):
    """Find a previously imported email by its strongest available identity."""
    if record.message_id:
        cursor.execute(
            "SELECT id FROM email_messages WHERE message_id = %s LIMIT 1",
            (record.message_id,),
        )
        row = cursor.fetchone()
        if row:
            return row[0]
    cursor.execute(
        "SELECT id FROM email_messages WHERE content_hash = %s LIMIT 1",
        (record.content_hash,),
    )
    row = cursor.fetchone()
    return row[0] if row else None


# noinspection PyTypeChecker,PyCompatibility
class EmailImporter:
    """Import only messages from approved sender addresses into MySQL.

    The source adapter supplies raw message bytes; all classification, parsing
    and storage is shared by future import adapters such as IMAP.
    """

    def __init__(self, connection, allowed_senders: Iterable[str]) -> None:
        self.connection = connection
        self.allowed_senders = tuple(allowed_senders)

    def _record_failure(self, source: ImportSource, raw: bytes, detail: str) -> None:
        """Record a parse failure without storing the message as an email."""
        source_fingerprint = hashlib.sha256(source.source_id.encode()).hexdigest()
        source_key = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """INSERT INTO email_imports
                   (email_id, source_type, source_id, source_fingerprint, source_key,
                    import_status, error_detail)
                   VALUES (NULL, %s, %s, %s, %s, 'error', %s)
                   ON DUPLICATE KEY UPDATE import_status='error', error_detail=VALUES(error_detail)""",
                (source.source_type, source.source_id, source_fingerprint, source_key, detail[:60000]),
            )
            self.connection.commit()
        finally:
            cursor.close()

    def import_source(self, source: ImportSource) -> ImportSummary:
        """Import eligible messages and report counts without mailbox actions.

        :param source: Read-only adapter implementing :class:`ImportSource`.
        :returns: Counts of scanned, filtered, imported, duplicate and failed messages.
        """
        summary = ImportSummary()
        source_fingerprint = hashlib.sha256(source.source_id.encode()).hexdigest()
        for raw in source.iter_raw_messages():
            summary.scanned += 1
            try:
                record = parse_message(raw)
            except Exception as error:  # malformed individual messages must not abort the mailbox
                summary.errors += 1
                detail = f"{type(error).__name__}: {error}"
                LOGGER.exception("Could not parse a message from %s", source.source_id)
                self._record_failure(source, raw, detail)
                continue

            if not sender_is_allowed(record.sender, self.allowed_senders):
                summary.filtered += 1
                continue

            try:
                duplicate, status = self._persist(source, source_fingerprint, record)
            except Exception as error:
                self.connection.rollback()
                summary.errors += 1
                LOGGER.exception("Could not persist an eligible message from %s", source.source_id)
                self._record_failure(source, raw, f"{type(error).__name__}: {error}")
                continue
            if duplicate:
                summary.duplicates += 1
            else:
                summary.imported += 1
            if status == "imported_with_warnings":
                summary.errors += 1
        return summary

    def _persist(
        self, source: ImportSource, source_fingerprint: str, record: EmailRecord,
    ) -> tuple[bool, str]:
        """Insert or link one message and its source-specific import record."""
        cursor = self.connection.cursor()
        source_key = record.content_hash
        try:
            cursor.execute(
                """SELECT import_status FROM email_imports
                   WHERE source_type=%s AND source_fingerprint=%s AND source_key=%s""",
                (source.source_type, source_fingerprint, source_key),
            )
            prior = cursor.fetchone()
            if prior and prior[0] in ("imported", "imported_with_warnings", "duplicate"):
                self.connection.rollback()
                return True, prior[0]

            email_id = _existing_email(cursor, record)
            duplicate = email_id is not None
            if not duplicate:
                cursor.execute(
                    """INSERT INTO email_messages
                       (message_id, sender, recipients, subject, received_at, text_body,
                        html_body, content_hash)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        record.message_id, record.sender,
                        json.dumps(record.recipients, ensure_ascii=False), record.subject,
                        record.received_at, record.text_body, record.html_body,
                        record.content_hash,
                    ),
                )
                email_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO email_processing (email_id, processing_status) VALUES (%s, 'pending')",
                    (email_id,),
                )

            status = "duplicate" if duplicate else (
                "imported_with_warnings" if record.defects else "imported"
            )
            details = "; ".join(record.defects) or None
            cursor.execute(
                """INSERT INTO email_imports
                   (email_id, source_type, source_id, source_fingerprint, source_key,
                    import_status, error_detail)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE email_id=VALUES(email_id),
                       import_status=VALUES(import_status), error_detail=VALUES(error_detail),
                       imported_at=CURRENT_TIMESTAMP""",
                (
                    email_id, source.source_type, source.source_id, source_fingerprint,
                    source_key, status, details,
                ),
            )
            self.connection.commit()
            return duplicate, status
        finally:
            cursor.close()
