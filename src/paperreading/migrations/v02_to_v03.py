"""Migrate a v0.2 PaperRecord into a normalized v0.3 PaperPackage."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone

from paperreading.domain.document import DocumentFormat, DocumentManifest
from paperreading.domain.evidence import EvidenceRef, EvidenceSpan
from paperreading.domain.package import (
    AnalyzedResearchExtension,
    AssessmentOrigin,
    AssessmentType,
    GroundedFinding,
    GroundedLimitation,
    GroundedMechanism,
    GroundedPaperRecord,
    GroundedSourceClaim,
    GroundedTestResult,
    LanguageStrength,
    LimitationOrigin,
    PackageState,
    PaperPackage,
    RecordType,
    ResearchAnalysis,
    ResearchAssessment,
    RunManifest,
)
from paperreading.domain.paper import PaperRecord


def _stable_id(prefix: str, *parts: object) -> str:
    serialized = json.dumps(parts, ensure_ascii=False, sort_keys=True, default=str)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def _text_hash(text: str | None) -> str | None:
    if not text:
        return None
    normalized = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class _EvidenceMigrator:
    def __init__(self, canonical_source_id: str) -> None:
        self.canonical_source_id = canonical_source_id
        self.index: dict[str, EvidenceSpan] = {}
        self.rewritten_source_ids: set[str] = set()

    def add(self, evidence: EvidenceRef) -> str:
        payload = evidence.model_dump(
            mode="json", exclude={"confidence"}, exclude_none=True
        )
        payload["source_id"] = self.canonical_source_id
        evidence_id = _stable_id("ev", payload)
        if evidence.source_id != self.canonical_source_id:
            self.rewritten_source_ids.add(evidence.source_id)
        self.index.setdefault(
            evidence_id,
            EvidenceSpan(
                evidence_id=evidence_id,
                source_id=self.canonical_source_id,
                type=evidence.type,
                page=evidence.page,
                section_path=[evidence.section] if evidence.section else [],
                table=evidence.table,
                column=evidence.column,
                figure=evidence.figure,
                equation=evidence.equation,
                appendix=evidence.appendix,
                quoted_text=evidence.text,
                text_hash=_text_hash(evidence.text),
            ),
        )
        return evidence_id

    def add_many(self, evidence: list[EvidenceRef]) -> list[str]:
        return list(dict.fromkeys(self.add(item) for item in evidence))


def migrate_v02_to_v03(
    record: PaperRecord,
    *,
    migrated_at: datetime | None = None,
) -> PaperPackage:
    """Preserve v0.2 content while making uncertain provenance explicit."""

    timestamp = migrated_at or datetime.now(timezone.utc)
    evidence = _EvidenceMigrator(record.metadata.source_id)

    source_claims = [
        GroundedSourceClaim(
            claim_id=_stable_id("claim", record.paper_id, index, item.statement),
            statement=item.statement,
            evidence_ids=evidence.add_many(item.evidence),
        )
        for index, item in enumerate(record.source_claims)
    ]
    findings = [
        GroundedFinding(
            finding_id=_stable_id("finding", record.paper_id, index, item.statement),
            statement=item.statement,
            relationship=item.relationship,
            language_strength=(
                LanguageStrength.CAUSAL
                if item.causal
                else LanguageStrength.ASSOCIATIONAL
            ),
            coefficient=item.coefficient,
            significance=item.significance,
            evidence_ids=evidence.add_many(item.evidence),
        )
        for index, item in enumerate(record.findings)
    ]
    heterogeneity = [
        GroundedFinding(
            finding_id=_stable_id(
                "heterogeneity", record.paper_id, index, item.statement
            ),
            statement=item.statement,
            relationship=item.relationship,
            language_strength=(
                LanguageStrength.CAUSAL
                if item.causal
                else LanguageStrength.ASSOCIATIONAL
            ),
            coefficient=item.coefficient,
            significance=item.significance,
            evidence_ids=evidence.add_many(item.evidence),
        )
        for index, item in enumerate(record.heterogeneity)
    ]
    mechanisms = [
        GroundedMechanism(
            mechanism_id=_stable_id(
                "mechanism", record.paper_id, index, item.statement
            ),
            statement=item.statement,
            variables=item.variables,
            evidence_ids=evidence.add_many(item.evidence),
        )
        for index, item in enumerate(record.mechanisms)
    ]
    robustness = [
        GroundedTestResult(
            test_id=_stable_id("test", record.paper_id, index, item.name),
            name=item.name,
            result=item.result,
            passed=item.passed,
            evidence_ids=evidence.add_many(item.evidence),
        )
        for index, item in enumerate(record.robustness)
    ]

    unbound_ids = evidence.add_many(record.evidence)
    field_evidence = {"legacy.unbound_evidence": unbound_ids} if unbound_ids else {}
    grounded_record = GroundedPaperRecord(
        paper_id=record.paper_id,
        record_type=RecordType.EMPIRICAL,
        metadata=record.metadata,
        research_questions=record.research_questions,
        theoretical_framework=record.theoretical_framework,
        data=record.data,
        variables=record.variables,
        empirical_design=record.empirical_design,
        source_claims=source_claims,
        findings=findings,
        mechanisms=mechanisms,
        heterogeneity=heterogeneity,
        robustness=robustness,
        limitations=[
            GroundedLimitation(
                limitation_id=_stable_id(
                    "limitation", record.paper_id, index, statement
                ),
                statement=statement,
                origin=LimitationOrigin.LEGACY_UNKNOWN,
            )
            for index, statement in enumerate(record.limitations)
        ],
        field_evidence=field_evidence,
    )

    analysis = ResearchAnalysis(
        assessments=[
            ResearchAssessment(
                assessment_id=_stable_id(
                    "assessment", record.paper_id, index, statement
                ),
                type=AssessmentType.INTERPRETATION,
                statement=statement,
                origin=AssessmentOrigin.LEGACY_UNKNOWN,
                caveats=["Migrated from v0.2 without explicit evidence links."],
            )
            for index, statement in enumerate(record.researcher_assessment)
        ],
        research_extensions=[
            AnalyzedResearchExtension(
                extension_id=_stable_id(
                    "extension", record.paper_id, index, item.title
                ),
                title=item.title,
                gap_type=item.gap_type,
                research_question=item.research_question,
                identification_strategy=item.identification_strategy,
                sample=item.sample,
                data_sources=item.data_sources,
                variables=item.variables,
                mechanism_test=item.mechanism_test,
                robustness=item.robustness,
                falsification=item.falsification,
                expected_contribution=item.expected_contribution,
                assumptions=[
                    "Migrated from v0.2; supporting evidence was not explicitly recorded."
                ],
            )
            for index, item in enumerate(record.extensions)
        ],
    )

    notes = [
        "v0.2 extensions and researcher assessment were moved out of the source record.",
        "Evidence was normalized by stable ID; source-content verification has not run.",
    ]
    if evidence.rewritten_source_ids:
        notes.append(
            "Legacy evidence source IDs were normalized to the package document source ID."
        )

    return PaperPackage(
        state=PackageState.MIGRATED,
        document=DocumentManifest(
            source_id=record.metadata.source_id,
            source_name=record.metadata.title,
            format=DocumentFormat.LEGACY_RECORD,
            media_type="application/vnd.paperreading.v0.2+json",
            sha256=None,
            size_bytes=0,
            page_count=max(
                (item.page or 0 for item in evidence.index.values()), default=0
            ),
            ingested_at=timestamp,
        ),
        record=grounded_record,
        evidence_index=evidence.index,
        analysis=analysis,
        run=RunManifest(
            run_id=_stable_id("run", record.paper_id, "v02-to-v03"),
            source_sha256=None,
            provider="migration",
            created_at=timestamp,
        ),
        migration_notes=notes,
    )
