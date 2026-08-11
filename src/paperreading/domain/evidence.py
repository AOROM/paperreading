"""Traceable evidence references and deterministic confidence scoring."""

from __future__ import annotations

from enum import Enum

from pydantic import Field, model_validator

from paperreading.domain.base import DomainModel


class EvidenceType(str, Enum):
    """Supported source surfaces for a research statement."""

    TEXT = "TEXT"
    TABLE = "TABLE"
    FIGURE = "FIGURE"
    EQUATION = "EQUATION"
    APPENDIX = "APPENDIX"
    METADATA = "METADATA"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Confidence(DomainModel):
    """Rule-derived confidence, not an unconstrained model opinion."""

    score: float = Field(ge=0, le=1)
    level: ConfidenceLevel
    reasons: list[str] = Field(min_length=1)


class EvidenceRef(DomainModel):
    """A source-aware locator for one claim or reported result."""

    source_id: str = Field(min_length=1)
    type: EvidenceType
    page: int | None = Field(default=None, ge=1)
    section: str | None = None
    table: str | None = None
    column: str | None = None
    figure: str | None = None
    equation: str | None = None
    appendix: str | None = None
    text: str | None = None
    confidence: Confidence | None = None

    @model_validator(mode="after")
    def require_provenance_and_score(self) -> EvidenceRef:
        """Require a reviewable locator and replace arbitrary confidence values."""

        locator_values = (
            self.page,
            self.section,
            self.table,
            self.column,
            self.figure,
            self.equation,
            self.appendix,
        )
        if not self.text and not any(value is not None for value in locator_values):
            raise ValueError(
                "evidence must include quoted/paraphrased text or a source locator"
            )

        object.__setattr__(self, "confidence", _score_confidence(self))
        return self


def _score_confidence(evidence: EvidenceRef) -> Confidence:
    """Apply the repository's transparent locator-specific scoring rule."""

    locator_count = sum(
        value is not None
        for value in (
            evidence.page,
            evidence.section,
            evidence.table,
            evidence.column,
            evidence.figure,
            evidence.equation,
            evidence.appendix,
        )
    )
    reasons = ["source_id is present"]

    if evidence.page and evidence.table and evidence.column:
        specificity = 0.98
        reasons.append("page, table, and column identify a precise result")
    elif evidence.page and evidence.section:
        specificity = 0.92
        reasons.append("page and section identify a precise passage")
    elif locator_count:
        specificity = 0.80
        reasons.append("at least one structural locator is present")
    else:
        specificity = 0.65
        reasons.append("text is present without a structural locator")

    extraction_consistency = 0.95 if evidence.text and locator_count else 0.90
    cross_check = 0.96 if locator_count >= 3 else 0.90
    score = round(specificity * extraction_consistency * cross_check, 3)

    if score >= 0.75:
        level = ConfidenceLevel.HIGH
    elif score >= 0.45:
        level = ConfidenceLevel.MEDIUM
    else:
        level = ConfidenceLevel.LOW

    reasons.append("score is rule-derived from locator specificity")
    return Confidence(score=score, level=level, reasons=reasons)
