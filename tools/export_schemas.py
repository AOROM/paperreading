"""Generate or verify the public PaperReading JSON Schemas."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from paperreading.domain import EvidenceRef, PaperRecord  # noqa: E402

SCHEMAS = {
    ROOT / "schemas" / "paper.schema.json": PaperRecord.model_json_schema,
    ROOT / "schemas" / "evidence.schema.json": EvidenceRef.model_json_schema,
}


def rendered_schemas() -> dict[Path, str]:
    return {
        path: json.dumps(factory(), ensure_ascii=False, indent=2) + "\n"
        for path, factory in SCHEMAS.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    mismatches = []
    for path, content in rendered_schemas().items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                mismatches.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")

    if mismatches:
        for path in mismatches:
            print(f"Schema is stale: {path}", file=sys.stderr)
        return 1
    print("Schemas are current." if args.check else "Schemas generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
