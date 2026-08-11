"""Portable research-intelligence primitives for PaperReading."""

from .evidence import evidence_coverage, evidence_label
from .matrix import build_literature_matrix, matrix_to_markdown
from .models import EmpiricalDesign, EvidenceRef, Finding, PaperRecord

__all__ = [
    "EmpiricalDesign",
    "EvidenceRef",
    "Finding",
    "PaperRecord",
    "build_literature_matrix",
    "evidence_coverage",
    "evidence_label",
    "matrix_to_markdown",
]
