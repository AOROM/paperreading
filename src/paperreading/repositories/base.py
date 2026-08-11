"""Repository port for local research artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from paperreading.domain import PaperDocument, PaperDraft, PaperPackage


class ResearchRepository(Protocol):
    def initialize(self, *, force_config: bool = False) -> Path: ...

    def save_document(
        self, document: PaperDocument, *, force: bool = False
    ) -> Path: ...

    def load_document(self, document_id: str) -> PaperDocument: ...

    def save_draft(self, draft: PaperDraft, *, force: bool = False) -> Path: ...

    def save_package(self, package: PaperPackage, *, force: bool = False) -> Path: ...

    def load_package(self, paper_id: str) -> PaperPackage: ...
