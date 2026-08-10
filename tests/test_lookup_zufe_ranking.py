from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "papers-reading-skill" / "scripts" / "lookup_zufe_ranking.py"


def run_lookup(journal: str) -> dict:
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--journal", journal],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout or result.stderr)
    return json.loads(result.stdout)


class LookupZufeRankingTests(unittest.TestCase):
    def test_finds_exact_chinese_top_journal(self) -> None:
        result = run_lookup("中国社会科学（中文版）")
        self.assertTrue(result["historical"])
        self.assertEqual(
            result["matches"],
            [
                {
                    "journal": "中国社会科学（中文版）",
                    "domain": "中文",
                    "level": "TOP",
                    "cell_index": 5,
                }
            ],
        )

    def test_finds_exact_chinese_level_a_journal(self) -> None:
        result = run_lookup("经济研究")
        self.assertEqual(len(result["matches"]), 1)
        self.assertEqual(result["matches"][0]["level"], "一级A")

    def test_finds_exact_chinese_level_b_journal(self) -> None:
        result = run_lookup("《中国工业经济》")
        self.assertEqual(len(result["matches"]), 1)
        self.assertEqual(result["matches"][0]["level"], "一级B")

    def test_unknown_journal_returns_empty_matches(self) -> None:
        result = run_lookup("不存在的示例期刊")
        self.assertEqual(result["matches"], [])


if __name__ == "__main__":
    unittest.main()
