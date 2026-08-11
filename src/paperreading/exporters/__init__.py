"""Output adapters; optional integrations are imported only when selected."""

from paperreading.exporters.base import Exporter, ExportFormat, ExportResult
from paperreading.exporters.json import JsonExporter
from paperreading.exporters.markdown import MarkdownExporter

__all__ = [
    "ExportFormat",
    "Exporter",
    "ExportResult",
    "JsonExporter",
    "MarkdownExporter",
]
