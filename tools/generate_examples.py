"""Generate or verify deterministic v0.3 example artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from paperreading.domain import PaperRecord  # noqa: E402
from paperreading.migrations import migrate_v02_to_v03  # noqa: E402

SOURCE = ROOT / "examples" / "paper-record.example.json"
DESTINATION = ROOT / "examples" / "paper-package.example.json"
FIXED_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def rendered_example() -> str:
    record = PaperRecord.model_validate_json(SOURCE.read_text(encoding="utf-8"))
    package = migrate_v02_to_v03(record, migrated_at=FIXED_TIME)
    return (
        json.dumps(
            package.model_dump(mode="json", exclude_none=True),
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = rendered_example()
    if args.check:
        if (
            not DESTINATION.is_file()
            or DESTINATION.read_text(encoding="utf-8") != content
        ):
            print(f"Example is stale: {DESTINATION.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print("Examples are current.")
        return 0
    DESTINATION.write_text(content, encoding="utf-8", newline="\n")
    print("Examples generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
