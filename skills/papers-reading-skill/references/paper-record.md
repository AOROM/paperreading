# PaperPackage Construction Contract

Use the v0.3 `PaperPackage` as the current research asset. Retain v0.2 `PaperRecord` only for compatibility or as input to deterministic migration. The 13 Excel columns are an output projection, not a source model.

## Package boundaries

- `document`: source identity, name, format, media type, hash, size, page count, and ingestion time.
- `record`: source-derived facts in `GroundedPaperRecord` only.
- `evidence_index`: normalized `EvidenceSpan` objects keyed by their exact `evidence_id`.
- `analysis`: researcher or AI-assisted assessment and proposed research extensions.
- `audit`: optional method-specific audit output; omit it when no auditor has run.
- `run`: pipeline version, source/config hashes, provider metadata when applicable, prompt versions, and creation time.
- `migration_notes`: provenance limitations introduced by version migration.

## GroundedPaperRecord

- `metadata`: exact bibliographic facts, source identifier, keywords, and independently sourced ranking evidence.
- `record_type`: empirical, theoretical, review, or other.
- `research_questions`: one to three concrete questions answered by the paper.
- `theoretical_framework`: named theory, propositions, and the paper's causal or explanatory chain.
- `data`: sample, period, sources, and exclusions.
- `variables`: one object per reported variable with role, definition, measurement, and source when available.
- `empirical_design`: required for empirical records; include method, equation, fixed effects, standard errors, identification, endogeneity treatments, and robustness checks.
- `source_claims`: statements explicitly made by the paper, each bound to one or more evidence IDs.
- `findings`: reported results, relationship direction, language strength, and evidence IDs.
- `mechanisms`, `heterogeneity`, and `robustness`: include only analyses actually reported.
- `limitations`: use paper-reported limitations; preserve a legacy-unknown origin after migration.
- `field_evidence`: optional evidence IDs for structured fields not represented by a typed claim.

Do not put researcher criticism, inferred gaps, or proposed designs in this object.

## EvidenceSpan

Every source claim and empirical result must resolve to one or more keys in `evidence_index`:

```json
{
  "evidence_id": "ev-0123456789abcdef",
  "source_id": "src-0123456789abcdef",
  "type": "TEXT",
  "page": 1,
  "section_path": ["Results"],
  "block_id": "p1-b0007",
  "char_start": 420,
  "char_end": 581,
  "quoted_text": "A faithfully copied source passage.",
  "text_hash": "sha256-of-normalized-quoted-text"
}
```

Allowed types are `TEXT`, `TABLE`, `FIGURE`, `EQUATION`, `APPENDIX`, and `METADATA`. Use only locators present in the supplied source. The key in `evidence_index` must equal `evidence_id`, and every referenced ID must exist.

Traceability is recalculated from locator specificity. Verification is created only by checking the span against a supplied `PaperDocument`. Neither value measures truth or study quality.

Table, figure, equation, or column references without a block-aware document may remain partially verified. Preserve that state rather than pretending full resolution.

## ResearchAnalysis

- `assessments`: interpretation, limitations, and caveats, each with an explicit origin and optional basis evidence IDs.
- `research_extensions`: proposed designs with a gap type, question, optional supporting evidence IDs, assumptions, and at least one executable design element.

An executable element can be an identification strategy, sample, data source, variable construction, mechanism test, or falsification test. Do not generate a gap from generic novelty language. Ground it in evidence, a reported limitation, contradiction, measurement boundary, or identification constraint.

The legacy 13-field projection requires at least one research extension because its thirteenth field is mandatory. JSON and Markdown package outputs do not impose that legacy requirement.

## Causal discipline

Set `language_strength` to `causal` only when both conditions hold:

1. The design is causally eligible, such as DID, IV, RDD, event study, or randomized assignment.
2. The record states an explicit identification strategy and supplied evidence supports it.

Fixed effects, cross-sectional OLS, correlation, and PSM alone do not automatically authorize causal language. When the paper itself uses stronger language, preserve that wording as a source claim if necessary and keep the assessment caveat separate.

## Lifecycle and verification

- `migrated`: created from v0.2; evidence has not been checked against source content.
- `finalized`: structurally complete package produced by a reviewed adapter workflow.
- `verified`: evidence verification ran and produced no errors under the selected mode.
- `audited`: reserved for a package with a completed method audit.

Do not set lifecycle state manually to imply work that did not run.

## Compatibility resources

- Inspect `schemas/v0.3/package.schema.json` or run `paperreading schema --kind package` for exact constraints.
- Inspect `schemas/v0.3/document.schema.json` for document blocks and manifests.
- Use `examples/paper-package.example.json` as a migration-structure example, never as research evidence.
- Run `paperreading validate <package.json> --strict` to require fully verified evidence.
- Use `paperreading migrate <record.json>` for v0.2 input; do not hand-edit the schema version.
