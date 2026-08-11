# Changelog

All notable changes to PaperReading will be documented in this file.

The project follows a lightweight Keep-a-Changelog style. Versioning will become strict once the reusable Python core reaches its first tagged release.

## [Unreleased]

### Added

- Reusable `paperreading` Python core for paper records, empirical designs, findings, and evidence anchors.
- Evidence-label rendering and evidence-coverage metrics.
- Dependency-free Literature Matrix generation and Markdown rendering.
- Portable JSON Schema for structured paper records.
- Architecture documentation and a staged product roadmap.
- `CITATION.cff` metadata.
- MIT License.
- Feature-request issue template.

### Changed

- Repositioned the project from a Codex-only skill to an evidence-grounded research workflow while preserving the existing skill and Excel writer.
- Updated bilingual README documentation around the new architecture and product direction.
- Extended CI compilation to cover the reusable Python core.

### Compatibility

- The existing `skills/papers-reading-skill/` runtime contract is intentionally unchanged in this restructuring.
- Existing workbook behavior and the 13-field Excel export remain unchanged.
