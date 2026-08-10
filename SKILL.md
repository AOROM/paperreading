---
name: papers-reading-skill
description: Read and structure finance, economics, management, and social science papers into 13 research-review fields, including feasible follow-up research designs, and safely append the validated row to the user's Excel review workbook. Use when Codex needs to extract bibliographic information, journal ranking, research questions, conclusions, theoretical logic, empirical models, data sources, variables, mechanisms, robustness checks, research extensions, or update the paper-reading workbook. For journal ranking, use Zhejiang University of Finance and Economics levels first and append confirmed labels such as 北核、南核、AMI.
---

# Papers Reading Skill

## Objective

Act as a finance researcher reading academic papers for a structured literature review. Extract 13 fields, preserve the paper's causal logic, distinguish the paper's claims and evidence from your assessment, and append the validated structured row to the review workbook unless the user explicitly requests draft-only output.

Always read `references/reading-fields.md` before producing or writing the structured fields. For the `期刊等级` field, also read `references/zufe-journal-ranking-2020.md`; use `references/zufe-journal-ranking-policy-fulltext.txt` only when a specific journal name must be checked against the Zhejiang University of Finance and Economics directory.

## Reading Workflow

1. Identify bibliographic metadata first: paper title, authors, journal, journal ranking, publication year/month, and keywords.
2. Read in this order when the full paper is available: abstract, introduction, theory/hypotheses, research design, data and variables, baseline results, mechanism tests, heterogeneity tests, robustness/endogeneity sections, conclusion.
3. Write `研究问题` as one to three numbered, concrete questions. Use the exact line pattern `1. ...？`, `2. ...？`, `3. ...？`; prioritize the main effect, mechanism, boundary condition, and economic consequence actually examined by the paper.
4. Write `研究结论` in labeled layers: `【基准结论】`, `【作用机制】`, `【异质性】`, and `【经济后果】`. Include only layers supported by the paper and never invent a missing analysis.
5. Compress `研究逻辑` into a clear causal chain: theory foundation -> core shock or explanatory variable -> mechanism or competing effects -> outcome -> empirical identification -> interpretation. Retain competing theoretical predictions when they are central.
6. Write `实证模型` in labeled blocks: `【基准模型】`, `【内生性】`, `【稳健性】`, and `【拓展检验】`. State the dependent variable, core explanatory variable, model type, fixed effects, controls, and identification strategy in the baseline block; organize the remaining tests under their corresponding labels.
7. Write `数据来源和变量设置` in labeled blocks: `【样本】`, `【数据】`, `【核心变量】`, `【机制变量】`, and `【控制变量】`. Cover sample period and scope, exclusions, databases or source documents, variable construction, and the final data structure.
8. Write `可进一步延伸的研究设计` as two to four numbered, paper-specific and executable designs. Ground each item in a result, limitation, unresolved mechanism, measurement boundary, or external-validity issue. State the extension question and at least one implementable element such as identification strategy, sample/data, variable construction, or test; do not write generic calls for “further research”.
9. Keep every field concise enough for a spreadsheet cell but complete enough to recover the paper's design without reopening the paper.
10. For `期刊等级`, output only confirmed classifications. Put the Zhejiang University of Finance and Economics level first when found, then append confirmed labels such as `北核`、`南核`、`AMI顶级`. Do not write missing-status phrases such as `待核实`, and do not invent unverified rankings.
11. After all 13 fields pass the completeness check, append them to `E:\0论文\01论文研读及指标设计\01论文研读汇总.xlsx` with `scripts/append_paper_reading.py`, unless the user explicitly requests draft-only/no-workbook output. Write Chinese papers to `中文` and English papers to `英文`.

## Required Structured Cell Patterns

Use these patterns when preparing spreadsheet-ready Chinese paper readings:

