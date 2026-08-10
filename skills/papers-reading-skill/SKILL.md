---
name: papers-reading-skill
description: Read finance, economics, management, and social-science papers into 13 evidence-grounded literature-review fields, propose executable follow-up research designs, and optionally append a validated row to an Excel review workbook without damaging existing content. Use when Codex needs to extract bibliographic metadata, journal ranking, research questions, findings, causal logic, empirical models, data, variables, mechanisms, robustness checks, extensions, or update a paper-reading workbook.
---

# Papers Reading Skill

## Core workflow

1. Identify the title, authors, journal, publication date, and keywords.
2. Read the abstract and introduction, then theory or hypotheses, research design, data and variables, baseline results, mechanism and heterogeneity tests, robustness or endogeneity checks, and conclusion.
3. Separate the paper's stated claims, reported evidence, and your assessment. Never fill a gap with an invented model, variable, test, source, or ranking.
4. Build the 13 fields in the exact order defined in `references/reading-fields.md`.
5. Check completeness and causal-language discipline before offering to write the row.
6. Append only after the fields are validated and a workbook path is available. Produce draft-only output when the user requests it.

## Required references

- Read `references/reading-fields.md` before producing structured fields or writing a workbook row.
- Read `references/zufe-journal-ranking-2020.md` before assigning `期刊等级`.
- Treat `references/zufe-journal-ranking-policy-fulltext.txt` as a historical 2020-policy lookup corpus. Run `scripts/lookup_zufe_ranking.py --journal "<期刊名称>"` for an exact listed-journal lookup. If needed, inspect a targeted literal-text match and its nearby `TOP期刊`、`一级A期刊` or `一级B期刊` heading; do not load all 4,000+ lines.
- For a current classification, verify the latest official policy version instead of assuming that the bundled 2020 directory is still current. Record only a confirmed classification.

## Evidence rules

- Use Chinese academic style unless the user requests another language.
- Phrase `研究问题` as one to three concrete, answerable questions.
- Organize `研究结论`, `实证模型`, and `数据来源和变量设置` with the labeled blocks required by `references/reading-fields.md`.
- Express `研究逻辑` as theory -> explanatory variable or shock -> mechanism or competing effects -> outcome -> identification -> interpretation.
- Do not describe correlation as causality unless the identification design supports causal language.
- Report variable abbreviations with their meanings and preserve explicitly reported null results.
- Propose two to four paper-specific extensions. Give each an implementable identification strategy, sample or data source, variable construction, mechanism test, outcome, or falsification test.
- For `期刊等级`, place a confirmed Zhejiang University of Finance and Economics level first, then append independently confirmed labels such as `北核`、`南核` or an AMI level. Omit unconfirmed labels and missing-status placeholders.

## Output contract

Use this exact order:

1. 序号
2. 论文名称
3. 作者
4. 期刊
5. 期刊等级
6. 发表时间
7. 关键词
8. 研究问题
9. 研究结论
10. 研究逻辑
11. 实证模型
12. 数据来源和变量设置
13. 可进一步延伸的研究设计

Use labeled fields for review by default. Use a Markdown table or CSV-compatible row only when requested.

## Workbook writing

1. Resolve the workbook in this order: an explicit user-provided path, then the `PAPER_READING_WORKBOOK` environment variable. If neither is available, return a draft and ask for a path before writing.
2. Build a UTF-8 JSON object with fields 2-13 using the exact Chinese keys; do not provide a manual sequence number.
3. Run `scripts/append_paper_reading.py --workbook <path> --data-json <json-path> --sheet 中文` for a Chinese paper, or use `--sheet 英文` for an English paper. When the environment variable is configured, `--workbook` may be omitted.
4. Treat `duplicate_skipped` as a successful no-op. Report the existing worksheet row and do not overwrite it.
5. Treat a header mismatch, locked workbook, validation failure, or write error as a hard stop. Leave the original workbook untouched and report the cause.
6. After success, report the worksheet, appended row, and timestamped backup path returned by the script.

The script may add the thirteenth field to a compatible 12-column workbook, preserve existing values and formatting, extend tables and filters, create a backup, validate a temporary save, and replace the workbook atomically. Do not bypass the script for routine insertion.
