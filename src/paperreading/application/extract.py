"""Run staged extraction through a provider port and preserve uncertainty."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from paperreading.application.workflow import ExtractionBundle
from paperreading.domain import (
    DraftStatus,
    EvidenceSpan,
    ExtractionCandidate,
    ExtractionConflict,
    PaperDocument,
    PaperDraft,
)
from paperreading.providers import (
    DEFAULT_EXTRACTION_STAGES,
    ExtractionProvider,
    ExtractionStage,
    ExtractionTask,
)
from paperreading.repositories.base import ResearchRepository


def _resolved_time(value: datetime | None) -> datetime:
    resolved = value or datetime.now(timezone.utc)
    if resolved.tzinfo is None or resolved.utcoffset() is None:
        raise ValueError("created_at must include a timezone")
    return resolved


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _merge_evidence(
    target: dict[str, EvidenceSpan], incoming: dict[str, EvidenceSpan]
) -> None:
    for evidence_id, evidence in incoming.items():
        existing = target.get(evidence_id)
        if existing is not None and existing != evidence:
            raise ValueError(f"conflicting definitions for evidence {evidence_id}")
        target[evidence_id] = evidence


def _candidate_conflicts(
    candidates: list[ExtractionCandidate],
) -> list[ExtractionConflict]:
    grouped: dict[str, list[ExtractionCandidate]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate.field_path, []).append(candidate)

    conflicts: list[ExtractionConflict] = []
    for field_path, items in grouped.items():
        values = {_canonical_json(item.value) for item in items}
        if len(values) > 1:
            conflicts.append(
                ExtractionConflict(
                    field_path=field_path,
                    candidate_ids=[item.candidate_id for item in items],
                    reason="provider returned incompatible values for one field",
                )
            )
    return conflicts


@dataclass(frozen=True)
class ExtractDocument:
    repository: ResearchRepository | None = None

    def execute(
        self,
        document: PaperDocument,
        provider: ExtractionProvider,
        *,
        stages: tuple[ExtractionStage, ...] = DEFAULT_EXTRACTION_STAGES,
        created_at: datetime | None = None,
        persist: bool = False,
        force: bool = False,
    ) -> tuple[ExtractionBundle, Path | None]:
        if len(stages) != len(set(stages)):
            raise ValueError("extraction stages must be unique")

        candidates: list[ExtractionCandidate] = []
        evidence_index: dict[str, EvidenceSpan] = {}
        unresolved_fields: list[str] = []
        issues: list[str] = []
        prompt_versions: dict[str, str] = {}

        for stage in stages:
            result = provider.extract(ExtractionTask(document=document, stage=stage))
            if result.stage != stage:
                raise ValueError("provider returned a result for the wrong stage")
            candidates.extend(result.candidates)
            _merge_evidence(evidence_index, result.evidence_index)
            unresolved_fields.extend(result.unresolved_fields)
            issues.extend(result.issues)
            if result.prompt_version:
                prompt_versions[stage.value] = result.prompt_version

        candidate_ids = [candidate.candidate_id for candidate in candidates]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("provider returned duplicate candidate IDs")
        if any(
            evidence.source_id != document.document_id
            for evidence in evidence_index.values()
        ):
            raise ValueError("provider evidence does not belong to the document")
        if any(
            evidence.verification is not None for evidence in evidence_index.values()
        ):
            raise ValueError(
                "providers cannot assert evidence verification; run the verifier"
            )

        referenced = {
            evidence_id
            for candidate in candidates
            for evidence_id in candidate.evidence_ids
        }
        missing = sorted(referenced - set(evidence_index))
        if missing:
            raise ValueError(
                "candidate references missing evidence IDs: " + ", ".join(missing)
            )

        conflicts = _candidate_conflicts(candidates)
        stable_payload = {
            "source_id": document.document_id,
            "canonical_text_sha256": document.canonical_text_sha256,
            "provider": provider.name,
            "provider_version": provider.version,
            "model": provider.model,
            "stages": [stage.value for stage in stages],
            "candidates": [
                candidate.model_dump(mode="json", exclude_none=True)
                for candidate in candidates
            ],
            "evidence_index": {
                evidence_id: evidence.model_dump(mode="json", exclude_none=True)
                for evidence_id, evidence in sorted(evidence_index.items())
            },
            "unresolved_fields": list(dict.fromkeys(unresolved_fields)),
            "issues": list(dict.fromkeys(issues)),
            "prompt_versions": prompt_versions,
        }
        digest = hashlib.sha256(
            _canonical_json(stable_payload).encode("utf-8")
        ).hexdigest()
        draft = PaperDraft(
            draft_id=f"draft-{digest[:16]}",
            source_id=document.document_id,
            status=(
                DraftStatus.NEEDS_REVIEW
                if conflicts or unresolved_fields
                else DraftStatus.EXTRACTED
            ),
            candidates=candidates,
            unresolved_fields=list(dict.fromkeys(unresolved_fields)),
            conflicts=conflicts,
            issues=list(dict.fromkeys(issues)),
            created_at=_resolved_time(created_at),
        )
        bundle = ExtractionBundle(
            document_id=document.document_id,
            canonical_text_sha256=document.canonical_text_sha256,
            draft=draft,
            evidence_index=evidence_index,
            provider=provider.name,
            provider_version=provider.version,
            model=provider.model,
            extraction_stages=list(stages),
            prompt_versions=prompt_versions,
        )

        destination: Path | None = None
        if persist:
            if self.repository is None:
                raise ValueError("persist=True requires a repository")
            destination = self.repository.save_draft(draft, force=force)
        return bundle, destination
