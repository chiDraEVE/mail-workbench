"""Extensible email source adapters and source-independent import logic."""

from .models import EmailRecord, ImportSource, ImportSummary
from .thunderbird import ThunderbirdMboxSource

__all__ = ["EmailRecord", "ImportSource", "ImportSummary", "ThunderbirdMboxSource"]
