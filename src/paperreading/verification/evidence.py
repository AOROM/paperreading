"""Resolve evidence locators and quotations against a PaperDocument."""

from __future__ import annotations

import hashlib
import re
from difflib import SequenceMatcher

from pydantic import Field

from paperreading.domain import (
    EvidenceSpan,
    EvidenceVerification,
    PackageState,
    PaperDocument,
    PaperPackage,
    VerificationStatus,
)
from paperreading.domain.base import DomainModel
from paperreading.validation.result import (
    IssueSeverity,
    ValidationIssue,
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _hash_text(text: str) -> str:
    return hashlib.sha256(_normalize(text).encode("utf-8")).hexdigest()


class PackageVerificationReport(DomainModel):
    valid: bool
    results: dict[str, EvidenceVerification]
    issues: list[ValidationIssue] = Field(default_factory=list)
    verified_count: int = Field(ge=0)
    partial_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)


def verify_span(
    evidence: EvidenceSpan,
    document: PaperDocument,
    *,
    minimum_quote_match: float = 0.95,
) -> EvidenceVerification:
    issues: list[str] = []
    source_match = evidence.source_id == document.document_id
    if not source_match:
        issues.append("source_id does not match the supplied document")

    pages = {page.page_number: page for page in document.pages}
    page = pages.get(evidence.page) if evidence.page is not None else None
    page_resolved = None if evidence.page is None else page is not None
    if page_resolved is False:
        issues.append("page locator does not resolve")

    blocks = document.block_index()
    block = blocks.get(evidence.block_id) if evidence.block_id else None
    block_resolved = None if evidence.block_id is None else block is not None
    if block_resolved is False:
        issues.append("block locator does not resolve")
    if block and evidence.page is not None and block.page != evidence.page:
        block_resolved = False
        issues.append("block locator does not belong to the specified page")

    char_range_resolved = None
    if evidence.char_start is not None and evidence.char_end is not None:
        char_range_resolved = bool(
            block
            and block.char_start <= evidence.char_start
            and evidence.char_end <= block.char_end
        )
        if not char_range_resolved:
            issues.append("character range does not resolve within the block")

    context = block.text if block else page.text if page else None
    quote_match = None
    text_hash_match = None
    if evidence.quoted_text:
        quoted = _normalize(evidence.quoted_text)
        text_hash_match = (
            None
            if not evidence.text_hash
            else _hash_text(evidence.quoted_text) == evidence.text_hash
        )
        if context is None:
            issues.append("quoted text cannot be checked without a resolved context")
        else:
            normalized_context = _normalize(context)
            quote_match = (
                1.0
                if quoted in normalized_context
                else round(SequenceMatcher(None, quoted, normalized_context).ratio(), 3)
            )
            if quote_match < minimum_quote_match:
                issues.append(
                    "quoted text does not meet the configured match threshold"
                )

    section_resolved = True
    if evidence.section_path and block:
        section_resolved = (
            block.section_path[: len(evidence.section_path)] == evidence.section_path
        )
        if not section_resolved:
            issues.append("section path does not match the specified block")
    elif evidence.section_path and page:
        section_resolved = any(
            item.section_path[: len(evidence.section_path)] == evidence.section_path
            for item in page.blocks
        )
        if not section_resolved:
            issues.append("section path does not resolve")
    elif evidence.section_path:
        section_resolved = False
        issues.append("section path cannot resolve without a page or block")

    unsupported_structural_locator = (
        bool(
            evidence.bbox
            or evidence.table
            or evidence.column
            or evidence.figure
            or evidence.equation
        )
        and not evidence.block_id
    )
    if unsupported_structural_locator:
        issues.append(
            "geometry, table, column, figure, or equation requires a block-aware "
            "parser for full verification"
        )

    hard_failure = (
        not source_match
        or page_resolved is False
        or block_resolved is False
        or char_range_resolved is False
        or not section_resolved
        or (quote_match is not None and quote_match < minimum_quote_match)
        or text_hash_match is False
    )
    if hard_failure:
        status = VerificationStatus.FAILED
    elif unsupported_structural_locator or (
        evidence.quoted_text and quote_match is None
    ):
        status = VerificationStatus.PARTIAL
    elif any(
        value is not None
        for value in (evidence.page, evidence.block_id, evidence.quoted_text)
    ):
        status = VerificationStatus.VERIFIED
    else:
        status = VerificationStatus.PARTIAL

    return EvidenceVerification(
        status=status,
        source_match=source_match,
        page_resolved=page_resolved,
        block_resolved=block_resolved,
        char_range_resolved=char_range_resolved,
        quote_match=quote_match,
        text_hash_match=text_hash_match,
        issues=issues,
    )


def verify_package(
    package: PaperPackage,
    document: PaperDocument,
    *,
    strict: bool = False,
    minimum_quote_match: float = 0.95,
) -> PackageVerificationReport:
    results = {
        evidence_id: verify_span(
            evidence,
            document,
            minimum_quote_match=minimum_quote_match,
        )
        for evidence_id, evidence in package.evidence_index.items()
    }
    issues: list[ValidationIssue] = []
    for evidence_id, result in results.items():
        if result.status is VerificationStatus.FAILED:
            issues.append(
                ValidationIssue(
                    code="EVIDENCE_VERIFICATION_FAILED",
                    severity=IssueSeverity.ERROR,
                    message="; ".join(result.issues) or "evidence verification failed",
                    path=f"evidence_index.{evidence_id}",
                )
            )
        elif result.status is VerificationStatus.PARTIAL:
            issues.append(
                ValidationIssue(
                    code="EVIDENCE_VERIFICATION_PARTIAL",
                    severity=IssueSeverity.ERROR if strict else IssueSeverity.WARNING,
                    message="; ".join(result.issues)
                    or "evidence is only partially verified",
                    path=f"evidence_index.{evidence_id}",
                )
            )
    verified = sum(
        item.status is VerificationStatus.VERIFIED for item in results.values()
    )
    partial = sum(
        item.status is VerificationStatus.PARTIAL for item in results.values()
    )
    failed = sum(item.status is VerificationStatus.FAILED for item in results.values())
    return PackageVerificationReport(
        valid=not any(item.severity is IssueSeverity.ERROR for item in issues),
        results=results,
        issues=issues,
        verified_count=verified,
        partial_count=partial,
        failed_count=failed,
    )


def apply_verification(
    package: PaperPackage,
    report: PackageVerificationReport,
) -> PaperPackage:
    if set(report.results) != set(package.evidence_index):
        raise ValueError("verification report evidence IDs must match the package")
    updated = package.model_copy(deep=True)
    for evidence_id, result in report.results.items():
        updated.evidence_index[evidence_id].verification = result
    fully_verified = report.valid and all(
        evidence.verification is not None
        and evidence.verification.status is VerificationStatus.VERIFIED
        for evidence in updated.evidence_index.values()
    )
    if fully_verified:
        updated.state = PackageState.VERIFIED
    elif updated.state is PackageState.VERIFIED:
        updated.state = PackageState.FINALIZED
    return PaperPackage.model_validate(updated.model_dump(mode="python"))
