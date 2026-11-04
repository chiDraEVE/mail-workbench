"""Portal-specific HTML extractors for job listings in email messages."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from email.utils import parseaddr
from typing import Iterable
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup, Tag

from python.email_import.models import EmailRecord
from .models import JobCandidate


_GENERIC_LINK_LABELS = {
    "stelle ansehen", "jetzt bewerben", "ich bin interessiert", "mehr erfahren",
    "mehr dazu", "job ansehen", "alle jobs anzeigen", "alle vorschläge ansehen",
    "apply now", "view job", "view job posting", "read more",
}
_TRACKING_OR_FOOTER_TEXT = {
    "im browser ansehen", "im browser öffnen", "datenschutz", "impressum",
    "kontakt", "abbestellen", "abmelden", "einstellungen", "häufige fragen",
}
_INSTAFFO_CHAT_TITLE = re.compile(
    r"(?:es geht um den folgenden job|es geht um folgenden job)\s*:\s*(.+?)(?:[.!\n]|$)",
    re.IGNORECASE,
)


def _clean_text(value: str | None) -> str | None:
    if not value:
        return None
    value = " ".join(value.replace("\xa0", " ").split()).strip(" \t\r\n-–—|•")
    if not value:
        return None
    return value


def _valid_anchor(anchor: Tag, allow_generic: bool = False) -> tuple[str, str] | None:
    """Return a usable absolute URL and label for an HTML anchor."""
    href = _clean_text(str(anchor.get("href", "")))
    label = _clean_text(anchor.get_text(" ", strip=True))
    if not href or not label:
        return None
    parsed = urlsplit(href)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return None
    normalized_label = label.casefold().rstrip(" ➔→›")
    if not allow_generic and (
        normalized_label in _GENERIC_LINK_LABELS
        or normalized_label in _TRACKING_OR_FOOTER_TEXT
    ):
        return None
    if len(label) < 4:
        return None
    label = re.sub(r"^\s*\d+[.)]\s*", "", label)
    return (href, label) if label else None


def _candidate(
    anchor: Tag,
    platform: str,
    *,
    title: str | None = None,
    company: str | None = None,
    location: str | None = None,
    employment_type: str | None = None,
    work_mode: str | None = None,
    description: str | None = None,
) -> JobCandidate | None:
    valid = _valid_anchor(anchor, allow_generic=title is not None)
    if not valid:
        return None
    url, label = valid
    title = _clean_text(title) or label
    title = re.sub(r"^\s*\d+[.)]\s*", "", title)
    if len(title) < 4 or title.casefold() in _GENERIC_LINK_LABELS:
        return None
    return JobCandidate(
        title=title[:500],
        url=url,
        platform=platform,
        company=_clean_text(company),
        location=_clean_text(location),
        employment_type=_clean_text(employment_type),
        work_mode=_clean_text(work_mode),
        description=_clean_text(description),
    )


class JobExtractor(ABC):
    """Common interface implemented by each email-template extractor."""

    platform: str

    def extract(self, email: EmailRecord) -> list[JobCandidate]:
        html = email.html_body or ""
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        candidates = self.extract_from_soup(soup, email)
        return _unique_candidates(candidates)

    @abstractmethod
    def extract_from_soup(
        self, soup: BeautifulSoup, email: EmailRecord,
    ) -> Iterable[JobCandidate | None]:
        """Extract candidates from a parsed email body."""


def _unique_candidates(candidates: Iterable[JobCandidate | None]) -> list[JobCandidate]:
    unique: list[JobCandidate] = []
    seen: set[str] = set()
    for item in candidates:
        if item is None or item.url in seen:
            continue
        seen.add(item.url)
        unique.append(item)
    return unique


class ArbeitsagenturExtractor(JobExtractor):
    platform = "arbeitsagentur"

    def extract_from_soup(self, soup: BeautifulSoup, email: EmailRecord):
        for heading in soup.find_all(["h2", "h3"]):
            anchor = heading.find("a", href=True)
            if anchor:
                yield _candidate(anchor, self.platform, title=heading.get_text(" ", strip=True))


class IndeedExtractor(JobExtractor):
    platform = "indeed"

    def extract_from_soup(self, soup: BeautifulSoup, email: EmailRecord):
        anchors = list(soup.select("td.j-e a[href]"))
        if not anchors:
            for anchor in soup.find_all("a", href=True):
                url = str(anchor.get("href", ""))
                path = urlsplit(url).path.lower()
                label = _clean_text(anchor.get_text(" ", strip=True)) or ""
                if ("/clk/dl" in path or "/pagead/" in path) and len(label) >= 12:
                    anchors.append(anchor)

        for anchor in anchors:
            card = anchor.find_parent("table")
            company = location = description = None
            if card:
                company_node = card.select_one("td.j-i .j-j")
                location_node = card.select_one("td.j-i .j-m")
                description_node = card.select_one("td.j-n")
                company = company_node.get_text(" ", strip=True) if company_node else None
                location = location_node.get_text(" ", strip=True) if location_node else None
                description = description_node.get_text(" ", strip=True) if description_node else None
            yield _candidate(
                anchor, self.platform, company=company, location=location,
                description=description,
            )


class LinkedInExtractor(JobExtractor):
    platform = "linkedin"

    def extract_from_soup(self, soup: BeautifulSoup, email: EmailRecord):
        anchors = list(soup.select("a.font-bold[href]"))
        if not anchors:
            for anchor in soup.find_all("a", href=True):
                path = urlsplit(str(anchor.get("href", ""))).path.lower()
                if "/jobs/view/" in path or "/comm/jobs/view/" in path:
                    anchors.append(anchor)
        for anchor in anchors:
            yield _candidate(anchor, self.platform)


class XingExtractor(JobExtractor):
    platform = "xing"

    def extract_from_soup(self, soup: BeautifulSoup, email: EmailRecord):
        anchors: list[Tag] = []
        for title in soup.select("span.DarkmodePetrolLink"):
            anchor = title.find_parent("a", href=True)
            if anchor:
                anchors.append(anchor)
        if not anchors:
            for anchor in soup.find_all("a", href=True):
                path = urlsplit(str(anchor.get("href", ""))).path.lower()
                label = _clean_text(anchor.get_text(" ", strip=True)) or ""
                if path.startswith("/m/") and len(label) >= 12:
                    anchors.append(anchor)
        for anchor in anchors:
            title_node = anchor.select_one("span.DarkmodePetrolLink")
            title = title_node.get_text(" ", strip=True) if title_node else None
            yield _candidate(anchor, self.platform, title=title)


class StepstoneExtractor(JobExtractor):
    platform = "stepstone"

    def extract_from_soup(self, soup: BeautifulSoup, email: EmailRecord):
        title = _clean_text(email.subject)
        if not title or title.casefold() in {"stepstone", "job alert", "job recommendation"}:
            title = None
        if not title:
            for heading in soup.find_all(["h1", "h2", "h3"]):
                candidate_title = _clean_text(heading.get_text(" ", strip=True))
                if candidate_title and candidate_title.casefold() not in {"stepstone", "jobbenachrichtigung"}:
                    title = candidate_title
                    break
        if not title:
            body_text = soup.get_text(" ", strip=True)
            before_greeting = re.split(r"\bHallo\b", body_text, maxsplit=1, flags=re.IGNORECASE)[0]
            title = _clean_text(before_greeting)
            if title:
                title = re.sub(r"^(?:stepstone|jobplattform)\s+", "", title, flags=re.IGNORECASE)
            if title and len(title) > 200:
                title = None

        cta = next(
            (anchor for anchor in soup.find_all("a", href=True)
             if (_clean_text(anchor.get_text(" ", strip=True)) or "").casefold() == "ich bin interessiert"),
            None,
        )
        if cta and title:
            yield _candidate(cta, self.platform, title=title)


class InstaffoExtractor(JobExtractor):
    """Extract public job links, while ignoring candidate chat links."""

    platform = "instaffo"

    def extract_from_soup(self, soup: BeautifulSoup, email: EmailRecord):
        for anchor in soup.find_all("a", href=True):
            decoded = unquote(str(anchor.get("href", ""))).lower()
            path = urlsplit(str(anchor.get("href", ""))).path.lower()
            if "/candidate/job/" in decoded or "candidate%2fjob" in decoded:
                continue
            if re.search(r"/(?:jobs?|stellenangebote?)/", path):
                yield _candidate(anchor, self.platform)


class StellenanzeigenExtractor(JobExtractor):
    platform = "stellenanzeigen.de"

    def extract_from_soup(self, soup: BeautifulSoup, email: EmailRecord):
        for anchor in soup.find_all("a", href=True):
            path = urlsplit(str(anchor.get("href", ""))).path.lower()
            if re.search(r"/(?:job|jobs|stellenangebot|stellenangebote)/", path):
                yield _candidate(anchor, self.platform)


class WorkwiseExtractor(JobExtractor):
    platform = "workwise"

    def extract_from_soup(self, soup: BeautifulSoup, email: EmailRecord):
        for anchor in soup.find_all("a", href=True):
            path = urlsplit(str(anchor.get("href", ""))).path.lower()
            if re.search(r"/(?:jobs?|stellenangebote?)/", path):
                yield _candidate(anchor, self.platform)


_EXTRACTORS: tuple[tuple[str, JobExtractor], ...] = (
    ("arbeitsagentur.de", ArbeitsagenturExtractor()),
    ("indeed.com", IndeedExtractor()),
    ("linkedin.com", LinkedInExtractor()),
    ("xing.com", XingExtractor()),
    ("stepstone.de", StepstoneExtractor()),
    ("instaffo.com", InstaffoExtractor()),
    ("stellenanzeigen.de", StellenanzeigenExtractor()),
    ("workwise.io", WorkwiseExtractor()),
)


def extractor_for_sender(sender: str | None) -> JobExtractor | None:
    """Select an extractor using the actual sender address stored on the email."""
    address = parseaddr(sender or "")[1].lower()
    if "@" not in address:
        return None
    domain = address.rsplit("@", 1)[1]
    for supported_domain, extractor in _EXTRACTORS:
        if domain == supported_domain or domain.endswith("." + supported_domain):
            return extractor
    return None
