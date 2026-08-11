"""The Paper Intelligence Object used by every interface and exporter."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal

from pydantic import Field, model_validator

from paperreading.domain.base import DomainModel
from paperreading.domain.evidence import EvidenceRef


class Relationship(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NULL = "null"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class VariableRole(str, Enum):
    DEPENDENT = "dependent"
    INDEPENDENT = "independent"
    CONTROL = "control"
    MEDIATOR = "mediator"
    MODERATOR = "moderator"
    INSTRUMENT = "instrument"


class DesignType(str, Enum):
    OLS = "ols"
    PANEL_FE = "panel_fe"
    DID = "did"
    STAGGERED_DID = "staggered_did"
    IV = "iv"
    RDD = "rdd"
    PSM = "psm"
    EVENT_STUDY = "event_study"
    RCT = "rct"
    QUALITATIVE = "qualitative"
    OTHER = "other"


class GapType(str, Enum):
    METHOD = "method_gap"
    DATA = "data_gap"
    VARIABLE = "variable_gap"
    MECHANISM = "mechanism_gap"
    CONTEXT = "context_gap"
    IDENTIFICATION = "identification_gap"
    EXTERNAL_VALIDITY = "external_validity_gap"
    TEMPORAL = "temporal_gap"
    MEASUREMENT = "measurement_gap"
    THEORY = "theory_gap"
    CONTRADICTORY_EVIDENCE = "contradictory_evidence"


class RankingEvidence(DomainModel):
    system: str = Field(min_length=1)
    label: str = Field(min_length=1)
    source: str = Field(min_length=1)
    version: str | None = None
    effective_date: date | None = None
    verified_on: date | None = None


class PaperMetadata(DomainModel):
    title: str = Field(min_length=1)
    authors: list[str] = Field(min_length=1)
    source_id: str = Field(min_length=1)
    journal: str | None = None
    publication_date: str | None = None
    doi: str | None = None
    language: str = "zh-CN"
    keywords: list[str] = Field(default_factory=list)
    rankings: list[RankingEvidence] = Field(default_factory=list)


class Theory(DomainModel):
    framework: str | None = None
    propositions: list[str] = Field(default_factory=list)
    causal_chain: str | None = None


class DataDescription(DomainModel):
    sample: str | None = None
    period: str | None = None
    sources: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)


class Variable(DomainModel):
    name: str = Field(min_length=1)
    role: VariableRole
    abbreviation: str | None = None
    definition: str | None = None
    measurement: str | None = None
    source: str | None = None


class EmpiricalDesign(DomainModel):
    type: DesignType
    method: str = Field(min_length=1)
    model_equation: str | None = None
    fixed_effects: list[str] = Field(default_factory=list)
    standard_errors: str | None = None
    identification_strategy: str | None = None
    endogeneity_methods: list[str] = Field(default_factory=list)
    robustness_checks: list[str] = Field(default_factory=list)


class SourceClaim(DomainModel):
    statement: str = Field(min_length=1)
    evidence: list[EvidenceRef] = Field(min_length=1)


class Finding(DomainModel):
    statement: str = Field(min_length=1)
    relationship: Relationship
    coefficient: float | None = None
    significance: str | None = None
    causal: bool = False
    evidence: list[EvidenceRef] = Field(min_length=1)


class Mechanism(DomainModel):
    statement: str = Field(min_length=1)
    variables: list[str] = Field(default_factory=list)
    evidence: list[EvidenceRef] = Field(min_length=1)


class TestResult(DomainModel):
    name: str = Field(min_length=1)
    result: str = Field(min_length=1)
    passed: bool | None = None
    evidence: list[EvidenceRef] = Field(min_length=1)


class ResearchExtension(DomainModel):
    title: str = Field(min_length=1)
    gap_type: GapType
    research_question: str = Field(min_length=1)
    identification_strategy: str | None = None
    sample: str | None = None
    data_sources: list[str] = Field(default_factory=list)
    variables: list[str] = Field(default_factory=list)
    mechanism_test: str | None = None
    robustness: list[str] = Field(default_factory=list)
    falsification: str | None = None
    expected_contribution: str | None = None

    @model_validator(mode="after")
    def require_executable_design(self) -> ResearchExtension:
        if not (
            self.identification_strategy
            or self.sample
            or self.data_sources
            or self.variables
            or self.mechanism_test
            or self.falsification
        ):
            raise ValueError(
                "research extension must contain an executable design element"
            )
        return self


class PaperRecord(DomainModel):
    """Canonical record; legacy Excel columns are only a projection of this model."""

    schema_version: Literal["0.2"] = "0.2"
    paper_id: str = Field(min_length=1)
    metadata: PaperMetadata
    research_questions: list[str] = Field(min_length=1, max_length=3)
    theoretical_framework: Theory
    data: DataDescription
    variables: list[Variable] = Field(min_length=1)
    empirical_design: EmpiricalDesign
    source_claims: list[SourceClaim] = Field(min_length=1)
    findings: list[Finding] = Field(min_length=1)
    mechanisms: list[Mechanism] = Field(default_factory=list)
    heterogeneity: list[Finding] = Field(default_factory=list)
    robustness: list[TestResult] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    extensions: list[ResearchExtension] = Field(min_length=2, max_length=4)
    researcher_assessment: list[str] = Field(default_factory=list)
    evidence: list[EvidenceRef] = Field(default_factory=list)

    def bound_evidence(self) -> list[EvidenceRef]:
        """Return every evidence reference attached to a typed research object."""

        result = list(self.evidence)
        result.extend(item for claim in self.source_claims for item in claim.evidence)
        result.extend(item for finding in self.findings for item in finding.evidence)
        result.extend(
            item for finding in self.heterogeneity for item in finding.evidence
        )
        result.extend(
            item for mechanism in self.mechanisms for item in mechanism.evidence
        )
        result.extend(item for test in self.robustness for item in test.evidence)
        return result
