"""Partial extraction artifacts that may preserve unresolved fields."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import Field, JsonValue, model_validator

from paperreading.domain.base import DomainModel


class DraftStatus(str, Enum):
    EXTRACTED = "extracted"
    NEEDS_REVIEW = "needs_review"
    READY_TO_FINALIZE = "ready_to_finalize"


class ExtractionCandidate(DomainModel):
    candidate_id: str = Field(min_length=1)
    field_path: str = Field(min_length=1)
    value: JsonValue
    evidence_ids: list[str] = Field(default_factory=list)
    extractor: str = Field(min_length=1)
    prompt_version: str | None = None


class ExtractionConflict(DomainModel):
    field_path: str = Field(min_length=1)
    candidate_ids: list[str] = Field(min_length=2)
    reason: str = Field(min_length=1)


class PaperDraft(DomainModel):
    schema_version: Literal["0.3"] = "0.3"
    draft_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    status: DraftStatus = DraftStatus.EXTRACTED
    candidates: list[ExtractionCandidate] = Field(default_factory=list)
    unresolved_fields: list[str] = Field(default_factory=list)
    conflicts: list[ExtractionConflict] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    created_at: datetime

    @model_validator(mode="after")
    def validate_review_state(self) -> PaperDraft:
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("created_at must include a timezone")
        candidate_ids = [item.candidate_id for item in self.candidates]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("candidate IDs must be unique")
        known = set(candidate_ids)
        for conflict in self.conflicts:
            if len(conflict.candidate_ids) != len(set(conflict.candidate_ids)):
                raise ValueError("conflict candidate IDs must be unique")
            missing = set(conflict.candidate_ids) - known
            if missing:
                raise ValueError("conflicts must reference existing candidates")
        if self.status is DraftStatus.READY_TO_FINALIZE and (
            self.unresolved_fields or self.conflicts
        ):
            raise ValueError(
                "ready-to-finalize drafts cannot contain unresolved fields or conflicts"
            )
        return self
