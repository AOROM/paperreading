# Changelog

All notable changes to PaperReading are documented in this file.

## [Unreleased]

No unreleased changes.

## [0.3.1] - 2026-08-14

### Added

- A bilingual, normative Research Principles contract derived from academic validity, evidence traceability, inference discipline, reproducibility, falsifiability, and research ethics.
- A principle-based decision gate and research-integrity section in the contribution and pull-request workflows.
- A repository hero illustration with documented generation provenance.
- The OSI-approved MIT License, with explicit Python distribution metadata, a standalone Skill license notice, and contribution terms.
- A CI licensing check that verifies repository declarations and the built wheel's license payload and metadata.
- An optional text-based PDF parser behind the existing document parser port.
- Provider-neutral staged extraction contracts and a deterministic offline JSON provider.
- Explicit `PaperDraft` candidate review and guarded `PaperPackage` finalization use cases.
- `extract`, `review`, `finalize`, and high-level `read` CLI commands.
- A linked synthetic extraction manifest and review-decision fixture for strict end-to-end verification.
- Parser, lifecycle, conflict-review, canonical-hash, PDF-adapter, and fuzzy-alignment regression tests.

### Changed

- Reorganized both README versions around a verifiable 60-second trial, audience-specific entry points, explicit capability boundaries, and a compact documentation map.
- Aligned Python package metadata with the evidence-grounded workflow positioning and added discoverability links and keywords.
- Clarified that the repository license does not relicense third-party research inputs, datasets, or extracted content.
- Separated source-binary hashes from canonical extracted-text hashes and made workflow timestamps injectable.
- Replaced whole-block fuzzy quotation comparison with conservative local-window alignment.
- Reorganized the roadmap into v0.4 Evidence Engine, v0.5 Research Library, v0.6 Research Intelligence, and v1.0 Stable Ecosystem gates.

### Boundaries

- PDF ingestion requires an existing text layer and does not provide OCR, geometry, table reconstruction, or figure extraction.
- The JSON provider replays inspected output; hosted model providers are not yet implemented.
- Batch processing, SQLite search, cross-paper synthesis, automatic gap discovery, and method auditors remain planned.

## [0.3.0] - 2026-08-11

### Added

- Versioned `PaperDocument`, `PaperDraft`, and `PaperPackage` contracts.
- A normalized evidence graph with stable `EvidenceSpan` identifiers and explicit verification states.
- Deterministic UTF-8 text and Markdown ingestion with section, block, character-range, and text-hash metadata.
- Source, page, block, section, quotation, and hash verification against supplied documents.
- A typed project configuration and atomic file repository under `.paperreading/`.
- `migrate`, `ingest`, and `verify` CLI commands and corresponding application use cases.
- Immutable v0.2 and v0.3 schema directories plus deterministic v0.3 examples.

### Changed

- Separated source-grounded paper content from researcher or AI-assisted analysis.
- Extended JSON, Markdown, validation, projection, and Excel paths to accept v0.3 packages.
- Made artifact writes refuse implicit overwrite unless `--force` is supplied.
- Updated the Codex Skill and bilingual documentation around the v0.3 evidence workflow.

### Compatibility

- v0.2 `PaperRecord` remains a supported public contract.
- Deterministic v0.2 → v0.3 migration preserves the legacy 13-field projection.
- Migrated evidence is explicitly marked unverified; migration does not claim source-content verification.
- PDF parsing, provider-driven extraction, batch processing, SQLite search, synthesis, and gap discovery remain unimplemented roadmap items.

## [0.2.0] - 2026-08-11

### Added

- A strict `PaperRecord` domain model independent of Excel and Codex.
- Typed evidence references with deterministic confidence scoring.
- Evidence traceability and causal-language validation reports.
- JSON and Markdown exporters with atomic output behavior.
- A first-class `paperreading` CLI and Python API.
- Public JSON Schemas, a synthetic rich-record example, and Core contract tests.
- Package, lint, type, schema, and build gates in CI.

### Changed

- Recast the 13 workbook fields as a backward-compatible projection.
- Moved the Excel implementation into `paperreading.exporters.excel`.
- Reduced the Codex Skill to an adapter that constructs and validates Core records.

### Compatibility

- The original `append_paper_reading.py` command remains available as a wrapper.
- Existing header validation, duplicate detection, style preservation, backup, temporary validation, and atomic replacement behavior remains covered by tests.
