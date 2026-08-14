"""Extraction provider ports and deterministic adapters."""

from paperreading.providers.base import (
    DEFAULT_EXTRACTION_STAGES,
    ExtractionProvider,
    ExtractionStage,
    ExtractionStageResult,
    ExtractionTask,
)
from paperreading.providers.json import (
    JsonExtractionManifest,
    JsonExtractionProvider,
    JsonStagePayload,
)

__all__ = [
    "DEFAULT_EXTRACTION_STAGES",
    "ExtractionProvider",
    "ExtractionStage",
    "ExtractionStageResult",
    "ExtractionTask",
    "JsonExtractionManifest",
    "JsonExtractionProvider",
    "JsonStagePayload",
]
