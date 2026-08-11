"""Guard causal wording with explicit identification evidence."""

from __future__ import annotations

import re

from paperreading.domain import DesignType, PaperRecord
from paperreading.validation.result import (
    IssueSeverity,
    ValidationIssue,
)

CAUSAL_DESIGNS = {
    DesignType.DID,
    DesignType.STAGGERED_DID,
    DesignType.IV,
    DesignType.RDD,
    DesignType.EVENT_STUDY,
    DesignType.RCT,
}

CAUSAL_LANGUAGE_RE = re.compile(
    r"(?:\bcauses?\b|\bleads? to\b|\bincreases?\b|\breduces?\b|"
    r"导致|促进|提高|增加|降低|减少|抑制|影响)",
    re.IGNORECASE,
)


def causal_language_issues(record: PaperRecord) -> list[ValidationIssue]:
    """Return causal-language violations without rewriting source statements."""

    issues: list[ValidationIssue] = []
    design = record.empirical_design
    design_supports_causality = design.type in CAUSAL_DESIGNS and bool(
        design.identification_strategy
    )

    findings = [*record.findings, *record.heterogeneity]
    for index, finding in enumerate(findings):
        causal_wording = bool(CAUSAL_LANGUAGE_RE.search(finding.statement))
        if (finding.causal or causal_wording) and not design_supports_causality:
            severity = IssueSeverity.ERROR if finding.causal else IssueSeverity.WARNING
            issues.append(
                ValidationIssue(
                    code="CAUSAL_LANGUAGE_WARNING",
                    severity=severity,
                    message=(
                        "Causal wording is not supported by both an eligible design "
                        "type and an explicit identification strategy."
                    ),
                    path=f"findings[{index}].statement",
                )
            )

    if design.type in CAUSAL_DESIGNS and not design.identification_strategy:
        issues.append(
            ValidationIssue(
                code="IDENTIFICATION_STRATEGY_MISSING",
                severity=IssueSeverity.WARNING,
                message=(
                    "The design type can support causal inference, but the record does "
                    "not state its identification strategy."
                ),
                path="empirical_design.identification_strategy",
            )
        )
    return issues
