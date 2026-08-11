---
name: papers-reading-skill
description: Evidence-grounded AI research workflow for converting supplied finance, economics, management, and social-science papers into strict PaperRecord JSON, binding claims and findings to source locators, validating causal language with the PaperReading CLI, projecting the legacy 13 fields, and exporting JSON, Markdown, or safe Excel rows. Use when Codex needs to read or review a paper, extract metadata, questions, theory, variables, empirical methods, findings, mechanisms, robustness, limitations, or research extensions, or update a literature-review workbook without damaging existing content.
---

# PaperReading Core Adapter

## Workflow

1. Establish the supplied source boundary and identify available title, author, journal, date, DOI, page, section, table, figure, equation, and appendix metadata.
2. Read the abstract and introduction, theory or hypotheses, data and variables, research design, baseline results, mechanisms, heterogeneity, robustness or endogeneity checks, conclusion, and relevant appendix material.
3. Build one canonical `PaperRecord` using `references/paper-record.md`. Keep source claims, reported findings, and researcher assessment in their separate model fields.
4. Save the record as UTF-8 JSON, then run `paperreading validate <record.json>`. Use `--strict` when every evidence item must carry a structural locator.
5. Resolve every validation error before export. Preserve warnings in the review handoff instead of silently strengthening the source evidence.
6. Produce the user-selected output through the CLI. Use `references/reading-fields.md` only when reviewing the legacy 13-field projection or its workbook style.

## Evidence protocol

- Record a source claim only when the paper explicitly states it and bind it to at least one `EvidenceRef`.
- Record a finding only when the supplied text, table, figure, equation, or appendix supports it.
- Keep researcher assessment separate from both source claims and reported findings.
- Preserve null results, caveats, sample limits, identification limits, and unresolved information.
- Never fabricate a quotation, page, section, table, column, figure, equation, appendix, variable, model, test, ranking, or causal claim.
- Treat confidence as rule-derived output from evidence specificity. Do not invent or manually inflate a confidence score.
- Do not translate one journal-ranking system into another. Record only independently verified labels with their source and version boundary.

## CLI operations

Validate the canonical record:

```bash
paperreading validate record.json
```

Review the backward-compatible 13-field projection without changing a workbook:

```bash
paperreading project record.json
```

Export a reviewable artifact:

```bash
paperreading export record.json review.md --format markdown
paperreading export record.json record.normalized.json --format json
```

Append to an existing compatible workbook only after the user authorizes that destination:

```bash
paperreading export record.json literature.xlsx --format excel --sheet 中文
```

The legacy `scripts/append_paper_reading.py` entry point remains a compatibility wrapper for existing 13-field JSON payloads. Prefer the CLI for new workflows.

## Mutation rules

- Produce draft or validation output when no destination is explicitly provided.
- Do not overwrite JSON or Markdown output unless the user requests replacement and `--force` is used.
- For Excel, require an explicit path or the existing `PAPER_READING_WORKBOOK` configuration.
- Treat `duplicate_skipped` as a successful no-op; report the existing worksheet row.
- Treat schema mismatch, locked workbook, validation failure, or write error as a hard stop.
- After a successful Excel append, report the worksheet, appended row, and timestamped backup path.

If the `paperreading` command is unavailable, report that the Core package with the required exporter extra must be installed. Do not bypass the validator or reimplement workbook mutation ad hoc.
