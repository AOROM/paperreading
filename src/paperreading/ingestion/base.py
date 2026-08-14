"""Document parser port."""

from datetime import datetime
from pathlib import Path
from typing import Protocol

from paperreading.domain import PaperDocument


class DocumentParser(Protocol):
    def supports(self, source: Path) -> bool: ...

    def parse(
        self,
        source: Path,
        *,
        ingested_at: datetime | None = None,
    ) -> PaperDocument: ...
