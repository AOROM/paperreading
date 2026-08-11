"""Document parser port."""

from pathlib import Path
from typing import Protocol

from paperreading.domain import PaperDocument


class DocumentParser(Protocol):
    def parse(self, source: Path) -> PaperDocument: ...
