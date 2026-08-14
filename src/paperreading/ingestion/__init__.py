"""Source-aware ingestion adapters."""

from paperreading.ingestion.base import DocumentParser
from paperreading.ingestion.pdf import PdfDocumentParser
from paperreading.ingestion.text import TextDocumentParser, parser_for_path

__all__ = [
    "DocumentParser",
    "PdfDocumentParser",
    "TextDocumentParser",
    "parser_for_path",
]
