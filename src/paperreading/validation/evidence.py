"""Validate evidence traceability and cross-field consistency."""

from __future__ import annotations

from paperreading.domain import ConfidenceLevel, EvidenceRef, PaperRecord
from paperreading.validation.causal import causal_language_issues
from paperreading.validation.result import (
    IssueSeverity,
    ValidationIssue,
    ValidationReport,
)


def _evidence_key(item: EvidenceRef) -> tuple[object, ...]:
    return (
        item.source_id,
        item.type,
        item.page,
        item.section,
        item.table,
        item.column,
        item.figure,
        item.equation,
        item.appendix,
        item.text,
    )


def validate_record(record: PaperRecord, *, strict: bool = False) -> ValidationReport:
    """Apply shared evidence and causal-language rules to a PaperRecord."""

    issues: list[ValidationIssue] = []
    unique_evidence = {
        _evidence_key(item): item for item in record.bound_evidence()
    }.values()

    known_source_ids = {record.metadata.source_id}
    if record.metadata.doi:
        known_source_ids.add(record.metadata.doi)

    for index, item in enumerate(unique_evidence):
        path = f"evidence[{index}]"
        if item.source_id not in known_source_ids:
            issues.append(
                ValidationIssue(
                    code="UNKNOWN_SOURCE_ID",
                    severity=IssueSeverity.WARNING,
                    message=(
                        f"Evidence source_id '{item.source_id}' is not the paper's "
                        "declared source_id or DOI."
                    ),
                    path=f"{path}.source_id",
                )
            )

        has_structural_locator = any(
            value is not None
            for value in (
                item.page,
                item.section,
                item.table,
                item.column,
                item.figure,
                item.equation,
                item.appendix,
            )
        )
        if not has_structural_locator:
            issues.append(
                ValidationIssue(
                    code="EVIDENCE_LOCATOR_MISSING",
                    severity=(IssueSeverity.ERROR if strict else IssueSeverity.WARNING),
                    message=(
                        "Evidence contains text but no page, section, table, figure, "
                        "equation, or appendix locator."
                    ),
                    path=path,
                )
            )

        if item.confidence and item.confidence.level is ConfidenceLevel.LOW:
            issues.append(
                ValidationIssue(
                    code="LOW_EVIDENCE_CONFIDENCE",
                    severity=IssueSeverity.WARNING,
                    message="The deterministic evidence score is low.",
                    path=f"{path}.confidence",
                )
            )

    issues.extend(causal_language_issues(record))
    valid = not any(issue.severity is IssueSeverity.ERROR for issue in issues)
    return ValidationReport(
        valid=valid,
        issues=issues,
        evidence_count=len(list(unique_evidence)),
        finding_count=len(record.findings) + len(record.heterogeneity),
    )
