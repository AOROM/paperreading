# PaperReading

[English](README.md) | **简体中文**

[![CI](https://github.com/AOROM/paperreading/actions/workflows/ci.yml/badge.svg)](https://github.com/AOROM/paperreading/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **把论文变成可检验、可比较、可延伸的研究知识。**

PaperReading 是面向**金融、经济、管理、会计与实证社会科学**的 evidence-grounded AI 论文研读工作流。它不止回答“论文讲了什么”，而是围绕研究问题、理论逻辑、识别策略、变量、证据、作用机制、稳健性、研究局限与可执行延伸设计建立结构化记录。

项目保留现有可安装的 Codex Skill 和安全 Excel 写入能力，同时开始抽离可复用的 Python 核心，用于可审计 Paper Record、Evidence Map、跨论文比较与后续文献综合。

## 为什么是 PaperReading？

多数论文阅读工具优化的是“总结内容”；PaperReading 更关注“为什么这个结论可信，以及下一步还能如何研究”。

```text
论文 / PDF
    │
    ├── Structured Reading ── 13 字段研读体系
    ├── Evidence Map ──────── 页码 / 章节 / 表格 / 图形证据定位
    ├── Method Audit ──────── 识别 / 内生性 / 稳健性
    ├── Literature Matrix ─── 多论文横向比较
    └── Research Extensions ─ 可执行延伸研究设计
                │
                └── Excel / JSON / Markdown / 后续集成
```

## 当前能力

### 1. Evidence-grounded 13 字段论文研读

现有 Codex Skill 可以按固定结构整理题名、作者、期刊、等级、时间、关键词、研究问题、研究结论、研究逻辑、实证模型、数据与变量以及延伸研究设计。

它会明确区分基准结果、作用机制、异质性、经济后果、内生性处理与稳健性检验，并避免补造缺失变量、模型、期刊等级或不受识别策略支持的因果表述。

### 2. 可审计 Paper Record

新增 `paperreading` Python 包，为论文元数据、实证设计、研究结论与证据定位提供可复用的数据模型。

```python
from paperreading import EvidenceRef, Finding, PaperRecord

paper = PaperRecord(
    title="示例论文",
    research_questions=["X 是否影响 Y？"],
    findings=[
        Finding(
            text="X 与 Y 显著正相关。",
            category="baseline",
            evidence=[EvidenceRef(page=12, table="表3", section="4.2")],
        )
    ],
)
```

### 3. Literature Matrix

多个 `PaperRecord` 可以直接生成跨论文比较矩阵，不依赖 pandas：

```python
from paperreading import build_literature_matrix, matrix_to_markdown

rows = build_literature_matrix([paper_a, paper_b])
print(matrix_to_markdown(rows))
```

矩阵会展示论文、期刊、研究问题、识别策略、核心 X/Y、作用机制、主要结论以及证据覆盖率。

### 4. 安全 Excel 文献研读工作流

原有确定性写入脚本继续保留：在已有工作簿中追加 13 字段记录，同时保留原始值、公式、样式、筛选、Excel Table 与工作簿结构；写入前查重，临时保存后重新验证，创建备份，再原子替换源文件。

## 项目结构

```text
paperreading/
├── paperreading/                   # 可复用 Research Intelligence 核心
│   ├── models.py                   # Paper / Method / Finding / Evidence 模型
│   ├── evidence.py                 # Evidence 标签与覆盖率
│   └── matrix.py                   # 跨论文 Literature Matrix
├── schemas/paper.schema.json       # Paper Record 可移植契约
├── skills/papers-reading-skill/    # 可安装 Codex Skill
├── examples/                       # 结构化示例
├── docs/                           # 架构与方法文档
├── tests/                          # Core + Excel 测试
├── ROADMAP.md
├── CHANGELOG.md
└── CITATION.cff
```

## 快速开始

### 使用 Codex Skill

```bash
git clone https://github.com/AOROM/paperreading.git
cd paperreading
python -m pip install -r requirements.txt
```

将 `skills/papers-reading-skill/` 复制到 Codex skills 目录，重新打开 Codex 会话，然后调用 `$papers-reading-skill`，或直接用自然语言要求进行结构化论文研读。

### 使用 Python Core

当前核心只依赖 Python 标准库：

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

可移植 JSON 示例见 [`examples/paper-record.example.json`](examples/paper-record.example.json)。

## 设计原则

- **Evidence before fluency**：重要结论优先保证可回查，而不是只追求流畅表述。
- **因果纪律**：没有足够识别设计时，不把相关关系写成因果关系。
- **结构化但可移植**：Excel 是导出目标，不再作为唯一底层数据模型。
- **研究导向延伸**：研究建议应尽量包含可实施的识别策略、样本、变量构造、机制检验、结果变量或证伪设计。
- **不静默补造**：未知的元数据、等级、方法或证据保持未知。

## Roadmap

下一阶段见 [`ROADMAP.md`](ROADMAP.md)：

- 自动 Evidence 抽取与 Evidence Map；
- Batch Paper Reading 与更丰富的 Literature Matrix；
- 跨论文 Research Gap 综合；
- Markdown / BibTeX / Zotero 导出；
- Benchmark 与幻觉率、证据准确率指标；
- 可选 CLI、Agent Adapter 与 Web Demo。

## 开发与验证

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_skill.py skills/papers-reading-skill
python -m unittest discover -s tests -v
```

提交前请阅读[中文贡献指南](CONTRIBUTING.zh-CN.md)。功能建议可通过 GitHub Issue Template 提交。

## 引用

如果 PaperReading 对你的研究工作有帮助，可使用 [`CITATION.cff`](CITATION.cff) 中的引用信息。

## 许可

MIT License，见 [LICENSE](LICENSE)。
