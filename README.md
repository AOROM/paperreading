# Paper Reading Skill

**English** | [简体中文](README.zh-CN.md)

[![CI](https://github.com/AOROM/paperreading/actions/workflows/ci.yml/badge.svg)](https://github.com/AOROM/paperreading/actions/workflows/ci.yml)

An installable Codex skill for reading finance, economics, management, and social-science papers. It converts each paper into 13 auditable fields, separates the paper's claims, empirical evidence, and the reviewer's assessment, proposes executable follow-up research designs, and can safely append the results to an existing Excel literature-review workbook.

## Core capabilities

- Extract the title, authors, journal, ranking, publication date, keywords, research questions, findings, research logic, empirical models, data and variables, and extension designs in a fixed order.
- Organize baseline results, mechanisms, heterogeneity, economic consequences, endogeneity treatment, and robustness checks into distinct layers.
- Avoid presenting correlation as causation or inventing missing variables, models, data sources, or journal rankings.
- Safely add the thirteenth field to a compatible 12-column workbook while preserving existing content, styles, formulas, filters, and table structure.
- Detect duplicates before writing, validate a temporary save, create a backup, and atomically replace the original workbook.

## Project structure

```text
paperreading/
├── skills/papers-reading-skill/   # Installable skill
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   └── scripts/append_paper_reading.py
├── examples/                      # Example input
├── tests/                         # End-to-end and structural tests
├── tools/                         # Repository-level validation tools
└── .github/workflows/ci.yml       # Automated validation
```

Repository-level documentation, tests, and CI configuration are not loaded into the skill's runtime context. Install only `skills/papers-reading-skill/`.

## Installation

1. Clone the repository and install the script dependencies:

   ```bash
   git clone https://github.com/AOROM/paperreading.git
   cd paperreading
   python -m pip install -r requirements.txt
   ```

2. Copy the skill directory into your Codex skills directory. Windows PowerShell example:

   ```powershell
   Copy-Item -Recurse -Force `
     .\skills\papers-reading-skill `
     "$env:USERPROFILE\.codex\skills\papers-reading-skill"
   ```

3. Start a new Codex session. Invoke the skill explicitly with `$papers-reading-skill`, or use a natural-language request about paper reading, 13-field extraction, or literature-review workbook updates.

## Workbook configuration

The public repository contains no personal workbook paths. The write script resolves its target in this order:

1. The command-line option `--workbook <path>`;
2. The `PAPER_READING_WORKBOOK` environment variable;
3. If neither is provided, stop without writing.

PowerShell:

```powershell
$env:PAPER_READING_WORKBOOK = "D:\research\paper-reading.xlsx"
```

Bash:

```bash
export PAPER_READING_WORKBOOK="/data/research/paper-reading.xlsx"
```

## Usage

Generate a draft without writing to a workbook:

```text
Use $papers-reading-skill to read this paper and produce the 13 structured fields, but do not write to a workbook.
```

Append a validated result to the configured workbook:

```text
Use $papers-reading-skill to read this paper; after validating all fields, append it to the Chinese worksheet.
```

Call the deterministic write script directly:

```bash
python skills/papers-reading-skill/scripts/append_paper_reading.py \
  --workbook "/path/to/paper-reading.xlsx" \
  --sheet 中文 \
  --data-json examples/paper-reading.example.json
```

Use `--sheet 中文` for a Chinese paper or `--sheet 英文` for an English paper. The script returns a JSON status such as `paper_appended`, `duplicate_skipped`, `schema_updated`, or `error`. If validation fails, the original workbook remains unchanged.

## Field and journal-ranking boundaries

See [`reading-fields.md`](skills/papers-reading-skill/references/reading-fields.md) for the field definitions. Record only journal-ranking labels confirmed by a reliable source, preserve the source system's original wording, and do not infer or translate classifications across ranking systems. For evaluation, promotion, research reporting, or submission decisions, verify the applicable system, version, and effective date.

## Development and validation

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_skill.py skills/papers-reading-skill
python -m unittest discover -s tests -v
```

GitHub Actions validates the skill metadata on every push and pull request and runs end-to-end tests for workbook updates, duplicate detection, environment-variable configuration, and failure-safe source preservation.

See [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a change.

## License

This repository currently has no open-source license. Public visibility does not automatically grant permission to copy, modify, or distribute its contents.
