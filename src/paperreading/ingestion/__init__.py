"""Source-aware ingestion adapters."""

from paperreading.ingestion.base import DocumentParser
from paperreading.ingestion.text import TextDocumentParser, parser_for_path

__all__ = ["DocumentParser", "TextDocumentParser", "parser_for_path"]
