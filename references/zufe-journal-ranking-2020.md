# Zhejiang University of Finance and Economics Journal Ranking Rules

Use this reference when filling the `期刊等级` field in the paper reading table.

## Source

Primary source: `关于印发《浙江财经大学中外文学术期刊定级管理办法（2020年修订）》的通知.doc`.

Extracted full text for lookup: `zufe-journal-ranking-policy-fulltext.txt`.

## Output Rule

Write only confirmed classifications. Do not write missing-status text.

Preferred format:

```text
浙江财经大学等级；外部标签
```

Examples:

```text
一级B；北核，南核，AMI顶级
一级B；北核
北核，南核
一级B
```

If nothing is confirmed, leave the field blank.

Do not write:

```text
待核实
浙财大：一级B；北核：是；南核：是
一级B；北核待核实
```

## Ranking Priority

1. Check the Zhejiang University of Finance and Economics ranking first.
2. For Chinese journals, exact listed rankings take priority: `TOP`、`一级A`、`一级B`.
3. If not listed in TOP/一级A/一级B, apply the rule-based categories:
   - CSSCI source journals, excluding CSSCI expanded edition: `二级A`; external label may include `南核`.
   - CSCD core journals, excluding expanded edition: `二级A`.
   - Peking University Chinese Core Journals, if not already 二级A or above: `二级B`; external label may include `北核`.
   - CSSCI expanded edition or CSCD expanded edition: `二级B`; do not label CSSCI expanded edition as `南核`.
   - Other legally published Chinese academic journals outside the above categories: `三级`.
4. For foreign journals, use the policy levels:
   - Listed foreign TOP or 一级A journals: use the listed level.
   - A&HCI indexed foreign journals: `一级A`.
   - CCF recommended international A-class conference papers: `一级A`.
   - SSCI Q1/Q2 or SCI Q1/Q2 journals not listed as TOP/一级A: `一级B`.
   - SSCI Q3/Q4, SCI Q3/Q4, or EI journals not listed above: `二级A`.
   - Other foreign journals and Hong Kong/Macau/Taiwan journals not indexed above: `二级B`.
5. If multiple categories apply, use the highest confirmed Zhejiang University of Finance and Economics level.

## External Labels

Append only labels that are confirmed by the user, the paper context, the provided workbook, the source document, or a reliable lookup source.

Common labels:

- `北核`: Peking University Chinese Core Journals.
- `南核`: CSSCI source journals, excluding CSSCI expanded edition.
- `AMI顶级`, `AMI权威`, `AMI核心`, etc.: use the exact confirmed AMI level.

Do not infer `北核`, `南核`, or AMI labels only from the Zhejiang University of Finance and Economics level. For example, a journal listed as `一级B` may also be 北核/南核, but those labels still need confirmation.

## Lookup Procedure

1. Normalize the journal name by removing book-title brackets such as `《》`, spaces, and punctuation variants.
2. Search `zufe-journal-ranking-policy-fulltext.txt` for the exact journal name.
3. If the journal appears under Chinese `TOP期刊`、`一级A期刊`、`一级B期刊`, use that level.
4. If the exact journal is not listed, apply the rule-based CSSCI/CSCD/北核 categories only when those external inclusions are confirmed.
5. Construct the field with the school level first and external labels after a semicolon.

## Example

For `《中国工业经济》`, the Zhejiang University of Finance and Economics source places it in Chinese `一级B期刊`. If 北核、南核、AMI顶级 are also confirmed, write:

```text
一级B；北核，南核，AMI顶级
```
