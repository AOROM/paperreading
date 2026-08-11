# PaperRecord Construction Contract

Use `PaperRecord` as the canonical internal object. The 13 Excel columns are a projection, not the source model.

## Object boundaries

- `metadata`: exact bibliographic facts, source identifier, keywords, and independently sourced ranking evidence.
- `research_questions`: one to three concrete questions answered by the paper.
- `theoretical_framework`: named theory, propositions, and the paper's causal or explanatory chain.
- `data`: sample, period, sources, and exclusions.
- `variables`: one object per variable with role, definition, measurement, and source when reported.
- `empirical_design`: design type, method, equation, fixed effects, standard errors, identification strategy, endogeneity treatments, and robustness checks.
- `source_claims`: statements explicitly made by the paper, each bound to evidence.
- `findings`: reported results, relationship direction, causal flag, and supporting evidence.
- `mechanisms`, `heterogeneity`, and `robustness`: include only analyses actually reported.
- `limitations`: reported or clearly marked researcher-identified boundaries.
- `extensions`: two to four paper-specific designs with at least one executable element.
- `researcher_assessment`: interpretation that must remain visibly separate from source claims and findings.
- `evidence`: optional document-level catalogue; evidence attached to typed objects remains authoritative.

## EvidenceRef

Every source claim, finding, mechanism, and robustness result must include at least one evidence object:

```json
{
  "source_id": "paper-id-or-doi",
  "type": "TABLE",
  "page": 12,
  "section": "4.2 Baseline Results",
  "table": "Table 3",
  "column": "(4)"
}
```

Allowed types are `TEXT`, `TABLE`, `FIGURE`, `EQUATION`, `APPENDIX`, and `METADATA`. Include quoted or faithfully paraphrased text when useful. Never add a locator that is not present in the supplied source.

The Core replaces any supplied confidence value with a deterministic score based on locator specificity. Page + table + column or page + section evidence normally scores higher than unlocated text.

Treat this value as a traceability-specificity score, not as the probability that a statement is true or a study is valid. Structural validation cannot prove that a locator matches source material that was not supplied.

## Causal discipline

Set `finding.causal` to `true` only when both conditions hold:

1. The design is causally eligible, such as DID, IV, RDD, event study, or randomized assignment.
2. The record states an explicit identification strategy and the supplied evidence supports it.

Fixed effects, cross-sectional OLS, correlation, and PSM alone do not automatically authorize causal language. Preserve the paper's stronger wording as a source claim if necessary, but keep the reviewer assessment and validation warning separate.

## Research extensions

Classify each extension with a supported gap type and include an executable element: identification strategy, sample, data source, variable construction, mechanism test, or falsification test. Do not generate a gap from generic novelty language; ground it in the paper's evidence, limitations, or identification boundary.

## Validation resources

- Inspect `schemas/paper.schema.json` through `paperreading schema --kind paper` when exact machine constraints are needed.
- Use the synthetic `examples/paper-record.example.json` as a structure example, never as research evidence.
- Run `paperreading validate <record.json> --strict` when source locators are mandatory.
