# PaperReading Roadmap

**English** | [简体中文](ROADMAP.zh-CN.md)

This roadmap separates shipped behavior from technical hypotheses. A capability is complete only when its public contract, failure behavior, tests, documentation, and compatibility impact are present. Dates are intentionally absent: research validity gates releases, not calendar pressure.

## Shipped foundations

### v0.2 — Research Intelligence Core

Status: implemented and retained as a compatibility contract.

- Strict `PaperRecord` and `EvidenceRef` models.
- Deterministic locator-specific confidence scoring.
- Evidence and causal-language validation.
- JSON, Markdown, legacy 13-field, and safe Excel outputs.
- CLI, Python API, public schemas, synthetic examples, and CI gates.

### v0.3 — Schema Separation & Migration

Status: implemented.

- `PaperDocument`, `PaperDraft`, and `PaperPackage` public models.
- Separation of source-grounded records from researcher or AI-assisted analysis.
- Stable evidence graph using normalized `EvidenceSpan` IDs.
- Deterministic v0.2 → v0.3 migration with explicit provenance caveats.
- Atomic, inspectable project storage under `.paperreading/`.
- Versioned schemas and backward-compatible 13-field projection.

### v0.3.1 — Core Hardening

Status: implemented.

- One `DocumentParser` port for UTF-8 text, Markdown, and optional text-based PDF input.
- Explicit PDF limits: no OCR, layout geometry, table reconstruction, or figure extraction.
- Separate source-binary SHA-256 and canonical extracted-text SHA-256 identities.
- Injectable timezone-aware ingestion, extraction, and finalization times for reproducible runs.
- Provider-neutral staged extraction contract plus a deterministic offline JSON adapter.
- Candidate and conflict preservation through Draft → Review → Finalize.
- Finalization guard that rejects unresolved drafts, changed documents, overlapping fields, and missing evidence.
- Evidence Verification v2 using conservative local-window fuzzy quotation alignment.
- `extract`, `review`, `finalize`, and high-level `read` commands.
- A linked synthetic end-to-end fixture that passes strict source verification.

## v0.4 — Evidence Engine

Status: planned; not implemented.

Release gates:

- At least one real model provider adapter with structured-output validation, retry policy, rate-limit behavior, and secret-safe run metadata.
- Stage-specific prompt contracts and fixtures for metadata, questions, theory, data, variables, design, findings, mechanisms, heterogeneity, robustness, and limitations.
- PDF geometry adapter and OCR adapter as separate capabilities with explicit provenance and abstention behavior.
- Typed verification for tables, figures, equations, bounding boxes, and appendices; unsupported surfaces remain `partial` rather than being guessed.
- A redistributable PaperReading-Bench with versioned annotation guidance and published unsupported-claim, locator-resolution, quote-alignment, conflict, and causal-language metrics.
- Regression gates for both extraction quality and abstention quality; no benchmark is optimized on hidden or copyrighted source text.

## v0.5 — Research Library

Status: planned; not implemented.

Release gates:

- Resumable batch ingestion with item-level isolation, idempotency, and exportable run reports.
- SQLite repository behind the existing repository port, with explicit schema migrations and backup guidance.
- Search and filtering by method, variable, dataset, evidence state, source, and user tag.
- Deterministic literature matrices whose cells retain record and evidence provenance.
- Expanded empirical-method schema for estimand, treatment timing, comparison group, identifying assumptions, diagnostics, and uncertainty.
- Incremental indexing without silently changing previously finalized packages.

## v0.6 — Research Intelligence

Status: planned; not implemented.

Release gates:

- Cross-paper consensus and contradiction detection over reviewed records only.
- Every synthesis statement bound to supporting, contradicting, and excluded paper IDs.
- Evidence-derived gap candidates using a published taxonomy and visible coverage limits.
- Transparent feasibility, novelty, and evidence-coverage components; no opaque aggregate “research quality” score.
- Initial OLS, panel fixed-effects, DID, IV, and RDD auditors with method-specific abstention and false-positive tests.
- Executable research designs derived from reviewed gaps, stored as analysis rather than source findings.

## v1.0 — Stable Ecosystem

Status: planned; not implemented.

Release gates:

- Stable schema, deprecation, migration, and support policy.
- PyPI releases with signed provenance and reproducible build guidance.
- Provider, parser, repository, verifier, and exporter plugin entry points.
- MCP, Zotero, BibTeX, and additional agent adapters.
- Public PaperReading-Bench methodology, baselines, limitations, and governance.
- Security, privacy, copyright, and data-retention guidance suitable for real research teams.

## Cross-version invariants

These invariants are governed by the normative [Research Principles](RESEARCH_PRINCIPLES.md).

1. Source claims, reported evidence, and researcher analysis remain distinct.
2. Every derived cross-paper statement identifies the records that support, contradict, or were excluded from it.
3. Causal wording never becomes stronger than the identification evidence.
4. Traceability and verification scores never masquerade as truth or study quality.
5. The domain remains independent of interfaces, providers, storage, and exporters.
6. Missing, conflicting, and unsupported information remains visible; the system may abstain.
7. Reproducibility records source identity, extracted-text identity, configuration, provider, model, prompt versions, and time.
8. Legacy Excel compatibility remains covered by success and failure-path tests.
9. Planned functionality is never documented as shipped functionality.
