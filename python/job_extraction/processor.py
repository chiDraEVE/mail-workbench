"""Persist extracted job candidates and update email processing states."""

from __future__ import annotations

import logging

from python.email_import.models import EmailRecord
from .extractors import extractor_for_sender
from .models import JobCandidate, ProcessingSummary

LOGGER = logging.getLogger(__name__)


class EmailJobProcessor:
    """Process pending imported emails once and link discovered jobs to them."""

    def __init__(self, connection, batch_size: int = 100) -> None:
        self.connection = connection
        self.batch_size = batch_size

    def process_pending(self) -> ProcessingSummary:
        summary = ProcessingSummary()
        while True:
            cursor = self.connection.cursor()
            try:
                cursor.execute(
                    """SELECT m.id, m.sender, m.subject, m.received_at,
                              m.text_body, m.html_body
                       FROM email_messages AS m
                       JOIN email_processing AS p ON p.email_id=m.id
                       WHERE p.processing_status='pending'
                       ORDER BY m.id LIMIT %s""",
                    (self.batch_size,),
                )
                rows = cursor.fetchall()
            finally:
                cursor.close()
            if not rows:
                break

            for email_id, sender, subject, received_at, text_body, html_body in rows:
                extractor = extractor_for_sender(sender)
                if extractor is None:
                    self._set_status(email_id, "unsupported", None)
                    summary.unsupported_senders += 1
                    summary.emails_processed += 1
                    continue

                email = EmailRecord(
                    message_id=None,
                    sender=sender,
                    recipients=(),
                    subject=subject,
                    received_at=received_at,
                    text_body=text_body,
                    html_body=html_body,
                    content_hash="",
                )
                try:
                    candidates = extractor.extract(email)
                    self._save_candidates(email_id, candidates)
                    state = "processed" if candidates else "no_jobs"
                    self._set_status(email_id, state, None)
                    summary.jobs_found += len(candidates)
                    summary.emails_without_jobs += not candidates
                    summary.emails_processed += 1
                except Exception as error:
                    self.connection.rollback()
                    detail = f"{type(error).__name__}: {error}"
                    LOGGER.exception("Could not extract jobs from email %s", email_id)
                    self._set_status(email_id, "error", detail)
                    summary.errors += 1
                    summary.emails_processed += 1
        return summary

    def _save_candidates(self, email_id: int, candidates: list[JobCandidate]) -> None:
        cursor = self.connection.cursor()
        try:
            for candidate in candidates:
                cursor.execute(
                    "SELECT id FROM job_publications WHERE url=%s ORDER BY id LIMIT 1",
                    (candidate.url,),
                )
                existing = cursor.fetchone()
                if existing:
                    publication_id = existing[0]
                    cursor.execute(
                        "UPDATE job_publications SET last_seen_at=CURRENT_TIMESTAMP WHERE id=%s",
                        (publication_id,),
                    )
                else:
                    company_id = self._company_id(cursor, candidate.company)
                    cursor.execute(
                        """INSERT INTO jobs
                           (title, employer_company_id, location, description,
                            employment_type, work_mode)
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (
                            candidate.title, company_id, candidate.location,
                            candidate.description, candidate.employment_type,
                            candidate.work_mode,
                        ),
                    )
                    job_id = cursor.lastrowid
                    cursor.execute(
                        """INSERT INTO job_publications
                           (job_id, platform, url, link_text)
                           VALUES (%s, %s, %s, %s)""",
                        (job_id, candidate.platform, candidate.url, candidate.title),
                    )
                    publication_id = cursor.lastrowid
                cursor.execute(
                    """INSERT IGNORE INTO email_observations (email_id, publication_id)
                       VALUES (%s, %s)""",
                    (email_id, publication_id),
                )
            self.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def _company_id(cursor, name: str | None) -> int | None:
        if not name:
            return None
        normalized = " ".join(name.split()).casefold()[:255]
        cursor.execute(
            "SELECT id FROM companies WHERE normalized_name=%s ORDER BY id LIMIT 1",
            (normalized,),
        )
        existing = cursor.fetchone()
        if existing:
            return existing[0]
        cursor.execute(
            "INSERT INTO companies (name, normalized_name) VALUES (%s, %s)",
            (name[:255], normalized),
        )
        return cursor.lastrowid

    def _set_status(self, email_id: int, status: str, detail: str | None) -> None:
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """UPDATE email_processing
                   SET processing_status=%s, error_detail=%s
                   WHERE email_id=%s""",
                (status, detail[:60000] if detail else None, email_id),
            )
            self.connection.commit()
        finally:
            cursor.close()
