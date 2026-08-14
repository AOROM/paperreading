"""Use cases shared by CLI and future interfaces."""

from paperreading.application.extract import ExtractDocument
from paperreading.application.finalize import FinalizeDraft
from paperreading.application.ingest import IngestDocument
from paperreading.application.migrate import MigrateRecord
from paperreading.application.review import ReviewDraft
from paperreading.application.verify import VerifyPackage
from paperreading.application.workflow import ExtractionBundle, ReviewDecisions

__all__ = [
    "ExtractDocument",
    "ExtractionBundle",
    "FinalizeDraft",
    "IngestDocument",
    "MigrateRecord",
    "ReviewDraft",
    "ReviewDecisions",
    "VerifyPackage",
]
