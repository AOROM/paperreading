"""Validate v0.3 package evidence state and causal-language strength."""

from __future__ import annotations

from paperreading.domain import (
    DesignType,
    LanguageStrength,
    PaperPackage,
    VerificationStatus,
)
from paperreading.validation.result import (
    IssueSeverity,
    ValidationIssue,
    ValidationReport,
)

CAUSAL_DESIGNS = {
    DesignType.DID,
    DesignType.STAGGERED_DID,
    DesignType.IV,
    DesignType.RDD,
    DesignType.EVENT_STUDY,
    DesignType.RCT,
}


def validate_package(
    package: PaperPackage,
    *,
    strict: bool = False,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for evidence_id, evidence in package.evidence_index.items():
        verification = evidence.verification
        path = f"evidence_index.{evidence_id}"
        if verification is None or verification.status is VerificationStatus.NOT_RUN:
            issues.append(
                ValidationIssue(
                    code="EVIDENCE_NOT_VERIFIED",
                    severity=IssueSeverity.ERROR if strict else IssueSeverity.WARNING,
                    message="Evidence has not been checked against a PaperDocument.",
                    path=path,
                )
            )
        elif verification.status is VerificationStatus.FAILED:
            issues.append(
                ValidationIssue(
                    code="EVIDENCE_VERIFICATION_FAILED",
                    severity=IssueSeverity.ERROR,
                    message="Evidence failed source-content verification.",
                    path=path,
                )
            )
        elif strict and verification.status is VerificationStatus.PARTIAL:
            issues.append(
                ValidationIssue(
                    code="EVIDENCE_VERIFICATION_PARTIAL",
                    severity=IssueSeverity.ERROR,
                    message="Strict validation requires fully verified evidence.",
                    path=path,
                )
            )

    design = package.record.empirical_design
    causal_supported = bool(
        design and design.type in CAUSAL_DESIGNS and design.identification_strategy
    )
    findings = [*package.record.findings, *package.record.heterogeneity]
    located_findings = [
        *(
            (f"record.findings[{index}]", finding)
            for index, finding in enumerate(package.record.findings)
        ),
        *(
            (f"record.heterogeneity[{index}]", finding)
            for index, finding in enumerate(package.record.heterogeneity)
        ),
    ]
    for path, finding in located_findings:
        if (
            finding.language_strength is LanguageStrength.CAUSAL
            and not causal_supported
        ):
            issues.append(
                ValidationIssue(
                    code="CAUSAL_LANGUAGE_UNSUPPORTED",
                    severity=IssueSeverity.ERROR,
                    message=(
                        "Causal language requires an eligible design and an explicit "
                        "identification strategy."
                    ),
                    path=f"{path}.language_strength",
                )
            )

    valid = not any(issue.severity is IssueSeverity.ERROR for issue in issues)
    return ValidationReport(
        valid=valid,
        issues=issues,
        evidence_count=len(package.evidence_index),
        finding_count=len(findings),
    )
