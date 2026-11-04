"""Command-line entry point for the configured Thunderbird MBOX import."""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

from python.database import PROJECT_ROOT, connect
from .importer import EmailImporter
from .thunderbird import ThunderbirdMboxSource


def main() -> int:
    """Run a read-only Thunderbird import and print aggregate counters."""
    load_dotenv(PROJECT_ROOT / ".env")
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    source_type = os.getenv("MAIL_SOURCE_TYPE", "mbox").strip().lower()
    if source_type != "mbox":
        raise SystemExit(f"Unsupported MAIL_SOURCE_TYPE: {source_type}")
    source_path = os.getenv("MAIL_SOURCE_PATH")
    if not source_path:
        raise SystemExit("MAIL_SOURCE_PATH is required for the Thunderbird import")
    configured_senders = os.getenv("JOB_SENDER_ALLOWLIST", "")
    senders = [sender.strip() for sender in configured_senders.split(",") if sender.strip()]
    if not senders:
        raise SystemExit("JOB_SENDER_ALLOWLIST is required; set comma-separated sender addresses in .env")

    source = ThunderbirdMboxSource(source_path)
    connection = connect()
    try:
        summary = EmailImporter(connection, senders).import_source(source)
    finally:
        connection.close()
    print(
        "Scanned {scanned}; filtered {filtered}; imported {imported}; "
        "duplicates {duplicates}; errors/warnings {errors}".format(**summary.__dict__)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
