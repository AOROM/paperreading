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

from paperreading.domain import (  # noqa: E402
    EvidenceRef,
    EvidenceSpan,
    PaperDocument,
    PaperDraft,
    PaperPackage,
    PaperRecord,
)

SCHEMAS = {
    # Stable root aliases.  The v0.2 names remain backward compatible.
    ROOT / "schemas" / "paper.schema.json": PaperRecord.model_json_schema,
    ROOT / "schemas" / "evidence.schema.json": EvidenceRef.model_json_schema,
    ROOT / "schemas" / "package.schema.json": PaperPackage.model_json_schema,
    ROOT / "schemas" / "document.schema.json": PaperDocument.model_json_schema,
    ROOT / "schemas" / "draft.schema.json": PaperDraft.model_json_schema,
    ROOT / "schemas" / "evidence-span.schema.json": EvidenceSpan.model_json_schema,
    # Immutable versioned contracts.
    ROOT / "schemas" / "v0.2" / "paper.schema.json": PaperRecord.model_json_schema,
    ROOT / "schemas" / "v0.2" / "evidence.schema.json": EvidenceRef.model_json_schema,
    ROOT / "schemas" / "v0.3" / "package.schema.json": PaperPackage.model_json_schema,
    ROOT / "schemas" / "v0.3" / "document.schema.json": PaperDocument.model_json_schema,
    ROOT / "schemas" / "v0.3" / "draft.schema.json": PaperDraft.model_json_schema,
    ROOT
    / "schemas"
    / "v0.3"
    / "evidence-span.schema.json": EvidenceSpan.model_json_schema,
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
