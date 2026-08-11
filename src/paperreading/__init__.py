"""Evidence-grounded research intelligence primitives."""

from paperreading.domain import PaperRecord
from paperreading.projections import LEGACY_FIELDS, to_legacy_13_fields
from paperreading.validation import ValidationReport, validate_record

__all__ = [
    "LEGACY_FIELDS",
    "PaperRecord",
    "ValidationReport",
    "to_legacy_13_fields",
    "validate_record",
]

__version__ = "0.2.0"
