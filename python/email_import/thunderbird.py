"""Read local Thunderbird MBOX folders without changing mailbox data."""

from __future__ import annotations

import mailbox
from pathlib import Path
from typing import Iterator


class ThunderbirdMboxSource:
    """Expose one Thunderbird MBOX file through the generic source interface.

    Thunderbird stores POP and Local Folders mail below ``Mail/`` and cached
    synchronized IMAP folders below ``ImapMail/``. The MBOX itself is the
    extensionless folder file; ``.msf`` files are indexes, not message data.

    :param path: Path to one MBOX folder file.
    :raises FileNotFoundError: If the configured path is absent.
    :raises ValueError: If the path is not a regular file.
    """

    source_type = "thunderbird_mbox"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve(strict=True)
        if not self.path.is_file():
            raise ValueError(f"MBOX source is not a regular file: {self.path}")
        self.source_id = str(self.path)

    def iter_raw_messages(self) -> Iterator[bytes]:
        """Yield message bytes from the MBOX while opening it read-only."""
        box = mailbox.mbox(self.path, create=False)
        try:
            for message in box:
                yield message.as_bytes()
        finally:
            box.close()
