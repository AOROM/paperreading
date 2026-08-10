# Contributing

**English** | [简体中文](CONTRIBUTING.zh-CN.md)

Thank you for improving Paper Reading Skill. Follow these conventions before submitting a change.

## Scope of changes

- Keep the instructions, scripts, and references required by Codex at runtime in `skills/papers-reading-skill/`.
- Keep maintainer documentation, tests, examples, and CI configuration at the repository level so they do not increase the skill's runtime context.
- Do not commit full paper texts, data without redistribution permission, personal workbooks, access tokens, personal filesystem paths, or other sensitive information.
- When modifying journal-ranking data, document its source, version, effective boundary, and verification date. Do not present a historical directory as current.

## Documentation translations

- Keep `README.md` and `README.zh-CN.md` semantically aligned.
- Keep `CONTRIBUTING.md` and `CONTRIBUTING.zh-CN.md` semantically aligned.
- Keep commands, paths, identifiers, and behavioral contracts identical across languages; translate explanatory prose only.

## Local checks

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_skill.py skills/papers-reading-skill
python -m unittest discover -s tests -v
```

When adding or changing workbook-write logic, cover at least a successful append, a duplicate no-op, a header mismatch that leaves the source unchanged, and target resolution through either an explicit path or the environment variable.

## Pull requests

State clearly:

1. The problem being solved;
2. Whether any behavior or field contract changes;
3. The validation commands you ran and their results;
4. The source and version of any external material involved.
