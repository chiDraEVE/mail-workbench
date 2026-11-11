"""Conservative canonicalization for job publication URLs."""

from __future__ import annotations

import re
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit


_TRACKING_PARAMETERS = {
    "gclid", "dclid", "fbclid", "msclkid", "twclid", "yclid",
    "mc_cid", "mc_eid", "ref", "referrer",
}
_PERCENT_ESCAPE = re.compile(r"%([0-9a-fA-F]{2})")
_EXTERNAL_ID_KEYS = {
    "jk", "jobid", "job_id", "job-id", "postingid", "posting_id",
    "vacancyid", "vacancy_id", "id",
}
_UNRESERVED = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
)


def _normalize_percent_escapes(value: str) -> str:
    """Decode escaped unreserved characters and uppercase other escapes."""
    def replace(match: re.Match[str]) -> str:
        character = chr(int(match.group(1), 16))
        return character if character in _UNRESERVED else "%" + match.group(1).upper()

    return _PERCENT_ESCAPE.sub(replace, value)


def normalize_job_url(url: str) -> str:
    """Normalize equivalent URL spellings while preserving job identifiers.

    Host casing, default ports, fragments, common tracking parameters, query
    ordering, and percent-escape casing do not distinguish publications. The
    scheme, path, non-tracking query parameters, and ``www`` host prefix are
    retained because they can identify different resources.
    """
    parts = urlsplit(url.strip())
    scheme = parts.scheme.lower()
    try:
        hostname = (parts.hostname or "").encode("idna").decode("ascii").lower()
        port = parts.port
    except (UnicodeError, ValueError):
        # Keep malformed legacy values usable for exact matching and review.
        return url.strip()
    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"
    if port is not None and not (
        (scheme == "http" and port == 80)
        or (scheme == "https" and port == 443)
    ):
        hostname = f"{hostname}:{port}"

    path = _normalize_percent_escapes(parts.path)
    query_items = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
        and key.lower() not in _TRACKING_PARAMETERS
    ]
    query_items.sort(key=lambda item: (item[0].casefold(), item[1]))
    query = urlencode(query_items, doseq=True)
    return urlunsplit((scheme, hostname, path, query, ""))


def external_job_id(url: str) -> str | None:
    """Derive a likely platform listing ID from a URL.

    Prefer known query parameters (including Indeed's ``jk``); when none is
    present, use the last non-empty path segment.
    """
    try:
        parts = urlsplit(url.strip())
        for key, value in parse_qsl(parts.query, keep_blank_values=True):
            if key.casefold() in _EXTERNAL_ID_KEYS and value.strip():
                return unquote(value).strip()[:255]
        segments = [segment for segment in parts.path.split("/") if segment]
        if segments:
            return unquote(segments[-1]).strip()[:255] or None
    except (ValueError, UnicodeError):
        return None
    return None
