"""Finalize a reviewed extraction bundle into a canonical paper package."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from paperreading.application.workflow import ExtractionBundle
from paperreading.domain import (
    DraftStatus,
    GroundedPaperRecord,
    PackageState,
    PaperDocument,
    PaperPackage,
    ResearchAnalysis,
    RunManifest,
)
from paperreading.repositories.base import ResearchRepository


def _resolved_time(value: datetime | None) -> datetime:
    resolved = value or datetime.now(timezone.utc)
    if resolved.tzinfo is None or resolved.utcoffset() is None:
        raise ValueError("finalized_at must include a timezone")
    return resolved


def _set_path(root: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    if not parts or parts[0] not in {"record", "analysis"}:
        raise ValueError("candidate field_path must start with record or analysis")
    if any(not part for part in parts):
        raise ValueError(f"invalid candidate field_path: {path!r}")
    cursor = root
    for part in parts[:-1]:
        existing = cursor.setdefault(part, {})
        if not isinstance(existing, dict):
            raise ValueError(f"overlapping candidate field paths at {path!r}")
        cursor = existing
    if parts[-1] in cursor:
        raise ValueError(f"duplicate candidate field_path: {path!r}")
    cursor[parts[-1]] = value


@dataclass(frozen=True)
class FinalizeDraft:
    repository: ResearchRepository | None = None

    def execute(
        self,
        bundle: ExtractionBundle,
        document: PaperDocument,
        *,
        finalized_at: datetime | None = None,
        persist: bool = False,
        force: bool = False,
    ) -> tuple[PaperPackage, Path | None]:
        if bundle.draft.status is not DraftStatus.READY_TO_FINALIZE:
            raise ValueError("draft must be reviewed and ready before finalization")
        if bundle.document_id != document.document_id:
            raise ValueError("bundle and document IDs do not match")
        if bundle.canonical_text_sha256 != document.canonical_text_sha256:
            raise ValueError("document text changed after extraction")

        field_paths = [item.field_path for item in bundle.draft.candidates]
        if len(field_paths) != len(set(field_paths)):
            raise ValueError("review must select exactly one candidate per field")
        for left in field_paths:
            for right in field_paths:
                if left != right and right.startswith(left + "."):
                    raise ValueError(
                        f"overlapping candidate field paths: {left!r} and {right!r}"
                    )

        payload: dict[str, Any] = {}
        for candidate in bundle.draft.candidates:
            _set_path(payload, candidate.field_path, candidate.value)
        record_payload = payload.get("record")
        if not isinstance(record_payload, dict):
            raise ValueError("reviewed draft does not contain a record")
        record_payload.setdefault("schema_version", "0.3")
        record = GroundedPaperRecord.model_validate(record_payload)

        analysis_payload = payload.get("analysis")
        analysis = (
            ResearchAnalysis.model_validate(analysis_payload)
            if isinstance(analysis_payload, dict) and analysis_payload
            else None
        )
        used_evidence = record.referenced_evidence_ids()
        if analysis:
            used_evidence.update(analysis.referenced_evidence_ids())
        missing = sorted(used_evidence - set(bundle.evidence_index))
        if missing:
            raise ValueError(
                "record references missing evidence: " + ", ".join(missing)
            )

        finalized = _resolved_time(finalized_at)
        config_payload = {
            "canonical_text_sha256": bundle.canonical_text_sha256,
            "provider": bundle.provider,
            "provider_version": bundle.provider_version,
            "model": bundle.model,
            "extraction_stages": bundle.extraction_stages,
            "prompt_versions": bundle.prompt_versions,
        }
        config_json = json.dumps(
            config_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        config_hash = hashlib.sha256(config_json.encode("utf-8")).hexdigest()
        run_material = f"{bundle.draft.draft_id}:{config_hash}"
        run_hash = hashlib.sha256(run_material.encode("utf-8")).hexdigest()
        run = RunManifest(
            run_id=f"run-{run_hash[:16]}",
            pipeline_version="0.3.1",
            source_sha256=document.manifest.sha256,
            canonical_text_sha256=document.canonical_text_sha256,
            config_hash=config_hash,
            provider=bundle.provider,
            provider_version=bundle.provider_version,
            model=bundle.model,
            prompt_versions=bundle.prompt_versions,
            created_at=finalized,
        )
        package = PaperPackage(
            state=PackageState.FINALIZED,
            document=document.manifest,
            record=record,
            evidence_index=bundle.evidence_index,
            analysis=analysis,
            run=run,
        )

        destination: Path | None = None
        if persist:
            if self.repository is None:
                raise ValueError("persist=True requires a repository")
            destination = self.repository.save_package(package, force=force)
        return package, destination
