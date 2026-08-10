# Paper Reading Field Schema

Use this schema when summarizing papers for a workbook explicitly specified by the user or configured through `PAPER_READING_WORKBOOK`.

## Fields

1. `序号`
   - Use the workbook row number logic when inserting into Excel.
   - If only drafting content, leave blank or use the next known sequence number.

2. `论文名称`
   - Use the exact Chinese or English paper title.
   - Do not translate the title unless the user requests translation.

3. `作者`
   - List authors in paper order.
   - Use Chinese punctuation for Chinese output, for example `作者A, 作者B, 作者C`.

4. `期刊`
   - Use the official journal name.
   - Keep book-title brackets if the user's style uses them, for example `《中国工业经济》`.

5. `期刊等级`
   - Record only classifications confirmed by a reliable source or supplied source material.
   - Preserve each source system's exact label and relevant version; do not infer or translate classifications between systems.
   - Use the compact format `北核，南核，AMI顶级`.
   - If only one classification is confirmed, record only that label.
   - If a ranking or label is not confirmed, omit it. Do not write `待核实`, `未知`, `未检索到`, or similar missing-status text in this field.

6. `发表时间`
   - Use year-month when available, matching the workbook style such as `202109`.
   - Use year only if month is unavailable.

7. `关键词`
   - Extract 4 to 8 terms.
   - Include the topic, core explanatory variable, outcome variable, mechanism, and theory when applicable.

8. `研究问题`
   - Write one to three concrete questions, one per line, using Arabic numbering: `1. ...？`, `2. ...？`, `3. ...？`.
   - Phrase each item as a specific question answerable by the paper; avoid broad topic statements.
   - Cover the main effect, mechanism, boundary condition, and economic consequence only when they are actually central to the paper.

9. `研究结论`
   - Organize findings as separate labeled lines: `【基准结论】`、`【作用机制】`、`【异质性】`、`【经济后果】`.
   - Include only layers that the paper analyzes. Report an explicitly tested null result, but do not invent a missing mechanism, heterogeneity analysis, or economic consequence.
   - Avoid copying the abstract mechanically; integrate results from the empirical sections.

10. `研究逻辑`
    - Compress the argument into a clear causal chain.
    - Recommended structure: theory basis -> core shock or explanatory variable -> mechanism or competing effects -> outcome -> empirical identification -> interpretation.
    - Include the core theoretical tension if the paper has one.
    - Prefer concise arrow-connected clauses or one compact paragraph; avoid repeating the conclusion or listing every hypothesis separately.

11. `实证模型`
    - Organize the content as separate labeled lines: `【基准模型】`、`【内生性】`、`【稳健性】`、`【拓展检验】`.
    - Under `【基准模型】`, specify the dependent variable, core explanatory variable, controls, fixed effects, model type, and identification strategy.
    - Under the remaining labels, report instrumental variables, DID or other endogeneity treatment; variable/sample/model robustness checks; and mechanism, heterogeneity, mediation, moderation, or economic-consequence tests when used.
    - If no endogeneity treatment is identified, write `【内生性】当前全文提取未识别到专门的内生性处理。`.

12. `数据来源和变量设置`
    - Organize the content as separate labeled lines: `【样本】`、`【数据】`、`【核心变量】`、`【机制变量】`、`【控制变量】`.
    - Under `【样本】`, record the period, scope, sample type, exclusions, and final panel or cross-sectional structure.
    - Under `【数据】`, record databases, annual reports, policy texts, regional statistics, surveys, manual coding, and data matching when applicable.
    - Under `【核心变量】`, define dependent, independent, and principal outcome variables with abbreviations and construction methods.
    - Under `【机制变量】`, define mechanism, mediating, or moderating variables; if none are set, state that the paper does not define a separate mechanism variable.
    - Under `【控制变量】`, group the main firm, individual, industry, regional, or macro controls without inventing unreported variables.

