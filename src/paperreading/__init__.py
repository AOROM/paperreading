"""Evidence-grounded research intelligence primitives."""

from paperreading.artifacts import ResearchArtifact, as_package, load_artifact
from paperreading.domain import PaperDocument, PaperDraft, PaperPackage, PaperRecord
from paperreading.migrations import migrate_v02_to_v03
from paperreading.projections import LEGACY_FIELDS, to_legacy_13_fields
from paperreading.validation import ValidationReport, validate_package, validate_record

__all__ = [
    "LEGACY_FIELDS",
    "PaperDocument",
    "PaperDraft",
    "PaperPackage",
    "PaperRecord",
    "ResearchArtifact",
    "ValidationReport",
    "as_package",
    "load_artifact",
    "migrate_v02_to_v03",
    "to_legacy_13_fields",
    "validate_package",
    "validate_record",
]

__version__ = "0.3.1"
