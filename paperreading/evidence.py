"""Helpers for rendering and measuring source evidence."""

from __future__ import annotations

from .models import EvidenceRef, PaperRecord


def evidence_label(ref: EvidenceRef) -> str:
    """Render a compact human-readable evidence anchor."""

    ref.validate()
    parts: list[str] = []
    if ref.page is not None:
        parts.append(f"p. {ref.page}")
    if ref.section:
        parts.append(ref.section)
    if ref.table:
        parts.append(ref.table)
    if ref.figure:
        parts.append(ref.figure)
    if ref.note:
        parts.append(ref.note)
    return " · ".join(parts)


def evidence_coverage(record: PaperRecord) -> float:
    """Return the share of findings that contain at least one evidence anchor."""

    record.validate()
    if not record.findings:
        return 0.0
    grounded = sum(1 for finding in record.findings if finding.evidence)
    return grounded / len(record.findings)
