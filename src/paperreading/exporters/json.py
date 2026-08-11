"""Lossless JSON export for versioned PaperReading artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from paperreading.artifacts import ResearchArtifact
from paperreading.exporters.base import ExportResult
from paperreading.exporters.text import atomic_write_text


class JsonExporter:
    def export(
        self,
        records: list[ResearchArtifact],
        destination: Path,
        **options: object,
    ) -> ExportResult:
        force = bool(options.get("force", False))
        payload: object
        if len(records) == 1:
            payload = records[0].model_dump(mode="json", exclude_none=True)
        else:
            payload = [
                record.model_dump(mode="json", exclude_none=True) for record in records
            ]
        content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        atomic_write_text(destination, content, force=force)
        return ExportResult(
            action="records_exported",
            format="json",
            destination=str(destination.expanduser().resolve()),
            records=len(records),
        )
