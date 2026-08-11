# PaperReading

**Evidence-grounded AI research workflow｜证据约束的 AI 研究工作流**

[English](README.md) | **简体中文**

[![CI](https://github.com/AOROM/paperreading/actions/workflows/ci.yml/badge.svg)](https://github.com/AOROM/paperreading/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![Version](https://img.shields.io/badge/version-0.3.0-4C1)

PaperReading 将研究材料转化为可版本化、可复核的研究资产。它要求陈述与来源位置绑定，分离论文报告事实与研究者分析，检查证据能否在已摄取的文档中被解析，并保留现有 13 字段 Excel 工作流。

> 当前边界：v0.3 支持 UTF-8 文本与 Markdown 摄取、v0.2 记录迁移、稳定 ID 证据规范化，以及正文位置和引文核验。它目前**不支持** PDF 解析、AI Provider 自动调用、批处理、SQLite 文献库搜索、多论文综合或自动研究缺口发现。

## 为什么需要 PaperReading

流畅的摘要不等于可辩护的研究资产。可靠工作流必须保留足够结构，以回答：

- 哪些陈述由论文报告，哪些属于后续解释？
- 哪个页码、章节、文本块、表格、图形、方程或引文支持某项主张？
- 某个来源位置是否真正与所提供的文档核对过？
- 实证设计是否足以支持因果表述？
- 研究资产能否演进，同时不静默破坏旧记录或 Excel 工作流？

PaperReading 将这些问题转化为显式 Schema、校验规则、迁移路径和失败行为。

## 研究宪章

规范性文档[《学术研究底层逻辑》](RESEARCH_PRINCIPLES.zh-CN.md)从学术有效性、可追溯性、可证伪性、可复现性和研究伦理出发，推导项目决策规则。其优先级高于兼容性、便利性、性能和增长指标。无法说明研究对象、证据、推断边界、不确定性和失败行为的能力，不得作为正式功能交付。

## 已实现能力

| 能力 | 状态 | 公开契约 |
|---|---|---|
| v0.3 研究包 | 已实现 | `PaperPackage` 分离文档、来源记录、规范化证据、分析、审计与运行元数据 |
| 来源感知摄取 | 已实现 | 将 UTF-8 `.txt`、`.md`、`.markdown` 确定性解析为 `PaperDocument` 文本块 |
| 证据图 | 已实现 | 研究对象通过稳定 ID 引用去重后的 `EvidenceSpan` 节点 |
| 证据核验 | 已实现 | 核验来源、页码、文本块、章节、引文和文本哈希，并明确返回 `verified`、`partial` 或 `failed` |
| v0.2 迁移 | 已实现 | 确定性地将 `PaperRecord` 迁移为 `PaperPackage`，同时显式保留溯源局限 |
| 分析分离 | 已实现 | 研究者判断和研究拓展位于来源记录之外 |
| 因果语言守卫 | 已实现 | 因果表述要求合格设计和明确识别策略 |
| 导出与兼容 | 已实现 | 无损 JSON、可复核 Markdown、旧版 13 字段投影与安全 Excel 追加 |
| 本地项目存储 | 已实现 | `.paperreading/` 下的原子化、可检查 JSON 文件，无需数据库 |
| PDF / Provider / 批处理 / 搜索 / 综合 / Gap | 规划中 | 按[路线图](ROADMAP.zh-CN.md)排序，绝不描述为已经交付 |

## 架构

```mermaid
flowchart LR
    S["UTF-8 文本或 Markdown"] --> I["确定性摄取"]
    I --> D["PaperDocument"]
    V2["v0.2 PaperRecord"] --> M["确定性迁移"]
    M --> P["v0.3 PaperPackage"]
    D --> V["证据核验器"]
    P --> V
    A["Skill 或提取适配器"] --> P
    V --> O{"已校验研究资产"}
    O --> J["JSON"]
    O --> MD["Markdown"]
    O --> L["旧版 13 字段投影"]
    L --> X["安全 Excel Exporter"]
```

依赖方向是明确的：

```text
domain <- migrations / ingestion / verification / validation / projections
       <- application use cases <- CLI / Skill / exporters / repositories
```

Domain 层不导入 Typer、OpenPyXL、模型 SDK、存储适配器或 Codex Runtime。文件存储和 Excel 都是可替换适配器，Schema 才是系统中心。

## 快速开始

从源码安装：

```bash
git clone https://github.com/AOROM/paperreading.git
cd paperreading
python -m pip install -e ".[excel]"
```

初始化一个可检查的本地项目：

```bash
paperreading init
```

该命令会创建 `.paperreading/config.toml`、清单文件，以及彼此独立的 documents、drafts、records、analyses、audits 和 cache 目录。

摄取合成 Markdown 来源：

```bash
paperreading ingest examples/source.example.md
```

在不修改项目的情况下迁移合成 v0.2 记录：

```bash
paperreading migrate examples/paper-record.example.json \
  --output paper-package.json
```

校验并导出任一版本：

```bash
paperreading validate examples/paper-record.example.json
paperreading validate examples/paper-package.example.json
paperreading export examples/paper-package.example.json review.md --format markdown
paperreading project examples/paper-package.example.json
```

核验证据 ID 已引用某个摄取文档的研究包：

```bash
paperreading verify package.json \
  --document .paperreading/documents/<document-id>.json \
  --strict \
  --output verified-package.json
```

在 v0.3 中，Skill 或其他提取适配器负责构造与来源关联的研究包。PaperReading 本身还不会从任意文本自动推断完整研究记录。

## v0.3 研究资产模型

```text
PaperPackage
├── document: DocumentManifest
├── record: GroundedPaperRecord
│   ├── metadata / questions / theory / data / variables / design
│   ├── source_claims -> evidence_ids[]
│   ├── findings / mechanisms / heterogeneity / robustness -> evidence_ids[]
│   └── 论文报告的局限
├── evidence_index: {evidence_id -> EvidenceSpan}
├── analysis
│   ├── 研究者或 AI 辅助判断
│   └── 可执行研究拓展
├── audit: 可选的方法审计报告
└── run: 可复现性元数据
```

`GroundedPaperRecord` 只包含来源派生信息；`ResearchAnalysis` 包含解释和拟议拓展。二者分离可以防止生成的研究想法被误认为论文发现。

EvidenceSpan 可以同时记录逻辑位置与物理位置：

```json
{
  "evidence_id": "ev-0123456789abcdef",
  "source_id": "src-0123456789abcdef",
  "type": "TEXT",
  "page": 1,
  "section_path": ["Results"],
  "block_id": "p1-b0007",
  "char_start": 420,
  "char_end": 581,
  "quoted_text": "A source quotation used for verification."
}
```

可追溯性分数衡量来源位置的具体程度。它**不是**真实性概率、研究质量分数、因果有效性分数或外部效度判断。证据核验只能确认来源位置和引文能否在给定 `PaperDocument` 中解析，仍不能证明论文方法或主张本身正确。

## Schema 与兼容性

根目录 Schema 名称继续作为便捷稳定别名；不可变的版本化契约位于 [`schemas/v0.2`](schemas/v0.2) 与 [`schemas/v0.3`](schemas/v0.3)。

| 输入 | 校验 | JSON / Markdown | 旧版投影 | 安全 Excel |
|---|---:|---:|---:|---:|
| v0.2 `PaperRecord` | 是 | 是 | 是 | 是 |
| v0.3 `PaperPackage` | 是 | 是 | 是，前提是存在研究拓展 | 是，通过同一投影层 |

迁移会完整保持 v0.2 的 13 字段投影，但不会假装旧版证据已与来源正文核对。迁移包会持续明确标记为 `migrated`，直到完成核验。

## Python API

```python
from datetime import datetime, timezone
from pathlib import Path

from paperreading import (
    PaperRecord,
    migrate_v02_to_v03,
    to_legacy_13_fields,
    validate_package,
)

record = PaperRecord.model_validate_json(
    Path("record.json").read_text(encoding="utf-8")
)
package = migrate_v02_to_v03(
    record,
    migrated_at=datetime.now(timezone.utc),
)
report = validate_package(package)

if report.valid:
    legacy_row = to_legacy_13_fields(package)
```

## 安全 Excel 兼容

```bash
paperreading export package.json literature.xlsx --format excel --sheet 中文
```

工作簿必须已经包含 `中文` 和 `英文` 工作表。Exporter 会：

- 校验 12 列或 13 列表头契约；
- 检测重复记录且不执行覆盖；
- 保留既有数值、公式、样式、表格、筛选和冻结窗格；
- 创建带时间戳的备份；
- 写入临时文件并重新打开校验；
- 只有校验成功后才原子替换源工作簿。

旧版 `skills/papers-reading-skill/scripts/append_paper_reading.py` 入口仍可用于既有 13 字段 JSON 集成。仓库不提交个人工作簿路径；`PAPER_READING_WORKBOOK` 可提供既有本地配置。

## Codex Skill

安装 Core 后，将 [`skills/papers-reading-skill`](skills/papers-reading-skill) 复制到 Codex skills 目录，开启新会话并调用 `$papers-reading-skill`。

Skill 是适配器，而不是第二套实现。它尊重用户提供的来源边界，构造来源约束的研究包或兼容 v0.2 记录，运行 Core 校验，报告不确定性，并在修改工作簿前请求授权。

## 项目结构

```text
paperreading/
├── RESEARCH_PRINCIPLES*.md # 中英文规范性学术研究契约
├── src/paperreading/
│   ├── domain/          # v0.2 与 v0.3 严格模型
│   ├── ingestion/       # 确定性文本 / Markdown 解析器
│   ├── migrations/      # 版本间转换
│   ├── verification/    # 来源正文证据检查
│   ├── validation/      # 证据状态与因果语言规则
│   ├── application/     # 可复用用例
│   ├── repositories/    # 本地原子 JSON 适配器
│   ├── projections/     # 旧版 13 字段投影
│   └── exporters/       # JSON、Markdown 与 Excel 适配器
├── schemas/             # 根别名与版本化 JSON Schema
├── skills/              # Codex 适配器
├── examples/            # 合成、不可引用的示例
├── tests/               # Domain、CLI、迁移、核验与 Excel 安全测试
└── tools/               # 确定性 Schema、示例与 Skill 检查
```

## 开发

```bash
python -m pip install -e ".[excel,dev]"
python -m ruff check .
python -m ruff format --check .
python -m mypy
python tools/export_schemas.py --check
python tools/generate_examples.py --check
python tools/validate_skill.py skills/papers-reading-skill
python -m unittest discover -s tests -v
python -m pip wheel --no-deps --wheel-dir dist .
```

架构、Schema 演进、兼容性和数据安全规则见[中文贡献指南](CONTRIBUTING.zh-CN.md)。已交付行为与规划假说的边界见[中文路线图](ROADMAP.zh-CN.md)。安全问题请遵循 [SECURITY.md](SECURITY.md)。

## 许可

本仓库目前未附加开源许可证。公开可见不等于自动授予复制、修改或分发权利。
