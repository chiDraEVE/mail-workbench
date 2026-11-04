"""Shared value objects and interfaces used by email source adapters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Protocol


@dataclass(frozen=True)
class EmailRecord:
    """Normalized message data independent of its source format.

    :param message_id: RFC Message-ID, when supplied by the sender.
    :param sender: Parsed sender mailbox address.
    :param recipients: Parsed To, Cc and Bcc addresses.
    :param subject: Decoded subject, if present.
    :param received_at: Date header converted to a naive UTC datetime.
    :param text_body: Decoded plain text body, when present.
    :param html_body: Decoded HTML body, when present.
    :param content_hash: SHA-256 digest of the original RFC message bytes.
    :param defects: Parser notices for malformed MIME/header data.
    """

    message_id: str | None
    sender: str | None
    recipients: tuple[str, ...]
    subject: str | None
    received_at: datetime | None
    text_body: str | None
    html_body: str | None
    content_hash: str
    defects: tuple[str, ...] = ()


class ImportSource(Protocol):
    """Read-only interface implemented by MBOX, IMAP and future adapters."""

    source_type: str
    source_id: str

    def iter_raw_messages(self) -> Iterator[bytes]:
        """Yield complete RFC message bytes without modifying the source."""


@dataclass
class ImportSummary:
    """Counters describing one run of the source-independent importer."""

    scanned: int = 0
    filtered: int = 0
    imported: int = 0
    duplicates: int = 0
    errors: int = 0
