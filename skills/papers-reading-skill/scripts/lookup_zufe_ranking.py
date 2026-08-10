"""Look up an exact journal name in the bundled historical ZUFE 2020 directory."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path


DEFAULT_POLICY = (
    Path(__file__).resolve().parents[1]
    / "references"
    / "zufe-journal-ranking-policy-fulltext.txt"
)
DOMAIN_RE = re.compile(r"^[一二]、(?P<domain>中文|外文)期刊目录$")
LEVEL_RE = re.compile(r"^（[一二三]）(?P<level>TOP|一级A|一级B)期刊（\d+本）$")


def normalize(value: str) -> str:
    text = unicodedata.normalize("NFKC", value).casefold()
    return "".join(character for character in text if character.isalnum())


def lookup(policy_path: Path, journal: str) -> list[dict[str, object]]:
    query = normalize(journal)
    if not query:
        raise ValueError("期刊名称不能为空。")

    text = policy_path.read_text(encoding="utf-8")
    domain: str | None = None
    level: str | None = None
    matches: list[dict[str, object]] = []

    for cell_index, cell in enumerate(text.split("\x07")):
        for raw_line in cell.splitlines():
            line = raw_line.strip()
            domain_match = DOMAIN_RE.fullmatch(line)
            if domain_match:
                domain = domain_match.group("domain")
                level = None
                continue

            level_match = LEVEL_RE.fullmatch(line)
            if level_match and domain is not None:
                level = level_match.group("level")

        if domain is None or level is None:
            continue
        candidate = " ".join(part.strip() for part in cell.splitlines() if part.strip())
        if normalize(candidate) == query:
            matches.append(
                {
                    "journal": candidate,
                    "domain": domain,
                    "level": level,
                    "cell_index": cell_index,
                }
            )

    return matches


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--journal", required=True, help="Exact journal name to look up"
    )
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    policy = args.policy.expanduser().resolve()
    if not policy.is_file():
        raise FileNotFoundError(f"政策文本不存在：{policy}")

    result = {
        "action": "lookup_complete",
        "query": args.journal,
        "policy_version": "2020修订",
        "historical": True,
        "matches": lookup(policy, args.journal),
        "warning": "历史目录不自动代表当前等级；当前用途必须核验官方最新版本。",
    }
    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2 if args.pretty else None,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            json.dumps(
                {"action": "error", "message": str(exc)},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        raise SystemExit(1)
