## Problem

Describe the problem or limitation.

## Changes

Describe the Core schema, validation, projection, exporter, Skill, or documentation changes. State any migration impact.

## Validation

- [ ] `python -m ruff check .` and `python -m ruff format --check .`
- [ ] `python -m mypy`
- [ ] `python tools/export_schemas.py --check`
- [ ] `python tools/validate_skill.py skills/papers-reading-skill`
- [ ] `python -m unittest discover -s tests -v`
- [ ] Legacy Excel behavior remains compatible or the migration is documented
- [ ] No confidential papers, workbooks, credentials, or personal paths are included
- [ ] External reference changes identify their source and policy version
