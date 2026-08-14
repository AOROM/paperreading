"""Provider-neutral extraction contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from pydantic import Field, model_validator

from paperreading.domain import EvidenceSpan, ExtractionCandidate, PaperDocument
from paperreading.domain.base import DomainModel


class ExtractionStage(str, Enum):
    METADATA = "metadata"
    RESEARCH_QUESTIONS = "research_questions"
    THEORY = "theory"
    DATA = "data"
    VARIABLES = "variables"
    DESIGN = "design"
    FINDINGS = "findings"
    MECHANISMS = "mechanisms"
    HETEROGENEITY = "heterogeneity"
    ROBUSTNESS = "robustness"
    LIMITATIONS = "limitations"
    ANALYSIS = "analysis"


DEFAULT_EXTRACTION_STAGES: tuple[ExtractionStage, ...] = tuple(ExtractionStage)


@dataclass(frozen=True)
class ExtractionTask:
    document: PaperDocument
    stage: ExtractionStage


class ExtractionStageResult(DomainModel):
    stage: ExtractionStage
    candidates: list[ExtractionCandidate] = Field(default_factory=list)
    evidence_index: dict[str, EvidenceSpan] = Field(default_factory=dict)
    unresolved_fields: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    prompt_version: str | None = None

    @model_validator(mode="after")
    def validate_evidence_index(self) -> ExtractionStageResult:
        for key, evidence in self.evidence_index.items():
            if key != evidence.evidence_id:
                raise ValueError("evidence_index key must equal evidence_id")
        return self


class ExtractionProvider(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    @property
    def model(self) -> str | None: ...

    def extract(self, task: ExtractionTask) -> ExtractionStageResult: ...
