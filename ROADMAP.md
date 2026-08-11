# PaperReading Roadmap

PaperReading is evolving from a single Codex paper-reading skill into an evidence-grounded research workflow for empirical social science. The roadmap intentionally keeps the existing skill and Excel workflow stable while moving reusable logic into a portable core.

## v0.2 — Research-intelligence foundation

Status: **in progress**

- [x] Reposition the repository around evidence-grounded empirical research.
- [x] Introduce portable `PaperRecord`, `EmpiricalDesign`, `Finding`, and `EvidenceRef` models.
- [x] Add a JSON Schema for interoperable paper records.
- [x] Add evidence labels and evidence-coverage metrics.
- [x] Add a dependency-free Literature Matrix builder.
- [x] Keep the current Codex skill and safe Excel append workflow compatible.
- [x] Add MIT license, citation metadata, changelog, architecture documentation, and feature-request template.
- [ ] Add representative public-domain / redistributable example outputs from finance, economics, and management.
- [ ] Add a short visual demo for the README.

## v0.3 — Evidence Map and method audit

- [ ] Normalize page, section, table, and figure anchors from model output.
- [ ] Render claim-to-evidence maps for each major finding.
- [ ] Add explicit evidence status: direct, inferred, missing, conflicting.
- [ ] Add method-audit adapters for panel FE, DID, IV, RDD, PSM, mediation, and common robustness designs.
- [ ] Add warnings for causal language that is stronger than the reported identification strategy.
- [ ] Export evidence maps to Markdown and JSON.

## v0.4 — Batch reading and synthesis

- [ ] Batch ingest a directory of structured paper records.
- [ ] Produce configurable Literature Matrices.
- [ ] Detect consensus, conflicting evidence, recurring mechanisms, common datasets, and repeated identification choices.
- [ ] Generate research-gap candidates grounded in the compared papers.
- [ ] Require every proposed gap to reference the papers and evidence that motivate it.

## v0.5 — Research workflow integrations

- [ ] Markdown exporter.
- [ ] BibTeX metadata bridge.
- [ ] Zotero-compatible export/import workflow.
- [ ] Obsidian-oriented Markdown template.
- [ ] Agent adapters beyond the existing Codex skill where stable integration contracts exist.
- [ ] Optional CLI for validate / matrix / export workflows.

## v0.6 — Benchmark and quality metrics

- [ ] Publish a redistributable PaperReading benchmark set.
- [ ] Measure metadata accuracy, variable accuracy, method accuracy, evidence-anchor accuracy, field completeness, and hallucination rate.
- [ ] Add regression tests against gold structured records.
- [ ] Publish benchmark methodology and limitations.

## v1.0 — Stable research workflow

Target criteria:

- stable paper-record schema with migration policy;
- auditable evidence model;
- batch comparison and synthesis;
- at least three durable export targets;
- benchmarked extraction quality;
- contributor documentation and release discipline;
- no dependence on a single agent client for the core data model.

## Contribution priorities

Good first contributions include:

1. adding sanitized example `PaperRecord` files;
2. adding matrix columns without introducing mandatory dependencies;
3. improving schema validation error messages;
4. documenting discipline-specific empirical methods;
5. adding tests for evidence edge cases;
6. proposing exporters behind small, stable interfaces.

Please open a feature request before large architectural changes so the data contract remains coherent.
