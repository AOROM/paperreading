# PaperReading

**English** | [简体中文](README.zh-CN.md)

[![CI](https://github.com/AOROM/paperreading/actions/workflows/ci.yml/badge.svg)](https://github.com/AOROM/paperreading/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Turn papers into research intelligence.**

PaperReading is an evidence-grounded AI research workflow for **finance, economics, management, accounting, and empirical social science**. Instead of stopping at a generic summary, it structures papers around research questions, theory, identification, variables, evidence, mechanisms, robustness, limitations, and executable follow-up designs.

The repository keeps the existing installable Codex skill and safe Excel workflow, while evolving toward a reusable Python core for auditable paper records, evidence maps, cross-paper comparison, and literature synthesis.

## Why PaperReading?

Most paper-reading tools optimize for *what a paper says*. PaperReading is designed around *why a result should be believed and how it can be extended*.

```text
Paper / PDF
    │
    ├── Structured Reading ── 13-field review schema
    ├── Evidence Map ──────── page / section / table / figure anchors
    ├── Method Audit ──────── identification / endogeneity / robustness
    ├── Literature Matrix ─── cross-paper comparison
    └── Research Extensions ─ executable follow-up designs
                │
                └── Excel / JSON / Markdown / future integrations
```

## Current capabilities

### 1. Evidence-grounded 13-field reading

The existing Codex skill extracts bibliographic metadata, research questions, findings, research logic, empirical models, data and variables, and follow-up research designs in a fixed auditable structure.

It explicitly separates baseline findings, mechanisms, heterogeneity, economic consequences, endogeneity treatment, and robustness checks, and avoids inventing missing variables, models, rankings, or causal claims.

### 2. Auditable paper records

The new `paperreading` Python package provides a reusable data model for paper metadata, empirical design, findings, and evidence anchors.

```python
from paperreading import EvidenceRef, Finding, PaperRecord

paper = PaperRecord(
    title="Example paper",
    research_questions=["Does X affect Y?"],
    findings=[
        Finding(
            text="X is positively associated with Y.",
            category="baseline",
            evidence=[EvidenceRef(page=12, table="Table 3", section="4.2")],
        )
    ],
)
```

### 3. Literature Matrix

Multiple `PaperRecord` objects can be converted into a compact comparison matrix without requiring pandas:

```python
from paperreading import build_literature_matrix, matrix_to_markdown

rows = build_literature_matrix([paper_a, paper_b])
print(matrix_to_markdown(rows))
```

The matrix exposes title, journal, research question, identification strategy, key X/Y variables, mechanisms, main finding, and evidence coverage.

### 4. Safe Excel literature-review workflow

The existing deterministic writer can append validated 13-field results to an existing workbook while preserving values, formulas, formatting, filters, tables, and workbook structure. It detects duplicates, validates a temporary save, creates a backup, and atomically replaces the source file.

## Project structure

```text
paperreading/
├── paperreading/                   # Reusable research-intelligence core
│   ├── models.py                   # Paper, method, finding, evidence models
│   ├── evidence.py                 # Evidence labels and coverage metrics
│   └── matrix.py                   # Cross-paper literature matrix
├── schemas/paper.schema.json       # Portable paper-record contract
├── skills/papers-reading-skill/    # Installable Codex skill
├── examples/                       # Structured examples
├── docs/                           # Architecture and methodology
├── tests/                          # Core + workbook tests
├── ROADMAP.md
├── CHANGELOG.md
└── CITATION.cff
```

## Quick start

### Use the Codex skill

```bash
git clone https://github.com/AOROM/paperreading.git
cd paperreading
python -m pip install -r requirements.txt
```

Copy `skills/papers-reading-skill/` into your Codex skills directory, start a new Codex session, then invoke `$papers-reading-skill` or ask naturally for a structured paper review.

### Use the Python core

The current core uses only the Python standard library:

```python
from paperreading import PaperRecord, EmpiricalDesign

paper = PaperRecord(
    title="Digital finance and firm innovation",
    authors=["Author A", "Author B"],
    research_questions=["Does digital finance affect firm innovation?"],
    empirical_design=EmpiricalDesign(
        explanatory_variables=["Digital finance"],
        outcome_variables=["Innovation"],
        fixed_effects=["Firm", "Year"],
        identification="Two-way fixed effects",
    ),
)

paper.validate()
```

See [`examples/paper-record.example.json`](examples/paper-record.example.json) for the portable JSON representation.

## Design principles

- **Evidence before fluency:** important claims should be traceable to the source.
- **Causal discipline:** correlation is not described as causality without an identification design that supports it.
- **Structured but portable:** Excel is an export target, not the canonical data model.
- **Research-oriented extensions:** follow-up ideas should specify an implementable identification strategy, sample, variable construction, mechanism test, outcome, or falsification test.
- **No silent invention:** unknown metadata, rankings, methods, or evidence remain unknown.

## Roadmap

The next milestones are tracked in [`ROADMAP.md`](ROADMAP.md):

- evidence extraction and evidence-map rendering;
- batch paper ingestion and richer literature matrices;
- research-gap synthesis across papers;
- Markdown / BibTeX / Zotero exporters;
- benchmark datasets and hallucination/evidence metrics;
- optional CLI, agent adapters, and web demo.

## Development

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_skill.py skills/papers-reading-skill
python -m unittest discover -s tests -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a change. Feature proposals are welcome through the GitHub issue templates.

## Citation

If PaperReading supports your research workflow, see [`CITATION.cff`](CITATION.cff) for citation metadata.

## License

MIT License. See [LICENSE](LICENSE).
