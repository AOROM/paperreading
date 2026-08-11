"""Evidence and causal-language validation for PaperRecord objects."""

from paperreading.validation.evidence import validate_record
from paperreading.validation.package import validate_package
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
    "validate_package",
]
