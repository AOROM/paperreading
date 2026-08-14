"""Generate or verify deterministic v0.3 example artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from paperreading.application import ReviewDecisions  # noqa: E402
from paperreading.domain import (  # noqa: E402
    DocumentBlock,
    EvidenceSpan,
    EvidenceType,
    ExtractionCandidate,
    PaperRecord,
)
from paperreading.ingestion import TextDocumentParser  # noqa: E402
from paperreading.migrations import migrate_v02_to_v03  # noqa: E402
from paperreading.providers import (  # noqa: E402
    ExtractionStage,
    JsonExtractionManifest,
    JsonStagePayload,
)

RECORD_SOURCE = ROOT / "examples" / "paper-record.example.json"
TEXT_SOURCE = ROOT / "examples" / "source.example.md"
PACKAGE_DESTINATION = ROOT / "examples" / "paper-package.example.json"
EXTRACTION_DESTINATION = ROOT / "examples" / "extraction-manifest.example.json"
DECISIONS_DESTINATION = ROOT / "examples" / "review-decisions.example.json"
FIXED_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _json(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _normalized_hash(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _span(
    document_id: str,
    block: DocumentBlock,
    quoted_text: str,
    evidence_id: str,
) -> EvidenceSpan:
    block_text = block.text
    local_start = block_text.index(quoted_text)
    char_start = block.char_start + local_start
    return EvidenceSpan(
        evidence_id=evidence_id,
        source_id=document_id,
        type=EvidenceType.TEXT,
        page=block.page,
        section_path=block.section_path,
        block_id=block.block_id,
        char_start=char_start,
        char_end=char_start + len(quoted_text),
        quoted_text=quoted_text,
        text_hash=_normalized_hash(quoted_text),
    )


def rendered_package() -> str:
    record = PaperRecord.model_validate_json(RECORD_SOURCE.read_text(encoding="utf-8"))
    package = migrate_v02_to_v03(record, migrated_at=FIXED_TIME)
    return _json(package.model_dump(mode="json", exclude_none=True))


def rendered_extraction_manifest() -> str:
    document = TextDocumentParser().parse(TEXT_SOURCE, ingested_at=FIXED_TIME)
    blocks = document.pages[0].blocks
    title_block = next(item for item in blocks if "Synthetic source" in item.text)
    question_block = next(item for item in blocks if "hypothetical" in item.text)
    result_block = next(item for item in blocks if "tool adoption" in item.text)
    limitation_block = next(item for item in blocks if "fictional" in item.text)

    title = "Synthetic source for ingestion"
    question_quote = (
        "Does a hypothetical digital coordination tool change specialization in a"
        "\nsynthetic panel of firms?"
    )
    question = re.sub(r"\s+", " ", question_quote)
    finding_quote = (
        "In the synthetic example, tool adoption is associated with higher measured"
        "\nspecialization."
    )
    finding = re.sub(r"\s+", " ", finding_quote)
    limitation = (
        "All entities, observations, and results in this example are fictional."
    )
    evidence = {
        "ev-title": _span(document.document_id, title_block, title, "ev-title"),
        "ev-question": _span(
            document.document_id, question_block, question_quote, "ev-question"
        ),
        "ev-finding": _span(
            document.document_id, result_block, finding_quote, "ev-finding"
        ),
        "ev-limitation": _span(
            document.document_id,
            limitation_block,
            limitation,
            "ev-limitation",
        ),
    }

    def candidate(
        candidate_id: str,
        field_path: str,
        value: object,
        evidence_ids: list[str] | None = None,
    ) -> ExtractionCandidate:
        return ExtractionCandidate(
            candidate_id=candidate_id,
            field_path=field_path,
            value=value,
            evidence_ids=evidence_ids or [],
            extractor="offline-json",
            prompt_version="fixture-1",
        )

    stages = {
        ExtractionStage.METADATA: JsonStagePayload(
            candidates=[
                candidate("cand-paper-id", "record.paper_id", "synthetic-demo"),
                candidate("cand-record-type", "record.record_type", "other"),
                candidate(
                    "cand-metadata",
                    "record.metadata",
                    {
                        "title": title,
                        "authors": ["Unknown"],
                        "source_id": document.document_id,
                        "language": "en",
                        "keywords": ["synthetic example"],
                    },
                    ["ev-title"],
                ),
                candidate(
                    "cand-field-evidence",
                    "record.field_evidence",
                    {"metadata.title": ["ev-title"]},
                    ["ev-title"],
                ),
            ],
            evidence_index={"ev-title": evidence["ev-title"]},
            prompt_version="fixture-1",
        ),
        ExtractionStage.RESEARCH_QUESTIONS: JsonStagePayload(
            candidates=[
                candidate(
                    "cand-questions",
                    "record.research_questions",
                    [question],
                    ["ev-question"],
                )
            ],
            evidence_index={"ev-question": evidence["ev-question"]},
            prompt_version="fixture-1",
        ),
        ExtractionStage.THEORY: JsonStagePayload(
            candidates=[candidate("cand-theory", "record.theoretical_framework", {})],
            prompt_version="fixture-1",
        ),
        ExtractionStage.DATA: JsonStagePayload(
            candidates=[
                candidate(
                    "cand-data",
                    "record.data",
                    {"sample": "synthetic panel of firms"},
                    ["ev-question"],
                )
            ],
            evidence_index={"ev-question": evidence["ev-question"]},
            prompt_version="fixture-1",
        ),
        ExtractionStage.VARIABLES: JsonStagePayload(
            candidates=[candidate("cand-variables", "record.variables", [])],
            prompt_version="fixture-1",
        ),
        ExtractionStage.FINDINGS: JsonStagePayload(
            candidates=[
                candidate(
                    "cand-source-claims",
                    "record.source_claims",
                    [
                        {
                            "claim_id": "claim-question",
                            "statement": question,
                            "evidence_ids": ["ev-question"],
                        }
                    ],
                    ["ev-question"],
                ),
                candidate(
                    "cand-findings",
                    "record.findings",
                    [
                        {
                            "finding_id": "finding-demo",
                            "statement": finding,
                            "relationship": "positive",
                            "language_strength": "associational",
                            "evidence_ids": ["ev-finding"],
                        }
                    ],
                    ["ev-finding"],
                ),
            ],
            evidence_index={
                "ev-question": evidence["ev-question"],
                "ev-finding": evidence["ev-finding"],
            },
            prompt_version="fixture-1",
        ),
        ExtractionStage.LIMITATIONS: JsonStagePayload(
            candidates=[
                candidate(
                    "cand-limitations",
                    "record.limitations",
                    [
                        {
                            "limitation_id": "limitation-demo",
                            "statement": limitation,
                            "origin": "paper",
                            "evidence_ids": ["ev-limitation"],
                        }
                    ],
                    ["ev-limitation"],
                )
            ],
            evidence_index={"ev-limitation": evidence["ev-limitation"]},
            prompt_version="fixture-1",
        ),
    }
    manifest = JsonExtractionManifest(
        source_id=document.document_id,
        provider="offline-json",
        provider_version="1.0.0",
        stages=stages,
    )
    return _json(manifest.model_dump(mode="json", exclude_none=True))


def rendered_examples() -> dict[Path, str]:
    return {
        PACKAGE_DESTINATION: rendered_package(),
        EXTRACTION_DESTINATION: rendered_extraction_manifest(),
        DECISIONS_DESTINATION: _json(
            ReviewDecisions(
                notes=["Reviewed synthetic fixture; no ambiguity was present."]
            ).model_dump(mode="json")
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = rendered_examples()
    if args.check:
        stale = [
            path
            for path, content in rendered.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            for path in stale:
                print(f"Example is stale: {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print("Examples are current.")
        return 0
    for destination, content in rendered.items():
        destination.write_text(content, encoding="utf-8", newline="\n")
    print("Examples generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