13. `可进一步延伸的研究设计`
    - Write two to four concrete, paper-specific designs, one per line, with Arabic numbering.
    - Ground every item in the paper's findings, limitations, unresolved mechanisms, measurement boundaries, identification weaknesses, or external-validity questions.
    - Each item must contain an implementable element: identification strategy, treatment or comparison group, sample/data source, variable construction, mechanism test, outcome, or falsification test.
    - Optional labels include `【识别强化】`、`【机制拓展】`、`【数据拓展】`、`【外部效度】`、`【经济后果】` and `【政策评估】`; use only labels relevant to the paper.
    - Do not write generic suggestions such as “扩大样本”“进一步研究其他机制” without explaining how to execute them.

## Style Target

The example row in the workbook uses dense but readable Chinese academic prose. Match that style:

- `研究问题`: numbered, concrete questions with one item per line.
- `研究结论`: layered lines for baseline conclusion, mechanism, heterogeneity, and economic consequence.
- `研究逻辑`: a compressed causal chain focused on theory, mechanism, competing effects, and identification.
- `实证模型`: layered lines for baseline model, endogeneity, robustness, and extended tests.
- `数据来源和变量设置`: layered lines for sample, data, core variables, mechanism variables, and controls.
- `可进一步延伸的研究设计`: two to four numbered and executable extensions linked directly to the paper's evidence or limitations.
- `期刊等级`: compact ranking string such as `北核，南核，AMI顶级`; include only confirmed rankings and labels.

## Existing Workbook Append Rules

When writing into an existing workbook such as `01论文研读汇总.xlsx`:

1. Load and inspect the workbook before writing. Never clear, reorder, rewrite, or restyle existing rows, sheets, formulas, tables, filters, frozen panes, validations, or column widths.
2. Match the exact 13-column order in this schema. Write Chinese papers to the existing `中文` worksheet and English papers to `英文` unless the user specifies otherwise.
3. If the workbook still has the original 12 headers in A:L and M is blank, append `可进一步延伸的研究设计` as M1 on both `中文` and `英文`. Copy L1's formatting to M1, copy the L-column body style to existing M cells, copy L's width, extend the filter/table range from L to M, and add the M2:M1000 input prompt. Do not insert a column or move A:L. If A:L differs from the expected schema or M contains a different header, stop without writing.
4. Determine the append row from the last genuinely populated paper-title cell, not merely `worksheet.max_row`, because a workbook may contain formatted blank template rows.
5. Before insertion, scan existing rows for duplicates using normalized paper title plus journal, with author and publication time as secondary checks. If a match exists, do not append or overwrite it.
6. Copy cell styles, alignment, borders, fills, fonts, number formats, and row-height behavior from the latest populated data row. Preserve in-cell line breaks and `wrap_text`.
7. Preserve the workbook's sequence formula pattern. If column A uses `=ROW()-1`, use the corresponding formula in the new row rather than replacing earlier sequence values.
8. Expand the existing Excel table and filter range to include only the appended rows; do not rename the table or add tracking columns outside the 13-field schema.
9. Save to a temporary file, reopen it for structural and value validation, create a timestamped backup of the original, and then replace the target atomically. If validation fails or the workbook is locked, leave the original untouched.
10. When the workbook's populated example rows use a different punctuation or date-granularity convention from the generic examples in this schema, follow the workbook's established convention. For example, preserve `北核、南核、AMI顶级` and year-only publication cells when those are the prevailing styles, while retaining the precise publication date in the automation database.
11. Use `scripts/append_paper_reading.py` for deterministic insertion. Pass `--workbook <path>` or set `PAPER_READING_WORKBOOK`; the script never assumes a personal filesystem path. It upgrades the 12-column schema safely, checks duplicates, preserves formatting, creates a backup, validates the temporary workbook, and replaces the source atomically.

## Minimum Completeness Check

Before finalizing a row, verify that the summary answers:

- What is the paper asking?
- What is the main conclusion?
- Why should the relationship exist theoretically?
- How is the relationship tested empirically?
- What data and variables support the test?
- What identification or robustness evidence makes the result credible?
- Which two to four feasible research designs can extend, challenge, or generalize the paper?
