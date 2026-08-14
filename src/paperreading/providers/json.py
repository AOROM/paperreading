"""Deterministic JSON extraction provider for offline and audited runs."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from paperreading.domain import EvidenceSpan, ExtractionCandidate
from paperreading.domain.base import DomainModel
from paperreading.providers.base import (
    ExtractionStage,
    ExtractionStageResult,
    ExtractionTask,
)


class JsonStagePayload(DomainModel):
    candidates: list[ExtractionCandidate] = Field(default_factory=list)
    evidence_index: dict[str, EvidenceSpan] = Field(default_factory=dict)
    unresolved_fields: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    prompt_version: str | None = None


class JsonExtractionManifest(DomainModel):
    schema_version: Literal["1"] = "1"
    source_id: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    provider_version: str = Field(min_length=1)
    model: str | None = None
    stages: dict[ExtractionStage, JsonStagePayload]

    @model_validator(mode="after")
    def validate_manifest_graph(self) -> JsonExtractionManifest:
        evidence_index: dict[str, EvidenceSpan] = {}
        candidate_ids: set[str] = set()
        for payload in self.stages.values():
            for key, evidence in payload.evidence_index.items():
                if key != evidence.evidence_id:
                    raise ValueError("evidence_index key must equal evidence_id")
                if evidence.source_id != self.source_id:
                    raise ValueError("evidence source_id must match manifest source_id")
                if evidence.verification is not None:
                    raise ValueError(
                        "provider evidence cannot contain verification results"
                    )
                existing = evidence_index.get(key)
                if existing is not None and existing != evidence:
                    raise ValueError(f"conflicting definitions for evidence {key}")
                evidence_index[key] = evidence
            for candidate in payload.candidates:
                if candidate.candidate_id in candidate_ids:
                    raise ValueError("candidate IDs must be unique across stages")
                candidate_ids.add(candidate.candidate_id)

        referenced = {
            evidence_id
            for payload in self.stages.values()
            for candidate in payload.candidates
            for evidence_id in candidate.evidence_ids
        }
        missing = sorted(referenced - set(evidence_index))
        if missing:
            raise ValueError(
                "candidate references missing evidence IDs: " + ", ".join(missing)
            )
        return self


class JsonExtractionProvider:
    """Replay checked extraction output without network or hidden model calls."""

    def __init__(self, manifest: JsonExtractionManifest) -> None:
        self.manifest = manifest

    @classmethod
    def from_path(cls, path: Path) -> JsonExtractionProvider:
        return cls(
            JsonExtractionManifest.model_validate_json(
                path.expanduser().read_text(encoding="utf-8")
            )
        )

    @property
    def name(self) -> str:
        return self.manifest.provider

    @property
    def version(self) -> str:
        return self.manifest.provider_version

    @property
    def model(self) -> str | None:
        return self.manifest.model

    def extract(self, task: ExtractionTask) -> ExtractionStageResult:
        if task.document.document_id != self.manifest.source_id:
            raise ValueError(
                "provider manifest source_id does not match the supplied document"
            )
        payload = self.manifest.stages.get(task.stage, JsonStagePayload())
        return ExtractionStageResult(
            stage=task.stage,
            candidates=payload.candidates,
            evidence_index=payload.evidence_index,
            unresolved_fields=payload.unresolved_fields,
            issues=payload.issues,
            prompt_version=payload.prompt_version,
        )
