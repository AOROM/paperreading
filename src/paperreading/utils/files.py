"""Atomic local-file output helpers."""

from __future__ import annotations

import json
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
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        os.replace(temporary, destination)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def atomic_write_json(destination: Path, payload: object, *, force: bool) -> None:
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    atomic_write_text(destination, content, force=force)
