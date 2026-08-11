"""Atomic text output shared by JSON and Markdown exporters."""

from __future__ import annotations

import os
import uuid
from pathlib import Path


def atomic_write_text(destination: Path, content: str, *, force: bool) -> None:
    destination = destination.expanduser().resolve()
    if destination.exists() and not force:
        raise FileExistsError(
            f"destination already exists; pass --force to replace it: {destination}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temporary, destination)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise
