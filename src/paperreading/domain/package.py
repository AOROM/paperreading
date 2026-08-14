"""v0.3 package separating source-grounded records from derived analysis."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import Field, model_validator

from paperreading.domain.base import DomainModel
from paperreading.domain.document import DocumentManifest
from paperreading.domain.evidence import EvidenceSpan, VerificationStatus
from paperreading.domain.paper import (
    DataDescription,
    EmpiricalDesign,
    GapType,
    PaperMetadata,
    Relationship,
    Theory,
    Variable,
)


class RecordType(str, Enum):
    EMPIRICAL = "empirical"
    THEORETICAL = "theoretical"
    REVIEW = "review"
    OTHER = "other"


class LanguageStrength(str, Enum):
    DESCRIPTIVE = "descriptive"
    ASSOCIATIONAL = "associational"
    CAUSAL = "causal"


class LimitationOrigin(str, Enum):
    PAPER = "paper"
    LEGACY_UNKNOWN = "legacy_unknown"


class AssessmentOrigin(str, Enum):
    RESEARCHER = "researcher"
    AI_ASSISTED = "ai_assisted"
    LEGACY_UNKNOWN = "legacy_unknown"


class AssessmentType(str, Enum):
    INTERPRETATION = "interpretation"
    LIMITATION = "limitation"
    CAVEAT = "caveat"


class AuditStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    UNCLEAR = "unclear"
    NOT_APPLICABLE = "not_applicable"


class CausalSupport(str, Enum):
    UNSUPPORTED = "unsupported"
    LIMITED = "limited"
    SUPPORTED_WITH_CAVEATS = "supported_with_caveats"
    SUPPORTED = "supported"


class PackageState(str, Enum):
    MIGRATED = "migrated"
    FINALIZED = "finalized"
    VERIFIED = "verified"
    AUDITED = "audited"


class GroundedSourceClaim(DomainModel):
    claim_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    evidence_ids: list[str] = Field(min_length=1)


class GroundedFinding(DomainModel):
    finding_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    relationship: Relationship
    language_strength: LanguageStrength = LanguageStrength.ASSOCIATIONAL
    coefficient: float | None = None
    significance: str | None = None
    evidence_ids: list[str] = Field(min_length=1)


class GroundedMechanism(DomainModel):
    mechanism_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    variables: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(min_length=1)


class GroundedTestResult(DomainModel):
    test_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    result: str = Field(min_length=1)
    passed: bool | None = None
    evidence_ids: list[str] = Field(min_length=1)


class GroundedLimitation(DomainModel):
    limitation_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    origin: LimitationOrigin
    evidence_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_evidence_for_paper_origin(self) -> GroundedLimitation:
        if self.origin is LimitationOrigin.PAPER and not self.evidence_ids:
            raise ValueError("paper-reported limitations require evidence IDs")
        return self


class GroundedPaperRecord(DomainModel):
    """Source-derived facts only; analysis and suggestions live outside this model."""

    schema_version: Literal["0.3"] = "0.3"
    paper_id: str = Field(min_length=1)
    record_type: RecordType = RecordType.EMPIRICAL
    metadata: PaperMetadata
    research_questions: list[str] = Field(min_length=1, max_length=3)
    theoretical_framework: Theory
    data: DataDescription
    variables: list[Variable] = Field(default_factory=list)
    empirical_design: EmpiricalDesign | None = None
    source_claims: list[GroundedSourceClaim] = Field(min_length=1)
    findings: list[GroundedFinding] = Field(default_factory=list)
    mechanisms: list[GroundedMechanism] = Field(default_factory=list)
    heterogeneity: list[GroundedFinding] = Field(default_factory=list)
    robustness: list[GroundedTestResult] = Field(default_factory=list)
    limitations: list[GroundedLimitation] = Field(default_factory=list)
    field_evidence: dict[str, list[str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_empirical_content(self) -> GroundedPaperRecord:
        if self.record_type is RecordType.EMPIRICAL:
            if self.empirical_design is None:
                raise ValueError("empirical records require empirical_design")
            if not self.findings:
                raise ValueError("empirical records require at least one finding")
        return self

    def referenced_evidence_ids(self) -> set[str]:
        result = {item for values in self.field_evidence.values() for item in values}
        result.update(
            item for claim in self.source_claims for item in claim.evidence_ids
        )
        result.update(
            item for finding in self.findings for item in finding.evidence_ids
        )
        result.update(
            item for finding in self.heterogeneity for item in finding.evidence_ids
        )
        result.update(
            item for mechanism in self.mechanisms for item in mechanism.evidence_ids
        )
        result.update(item for test in self.robustness for item in test.evidence_ids)
        result.update(
            item for limitation in self.limitations for item in limitation.evidence_ids
        )
        return result


class ResearchAssessment(DomainModel):
    assessment_id: str = Field(min_length=1)
    type: AssessmentType
    statement: str = Field(min_length=1)
    origin: AssessmentOrigin
    basis_evidence_ids: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class AnalyzedResearchExtension(DomainModel):
    extension_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    gap_type: GapType
    research_question: str = Field(min_length=1)
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    identification_strategy: str | None = None
    sample: str | None = None
    data_sources: list[str] = Field(default_factory=list)
    variables: list[str] = Field(default_factory=list)
    mechanism_test: str | None = None
    robustness: list[str] = Field(default_factory=list)
    falsification: str | None = None
    expected_contribution: str | None = None
    assumptions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_executable_design(self) -> AnalyzedResearchExtension:
        if not (
            self.identification_strategy
            or self.sample
            or self.data_sources
            or self.variables
            or self.mechanism_test
            or self.falsification
        ):
            raise ValueError("research extension requires an executable design element")
        return self


class ResearchAnalysis(DomainModel):
    assessments: list[ResearchAssessment] = Field(default_factory=list)
    research_extensions: list[AnalyzedResearchExtension] = Field(default_factory=list)

    def referenced_evidence_ids(self) -> set[str]:
        result = {
            item
            for assessment in self.assessments
            for item in assessment.basis_evidence_ids
        }
        result.update(
            item
            for extension in self.research_extensions
            for item in extension.supporting_evidence_ids
        )
        return result


class AuditCheck(DomainModel):
    code: str = Field(min_length=1)
    status: AuditStatus
    message: str = Field(min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)
    severity: str = "info"


class MethodAuditReport(DomainModel):
    method: str = Field(min_length=1)
    causal_support: CausalSupport
    checks: list[AuditCheck] = Field(default_factory=list)
    auditor_version: str = "0.3.1"

    def referenced_evidence_ids(self) -> set[str]:
        return {item for check in self.checks for item in check.evidence_ids}


class RunManifest(DomainModel):
    run_id: str = Field(min_length=1)
    pipeline_version: str = "0.3.1"
    source_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    canonical_text_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    config_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    provider: str | None = None
    provider_version: str | None = None
    model: str | None = None
    prompt_versions: dict[str, str] = Field(default_factory=dict)
    created_at: datetime

    @model_validator(mode="after")
    def require_timezone(self) -> RunManifest:
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("created_at must include a timezone")
        if self.model and not self.provider:
            raise ValueError("model requires a provider")
        if self.provider_version and not self.provider:
            raise ValueError("provider_version requires a provider")
        return self


class PaperPackage(DomainModel):
    """Canonical v0.3 research asset with normalized evidence references."""

    schema_version: Literal["0.3"] = "0.3"
    state: PackageState
    document: DocumentManifest
    record: GroundedPaperRecord
    evidence_index: dict[str, EvidenceSpan] = Field(min_length=1)
    analysis: ResearchAnalysis | None = None
    audit: MethodAuditReport | None = None
    run: RunManifest
    migration_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_evidence_graph(self) -> PaperPackage:
        if self.document.source_id != self.record.metadata.source_id:
            raise ValueError("document and metadata source_id values must match")
        for key, evidence in self.evidence_index.items():
            if key != evidence.evidence_id:
                raise ValueError("evidence_index key must equal evidence_id")
            if evidence.source_id != self.document.source_id:
                raise ValueError("evidence source_id must match document source_id")

        referenced = self.record.referenced_evidence_ids()
        if self.analysis:
            referenced.update(self.analysis.referenced_evidence_ids())
        if self.audit:
            referenced.update(self.audit.referenced_evidence_ids())
        missing = sorted(referenced - set(self.evidence_index))
        if missing:
            raise ValueError(f"unresolved evidence IDs: {', '.join(missing)}")
        if self.state is PackageState.VERIFIED and any(
            evidence.verification is None
            or evidence.verification.status is not VerificationStatus.VERIFIED
            for evidence in self.evidence_index.values()
        ):
            raise ValueError(
                "verified packages require every evidence span to be fully verified"
            )
        if self.state is PackageState.AUDITED and self.audit is None:
            raise ValueError("audited packages require an audit report")
        if self.document.sha256 and self.run.source_sha256:
            if self.document.sha256 != self.run.source_sha256:
                raise ValueError("run source_sha256 must match document sha256")
        elif self.document.sha256 and self.state is not PackageState.MIGRATED:
            raise ValueError(
                "finalized, verified, and audited packages require run source_sha256"
            )
        return self
