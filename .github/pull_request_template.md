## Problem

Describe the problem or limitation.

## Changes

Describe the Core schema, validation, projection, exporter, Skill, or documentation changes. State any migration impact.

## Research integrity impact

List the affected [Research Principles](https://github.com/AOROM/paperreading/blob/main/RESEARCH_PRINCIPLES.md) (P1–P12). Explain the evidence boundary, inference limit, uncertainty representation, failure behavior, and any residual trade-off.

## Validation

- [ ] `python -m ruff check .` and `python -m ruff format --check .`
- [ ] `python -m mypy`
- [ ] `python tools/export_schemas.py --check`
- [ ] `python tools/generate_examples.py --check`
- [ ] `python tools/validate_skill.py skills/papers-reading-skill`
- [ ] `python -m unittest discover -s tests -v`
- [ ] v0.3 evidence IDs, verification state, and analysis boundaries remain valid
- [ ] Affected Research Principles and residual limitations are documented
- [ ] Legacy Excel behavior remains compatible or the migration is documented
- [ ] No confidential papers, workbooks, credentials, or personal paths are included
- [ ] External reference changes identify their source and policy version