- `研究问题`: write one question per line with Arabic numbering. Each item must be answerable by the paper's theory or empirical design, for example `1. 数字化转型如何影响企业专业化分工？`.
- `研究结论`: use separate lines beginning with `【基准结论】`、`【作用机制】`、`【异质性】`、`【经济后果】`. Omit an inapplicable layer; if the paper explicitly tests a layer but reports no significant result, report that null result.
- `研究逻辑`: prefer a compact chain such as `交易成本理论 → 数字化降低外部交易成本与内部管控成本 → 两类效应竞争 → 外部交易成本效应占主导 → 企业趋向专业化`. Add the identification step only when needed to make the interpretation credible.
- `实证模型`: use separate lines beginning with `【基准模型】`、`【内生性】`、`【稳健性】`、`【拓展检验】`. If no endogeneity treatment is identified, write `【内生性】当前全文提取未识别到专门的内生性处理。`.
- `数据来源和变量设置`: use separate lines beginning with `【样本】`、`【数据】`、`【核心变量】`、`【机制变量】`、`【控制变量】`. If the paper does not define a separate mechanism variable, state that fact rather than inventing one.
- `可进一步延伸的研究设计`: write two to four numbered items, one per line. Prefer compact forms such as `1. 【识别强化】利用……构造……，检验……。`, `2. 【机制拓展】结合……数据，识别……渠道。`, `3. 【外部效度】将样本拓展至……并比较……。`; include only feasible directions supported by the paper.

Keep the labels, numbering, Chinese punctuation, and line breaks inside each Excel cell. Do not collapse these structured blocks into one undifferentiated paragraph.

## Quality Standards

- Use Chinese academic style unless the user requests otherwise.
- Prefer precise disciplinary terms: mechanism, channel, heterogeneity, endogeneity, identification, fixed effects, instrumental variables, mediation effect, moderating effect, economic consequence.
- Do not invent journal level, data source, variables, model names, or robustness tests. For `期刊等级`, omit unconfirmed ranking labels instead of writing `待核实`; for other critical paper fields, mark missing information as "文中未明确" or ask for the relevant page.
- Do not treat correlation as causality unless the paper's identification design supports causal language.
- Preserve competing theoretical predictions when the paper compares opposite mechanisms, such as external transaction costs versus internal management costs.
- Report variable abbreviations together with their meaning when the paper uses abbreviations, for example "企业数字化程度（Digital）".
- For empirical papers, always check whether the paper addresses endogeneity; if not, state that the current extraction did not identify an endogeneity treatment.

## Output Format

Use this exact 13-field order for review output and workbook insertion:

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

For spreadsheet-ready output, use a Markdown table or CSV-compatible rows only when requested. Otherwise, use labeled fields so the user can review content before insertion.

## Workbook Write Workflow

1. Build a UTF-8 JSON object with fields 2—13 using the exact Chinese keys above; do not supply a manual sequence number.
2. Run `scripts/append_paper_reading.py --data-json <json-path> --sheet 中文` for Chinese papers or replace the sheet with `英文`. Omit `--workbook` to use the default workbook; pass it only when the user specifies another workbook.
3. Let the script add the 13th column `可进一步延伸的研究设计` to column M when the workbook still has the original 12-column schema. It must append the column at the right, copy column L's header/body formatting and width, extend filters/tables, and add the M-column input prompt without moving or rewriting columns A:L.
4. Treat `duplicate_skipped` as a successful no-op. Report the existing row and do not overwrite it.
5. Treat any header mismatch, workbook lock, validation failure, or write error as a hard stop. Keep the original workbook untouched and report the cause.
6. After success, report the worksheet and appended row. The script creates a timestamped backup, saves to a temporary file, reopens it for validation, and then replaces the workbook atomically.

## Review Heuristics

For finance and economics papers, prioritize these checks:

- Theory fit: identify whether the paper relies on agency theory, information asymmetry, transaction cost theory, resource allocation, market competition, financing constraints, corporate governance, or institutional theory.
- Identification credibility: check whether the paper uses fixed effects, instrumental variables, DID, PSM, RD, event study, placebo tests, alternative measures, or sample adjustments.
- Variable construction: record whether core variables come from financial databases, annual report text analysis, policy text, regional statistics, manual coding, survey data, or third-party indices.
- Contribution: infer contribution only after extracting question, mechanism, and identification; avoid generic statements such as "丰富了相关研究" unless the user asks for literature-review positioning.
- Limits: note sample scope, measurement limits, omitted mechanisms, and external validity only if the user asks for critique or paper evaluation.
