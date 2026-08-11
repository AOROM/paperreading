"""Exporter protocol shared by concrete output adapters."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Protocol

from paperreading.artifacts import ResearchArtifact


class ExportFormat(str, Enum):
    JSON = "json"
    MARKDOWN = "markdown"
    EXCEL = "excel"


class ExportResult(dict[str, object]):
    """JSON-serializable result returned by every exporter."""


class Exporter(Protocol):
    def export(
        self,
        records: list[ResearchArtifact],
        destination: Path,
        **options: object,
    ) -> ExportResult: ...
