"""Serializable application contract for extraction and human review."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from paperreading.domain import EvidenceSpan, PaperDraft
from paperreading.domain.base import DomainModel
from paperreading.providers.base import ExtractionStage


class ReviewDecisions(DomainModel):
    selections: dict[str, str] = Field(default_factory=dict)
    dismissed_unresolved_fields: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_decisions(self) -> ReviewDecisions:
        if any(
            not field or not candidate for field, candidate in self.selections.items()
        ):
            raise ValueError(
                "review selections require non-empty fields and candidate IDs"
            )
        if len(self.dismissed_unresolved_fields) != len(
            set(self.dismissed_unresolved_fields)
        ):
            raise ValueError("dismissed unresolved fields must be unique")
        if any(not field for field in self.dismissed_unresolved_fields):
            raise ValueError("dismissed unresolved fields cannot be empty")
        if any(not note for note in self.notes):
            raise ValueError("review notes cannot be empty")
        return self


class ExtractionBundle(DomainModel):
    """Keep draft candidates, evidence, and run identity together."""

    schema_version: Literal["0.3"] = "0.3"
    document_id: str = Field(min_length=1)
    canonical_text_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    draft: PaperDraft
    evidence_index: dict[str, EvidenceSpan] = Field(default_factory=dict)
    provider: str = Field(min_length=1)
    provider_version: str = Field(min_length=1)
    model: str | None = None
    extraction_stages: list[ExtractionStage] = Field(min_length=1)
    prompt_versions: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_graph(self) -> ExtractionBundle:
        if self.document_id != self.draft.source_id:
            raise ValueError("bundle document_id must equal draft source_id")
        if len(self.extraction_stages) != len(set(self.extraction_stages)):
            raise ValueError("bundle extraction_stages must be unique")
        for key, evidence in self.evidence_index.items():
            if key != evidence.evidence_id:
                raise ValueError("evidence_index key must equal evidence_id")
            if evidence.source_id != self.document_id:
                raise ValueError("evidence source_id must match bundle document_id")
        referenced = {
            evidence_id
            for candidate in self.draft.candidates
            for evidence_id in candidate.evidence_ids
        }
        missing = sorted(referenced - set(self.evidence_index))
        if missing:
            raise ValueError(
                "candidate references missing evidence IDs: " + ", ".join(missing)
            )
        return self
