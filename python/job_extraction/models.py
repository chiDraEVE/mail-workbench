"""Value objects for extracted job listings and processing summaries."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class JobCandidate:
    """A job listing found in an email message."""

    title: str
    url: str
    platform: str
    company: str | None = None
    location: str | None = None
    employment_type: str | None = None
    work_mode: str | None = None
    description: str | None = None


@dataclass
class ProcessingSummary:
    """Counters for downstream processing of imported email messages."""

    emails_processed: int = 0
    jobs_found: int = 0
    emails_without_jobs: int = 0
    unsupported_senders: int = 0
    errors: int = 0
