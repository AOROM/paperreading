"""Ingest a local source through an explicit parser and repository port."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from paperreading.domain import PaperDocument
from paperreading.ingestion import DocumentParser, parser_for_path
from paperreading.repositories.base import ResearchRepository


@dataclass(frozen=True)
class IngestDocument:
    repository: ResearchRepository

    def execute(
        self,
        source: Path,
        *,
        parser: DocumentParser | None = None,
        ingested_at: datetime | None = None,
        force: bool = False,
    ) -> tuple[PaperDocument, Path]:
        selected = parser or parser_for_path(source)
        document = selected.parse(source, ingested_at=ingested_at)
        destination = self.repository.save_document(document, force=force)
        return document, destination
