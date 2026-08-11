# Changelog

All notable changes to PaperReading are documented in this file.

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
