# PaperReading Roadmap

**English** | [简体中文](ROADMAP.zh-CN.md)

The roadmap separates shipped behavior from research hypotheses. A milestone is complete only when its public contract, failure behavior, tests, and documentation are present.

## v0.2 — Core Refactor

Status: implemented in the repository.

- Canonical Pydantic `PaperRecord` and `EvidenceRef` models.
- Deterministic evidence-confidence scoring.
- Evidence and causal-language validation.
- Legacy 13-field projection.
- JSON, Markdown, and safe Excel exporters.
- `paperreading` CLI and importable Python API.
- Public JSON Schemas and synthetic example record.
- Codex Skill as an adapter to the Core.
- Lint, type, schema, package, Skill, and compatibility gates in CI.

## v0.3 — Evidence Engine

Status: planned.

- Section-aware PDF document model and optional parser dependency.
- Multi-pass extraction protocol with explicit provider interface.
- Claim-to-evidence graph and evidence deduplication.
- Extraction-consistency and cross-check inputs for confidence scoring.
- Expanded causal-language benchmark and unsupported-claim metric.
- First small, redistributable golden dataset.

## v0.4 — Batch Research Library

Status: planned.

- Batch ingestion with resumable failures.
- Local SQLite repository and versioned migrations.
- Search and filter by method, variable, dataset, and tag.
- Literature matrix, deterministic comparison, and record-level provenance.
- Incremental project index under `.paperreading/`.

## v0.5 — Research Intelligence

Status: planned.

- Consensus and conflict detection across records.
- Synthesis statements bound to supporting and contradicting paper IDs.
- Evidence-derived gap candidates using a published taxonomy.
- Feasibility and novelty assessment with transparent components.
- Executable research-design output derived from validated gaps.

## v0.6 — Empirical Method Auditors

Status: planned.

- OLS and panel fixed-effects checks.
- DID, staggered DID, and event-study checks.
- IV and RDD checks.
- PSM, placebo, and mediation interpretation checks.
- Method-specific fixtures and false-positive tests.

## v1.0 — Stable Ecosystem

Status: planned.

- Stable schema and migration policy.
- PyPI release and signed release artifacts.
- Provider and exporter plugin entry points.
- MCP, Zotero, BibTeX, and additional agent adapters.
- Public PaperReading-Bench methodology and baseline results.

## Invariants across every version

1. Source claim, reported evidence, and researcher assessment remain distinct.
2. Every derived cross-paper statement identifies its supporting records.
3. Causal wording never becomes stronger than the identification evidence.
4. The domain layer remains independent of interfaces, providers, and exporters.
5. Legacy Excel compatibility remains covered by failure-path tests.
6. Planned functionality is never documented as shipped functionality.
