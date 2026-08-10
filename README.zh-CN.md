# Paper Reading Skill

[English](README.md) | **简体中文**

[![CI](https://github.com/AOROM/paperreading/actions/workflows/ci.yml/badge.svg)](https://github.com/AOROM/paperreading/actions/workflows/ci.yml)

面向金融、经济、管理与社会科学论文的 Codex skill。它把论文整理为 13 个可复核字段，区分论文主张、经验证据与研究者判断，提出可执行的后续研究设计，并可安全写入既有 Excel 文献研读表。

## 核心能力

- 按固定顺序提取题名、作者、期刊、等级、时间、关键词、研究问题、结论、研究逻辑、实证模型、数据与变量以及延伸设计。
- 对基准结果、作用机制、异质性、经济后果、内生性与稳健性检验进行分层表达。
- 避免把相关关系误写为因果关系，不补造缺失的变量、模型、数据来源或期刊等级。
- 在兼容的 12 列工作簿中安全补充第 13 列，并保留原有内容、样式、公式、筛选与表格结构。
- 写入前查重；写入时先保存临时文件并验证，再备份和原子替换原工作簿。

## 项目结构

```text
paperreading/
├── skills/papers-reading-skill/   # 可直接安装的 skill
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   └── scripts/append_paper_reading.py
├── examples/                      # 示例输入
├── tests/                         # 端到端与结构测试
├── tools/                         # 仓库级校验工具
└── .github/workflows/ci.yml       # 自动校验
```

仓库层文档、测试与 CI 不会进入 skill 的运行上下文；真正需要安装的是 `skills/papers-reading-skill/`。

## 安装

1. 克隆仓库并安装脚本依赖：

   ```bash
   git clone https://github.com/AOROM/paperreading.git
   cd paperreading
   python -m pip install -r requirements.txt
   ```

2. 将 skill 目录复制到 Codex skills 目录。Windows PowerShell 示例：

   ```powershell
   Copy-Item -Recurse -Force `
     .\skills\papers-reading-skill `
     "$env:USERPROFILE\.codex\skills\papers-reading-skill"
   ```

3. 重新打开 Codex 会话，并通过 `$papers-reading-skill` 显式调用，或使用与论文研读、13 字段整理、文献表写入相关的自然语言请求触发。

## 配置工作簿

公开版本不包含任何个人工作簿路径。写入脚本按以下优先级解析目标文件：

1. 命令行 `--workbook <path>`；
2. 环境变量 `PAPER_READING_WORKBOOK`；
3. 两者均不存在时停止写入。

PowerShell：

```powershell
$env:PAPER_READING_WORKBOOK = "D:\research\paper-reading.xlsx"
```

Bash：

```bash
export PAPER_READING_WORKBOOK="/data/research/paper-reading.xlsx"
```

## 使用方式

仅生成草稿：

```text
使用 $papers-reading-skill 研读这篇论文，生成 13 个结构化字段，但不要写入工作簿。
```

写入已配置的工作簿：

```text
使用 $papers-reading-skill 研读这篇论文；核验字段完整后，写入中文工作表。
```

直接调用确定性写入脚本：

```bash
python skills/papers-reading-skill/scripts/append_paper_reading.py \
  --workbook "/path/to/paper-reading.xlsx" \
  --sheet 中文 \
  --data-json examples/paper-reading.example.json
```

中文论文使用 `--sheet 中文`，英文论文使用 `--sheet 英文`。脚本输出 JSON 状态，例如 `paper_appended`、`duplicate_skipped`、`schema_updated` 或 `error`。发生校验错误时，原工作簿保持不变。

## 字段与期刊等级边界

字段定义见 [`reading-fields.md`](skills/papers-reading-skill/references/reading-fields.md)。期刊等级仅记录经可靠来源确认的原始标签；不同评价体系之间不得推断或换算。涉及当前评价、职称、成果申报或投稿决策时，必须核实适用体系、版本与生效日期。

## 开发与验证

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_skill.py skills/papers-reading-skill
python -m unittest discover -s tests -v
```

GitHub Actions 会在推送和拉取请求上验证 skill 元数据，并对 Excel 写入、重复检测、环境变量配置和失败不改源文件等行为执行端到端测试。

提交变更前，请阅读[中文贡献指南](CONTRIBUTING.zh-CN.md)。

## 许可

本仓库目前未附加开源许可证。公开可见不等于自动授予复制、修改或分发权利。
