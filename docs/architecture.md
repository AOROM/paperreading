# Architecture

## Product boundary

PaperReading separates the **canonical research record** from the **agent that extracts it** and the **destination that stores it**.

```text
                 INPUTS
          PDF / DOI / structured text
                    │
                    ▼
             AGENT ADAPTERS
       Codex skill / future adapters
                    │
                    ▼
              CORE RECORD
        PaperRecord + EvidenceRef
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
     Evidence    Method      Literature
       Map        Audit        Matrix
        │           │           │
        └───────────┼───────────┘
                    ▼
                 EXPORTS
      Excel / JSON / Markdown / future
```

The existing Codex skill is an adapter that produces the 13-field review and can invoke the deterministic Excel writer. The `paperreading` package is deliberately agent-neutral.

## Canonical data model

The canonical representation is `PaperRecord`, mirrored by `schemas/paper.schema.json`.

Core entities:

- `PaperRecord`: metadata, research questions, research logic, mechanisms, limitations, empirical design, findings, and extension ideas.
- `EmpiricalDesign`: X/Y variables, controls, fixed effects, model type, identification strategy, endogeneity treatment, and robustness checks.
- `Finding`: one baseline/mechanism/heterogeneity/economic-consequence result plus its evidence anchors.
- `EvidenceRef`: source location such as page, section, table, figure, and a short non-verbatim note.

Excel's 13 fields remain a supported **view/export contract**, not the only internal representation.

## Evidence model

Evidence is attached at the finding level. A finding can have zero or more `EvidenceRef` objects.

An evidence anchor should prefer structural references over copied prose:

```json
{
  "page": 12,
  "section": "4.2 Baseline results",
  "table": "Table 3",
  "figure": null,
  "note": "Main coefficient reported in column (4)."
}
```

`evidence_coverage()` measures how many findings have at least one source anchor. It is a completeness indicator, not a truth or quality score.

## Literature Matrix

`build_literature_matrix()` intentionally returns plain dictionaries instead of a dataframe. This keeps the core dependency-free and lets callers choose pandas, Excel, HTML, or another presentation layer.

The initial matrix focuses on:

- title and journal;
- first research question;
- identification strategy;
- key explanatory and outcome variables;
- mechanisms;
- main finding;
- evidence coverage.

Future releases can add configurable columns without coupling the canonical model to a specific table library.

## Compatibility strategy

During v0.x:

1. Existing Codex Skill behavior should remain backward compatible unless a change is explicitly documented.
2. Existing workbook-writing safety guarantees must not regress.
3. New core fields should be additive when possible.
4. Breaking JSON-schema changes require a migration note in `CHANGELOG.md`.
5. Agent-specific prompts must not become dependencies of the core Python package.
