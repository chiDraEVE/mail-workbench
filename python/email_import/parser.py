"""Parse RFC 5322/MIME bytes into the shared normalized email model."""

from __future__ import annotations

import hashlib
from datetime import timezone
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime

from .models import EmailRecord


def _body_parts(message) -> tuple[str | None, str | None]:
    """Extract text and HTML leaf parts while ignoring attachments."""
    text_parts: list[str] = []
    html_parts: list[str] = []
    for part in message.walk():
        if (
            part.is_multipart()
            or part.get_content_disposition() == "attachment"
            or part.get_filename()
        ):
            continue
        content_type = part.get_content_type()
        if content_type not in ("text/plain", "text/html"):
            continue
        try:
            content = part.get_content()
        except (LookupError, UnicodeError, ValueError):
            payload = part.get_payload(decode=True) or b""
            charset = part.get_content_charset() or "utf-8"
            content = payload.decode(charset, errors="replace")
        if isinstance(content, str):
            (text_parts if content_type == "text/plain" else html_parts).append(content)
    return "\n".join(text_parts) or None, "\n".join(html_parts) or None


def parse_message(raw: bytes) -> EmailRecord:
    """Parse raw RFC message bytes without rejecting recoverable defects.

    Dates are normalized to naive UTC for MySQL ``DATETIME``. Invalid or
    missing dates remain ``None`` and are reported as parser defects where
    applicable. Message-ID and content hash are both retained for deduplication.

    :param raw: Complete message bytes, excluding the MBOX envelope separator.
    :returns: A normalized :class:`EmailRecord`.
    """
    message = BytesParser(policy=policy.default).parsebytes(raw)
    sender_addresses = getaddresses(message.get_all("From", []))
    sender = next((address for _, address in sender_addresses if address), None)
    recipient_headers = sum(
        (message.get_all(name, []) for name in ("To", "Cc", "Bcc")), []
    )
    recipients = tuple(
        address for _, address in getaddresses(recipient_headers) if address
    )

    received_at = None
    date_header = message.get("Date")
    if date_header:
        try:
            parsed_date = parsedate_to_datetime(str(date_header))
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            received_at = parsed_date.astimezone(timezone.utc).replace(tzinfo=None)
        except (TypeError, ValueError, OverflowError):
            pass

    message_id = str(message.get("Message-ID", "")).strip() or None
    defects = tuple(
        f"{part.__class__.__name__}: {part}" for part in message.walk()
        for part in part.defects
    )
    if not sender:
        defects += ("Missing or invalid From header",)
    if not date_header or received_at is None:
        defects += ("Missing or invalid Date header",)
    if not message_id:
        defects += ("Missing Message-ID; content hash will be used for deduplication",)

    text_body, html_body = _body_parts(message)
    return EmailRecord(
        message_id=message_id,
        sender=sender,
        recipients=recipients,
        subject=str(message.get("Subject")) if message.get("Subject") is not None else None,
        received_at=received_at,
        text_body=text_body,
        html_body=html_body,
        content_hash=hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest(),
        defects=defects,
    )
