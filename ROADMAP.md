# PaperReading Roadmap

**English** | [简体中文](ROADMAP.zh-CN.md)

This roadmap separates shipped behavior from technical hypotheses. A capability is complete only when its public contract, migration or compatibility behavior, failure paths, tests, and documentation are present.

## Shipped foundations

### v0.2 — Research Intelligence Core

Status: implemented and retained as a compatibility contract.

- Strict `PaperRecord` and `EvidenceRef` models.
- Deterministic locator-specific confidence scoring.
- Evidence and causal-language validation.
- JSON, Markdown, legacy 13-field, and safe Excel outputs.
- CLI, Python API, public schemas, synthetic examples, and CI gates.

### v0.3 — Schema Separation & Migration

Status: implemented in the repository.

- `PaperDocument`, `PaperDraft`, and `PaperPackage` public models.
- Strict separation of source-grounded records and researcher analysis.
- Stable, de-duplicated evidence graph using `EvidenceSpan` IDs.
- Deterministic v0.2 → v0.3 migration with explicit provenance caveats.
- Deterministic UTF-8 text and Markdown ingestion with block and section locators.
- Source, page, block, section, quotation, and text-hash verification.
- Inspectable atomic file repository under `.paperreading/`.
- Versioned v0.2 and v0.3 JSON Schemas and deterministic examples.
- v0.3 support in validation, CLI, JSON, Markdown, legacy projection, and Excel.
- Regression proof that migrated packages preserve the v0.2 13-field projection.

## Next: complete the Evidence Engine

Status: planned; not implemented.

Exit criteria:

- Optional PDF parser behind a documented adapter boundary, with page geometry and table/figure limitations stated explicitly.
- Multi-pass extraction protocol behind a provider interface; no provider dependency in the domain.
- Candidate/conflict review flow from `PaperDraft` to finalized `PaperPackage`.
- Evidence verification for PDF blocks, tables, figures, and equations with typed partial states.
- Small redistributable golden dataset and published unsupported-claim, locator-resolution, and causal-language metrics.
- Reproducible prompt/provider metadata without storing secrets or copyrighted sources.

## v0.4 — Batch Research Library

Status: planned; not implemented.

- Resumable batch ingestion with item-level failure isolation.
- SQLite repository behind the existing repository port and versioned migrations.
- Search and filter by method, variable, dataset, evidence state, and tag.
- Deterministic literature matrix and record-level comparison provenance.
- Incremental project index and exportable run reports.

## v0.5 — Evidence-Grounded Synthesis

Status: planned; not implemented.

- Consensus and conflict detection across verified records.
- Every synthesis statement bound to supporting and contradicting paper IDs.
- Evidence-derived gap candidates using a published taxonomy.
- Transparent feasibility, novelty, and evidence-coverage components.
- Executable research designs derived from reviewed gaps, never presented as source findings.

## v0.6 — Empirical Method Auditors

Status: planned; not implemented.

- OLS and panel fixed-effects checks.
- DID, staggered DID, and event-study checks.
- IV and RDD checks.
- PSM, placebo, and mechanism-interpretation checks.
- Method-specific fixtures, abstention behavior, and false-positive tests.

## v1.0 — Stable Ecosystem

Status: planned; not implemented.

- Stable schema, deprecation, and migration policy.
- PyPI release and signed release artifacts.
- Provider, parser, repository, and exporter plugin entry points.
- MCP, Zotero, BibTeX, and additional agent adapters.
- Public PaperReading-Bench methodology and reproducible baselines.

## Cross-version invariants

These invariants are governed by the normative [Research Principles](RESEARCH_PRINCIPLES.md).

1. Source claims, reported evidence, and researcher analysis remain distinct.
2. Every derived cross-paper statement identifies its supporting records.
3. Causal wording never becomes stronger than the identification evidence.
4. Traceability and verification scores never masquerade as truth or study quality.
5. The domain remains independent of interfaces, providers, storage, and exporters.
6. Legacy Excel compatibility remains covered by success and failure-path tests.
7. Planned functionality is never documented as shipped functionality.
