"""Traceable evidence references and deterministic confidence scoring."""

from __future__ import annotations

from enum import Enum
from typing import Literal

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


class TraceabilityScore(DomainModel):
    """Locator-specificity score; it is not a truth or study-quality score."""

    score: float = Field(ge=0, le=1)
    level: ConfidenceLevel
    reasons: list[str] = Field(min_length=1)
    scoring_version: Literal["1"] = "1"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    PARTIAL = "partial"
    FAILED = "failed"
    NOT_RUN = "not_run"


class EvidenceVerification(DomainModel):
    """Result of checking an EvidenceSpan against a supplied PaperDocument."""

    status: VerificationStatus
    source_match: bool | None = None
    page_resolved: bool | None = None
    block_resolved: bool | None = None
    char_range_resolved: bool | None = None
    quote_match: float | None = Field(default=None, ge=0, le=1)
    text_hash_match: bool | None = None
    issues: list[str] = Field(default_factory=list)
    verifier_version: str = "0.3.1"

    @model_validator(mode="after")
    def validate_run_state(self) -> EvidenceVerification:
        checks = (
            self.source_match,
            self.page_resolved,
            self.block_resolved,
            self.char_range_resolved,
            self.quote_match,
            self.text_hash_match,
        )
        if self.status is VerificationStatus.NOT_RUN:
            if any(item is not None for item in checks) or self.issues:
                raise ValueError("not-run verification cannot contain check results")
        elif self.source_match is None:
            raise ValueError("completed verification requires source_match")
        return self


class EvidenceSpan(DomainModel):
    """Normalized evidence node referenced by ID from v0.3 research objects."""

    evidence_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    type: EvidenceType
    page: int | None = Field(default=None, ge=1)
    section_path: list[str] = Field(default_factory=list)
    block_id: str | None = None
    char_start: int | None = Field(default=None, ge=0)
    char_end: int | None = Field(default=None, ge=0)
    bbox: tuple[float, float, float, float] | None = None
    table: str | None = None
    column: str | None = None
    figure: str | None = None
    equation: str | None = None
    appendix: str | None = None
    quoted_text: str | None = None
    text_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    traceability: TraceabilityScore | None = None
    verification: EvidenceVerification | None = None

    @model_validator(mode="after")
    def validate_span_and_score(self) -> EvidenceSpan:
        structural = (
            self.page,
            self.section_path,
            self.block_id,
            self.bbox,
            self.table,
            self.column,
            self.figure,
            self.equation,
            self.appendix,
        )
        if not self.quoted_text and not any(structural):
            raise ValueError(
                "evidence span must include quoted text or a structural locator"
            )
        if (self.char_start is None) != (self.char_end is None):
            raise ValueError("char_start and char_end must be supplied together")
        if self.char_start is not None and not self.block_id:
            raise ValueError("character ranges require a block_id")
        if (
            self.char_start is not None
            and self.char_end is not None
            and self.char_end <= self.char_start
        ):
            raise ValueError("char_end must be greater than char_start")
        if self.text_hash and not self.quoted_text:
            raise ValueError("text_hash requires quoted_text")
        if self.bbox:
            if self.page is None:
                raise ValueError("bbox requires a page locator")
            x1, y1, x2, y2 = self.bbox
            if x2 <= x1 or y2 <= y1:
                raise ValueError("bbox must have increasing coordinates")
        object.__setattr__(self, "traceability", score_traceability(self))
        return self


def score_traceability(evidence: EvidenceSpan) -> TraceabilityScore:
    """Calculate locator specificity without claiming source-content verification."""

    locator_count = sum(
        bool(value)
        for value in (
            evidence.page,
            evidence.section_path,
            evidence.block_id,
            evidence.bbox,
            evidence.table,
            evidence.column,
            evidence.figure,
            evidence.equation,
            evidence.appendix,
        )
    )
    reasons = ["source_id is present"]
    if evidence.page and evidence.block_id and evidence.char_start is not None:
        score = 0.98
        reasons.append("page, block, and character range are present")
    elif evidence.page and evidence.table and evidence.column:
        score = 0.95
        reasons.append("page, table, and column are present")
    elif evidence.page and evidence.section_path:
        score = 0.85
        reasons.append("page and section path are present")
    elif locator_count:
        score = 0.70
        reasons.append("at least one structural locator is present")
    else:
        score = 0.50
        reasons.append("quoted text is present without a structural locator")

    if score >= 0.80:
        level = ConfidenceLevel.HIGH
    elif score >= 0.55:
        level = ConfidenceLevel.MEDIUM
    else:
        level = ConfidenceLevel.LOW
    reasons.append("score measures traceability specificity only")
    return TraceabilityScore(score=score, level=level, reasons=reasons)
