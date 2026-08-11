"""Compatibility entry point for the PaperReading Core Excel exporter."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path


def _load_core() -> Callable[[], int]:
    repository_src = Path(__file__).resolve().parents[3] / "src"
    if repository_src.is_dir() and str(repository_src) not in sys.path:
        sys.path.insert(0, str(repository_src))
    try:
        from paperreading.exporters.excel import legacy_main

        return legacy_main
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            f"PaperReading Core dependency '{exc.name}' is unavailable. Install the "
            "repository with the excel extra before using this compatibility script."
        ) from exc


if __name__ == "__main__":
    try:
        main = _load_core()
        raise SystemExit(main())
    except Exception as exc:
        print(
            json.dumps({"action": "error", "message": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        raise SystemExit(1) from None
