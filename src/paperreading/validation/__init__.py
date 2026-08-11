"""Evidence and causal-language validation for PaperRecord objects."""

from paperreading.validation.evidence import validate_record
from paperreading.validation.result import (
    IssueSeverity,
    ValidationIssue,
    ValidationReport,
)

__all__ = [
    "IssueSeverity",
    "ValidationIssue",
    "ValidationReport",
    "validate_record",
]
