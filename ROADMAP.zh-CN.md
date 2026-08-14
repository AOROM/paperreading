# PaperReading 路线图

[English](ROADMAP.md) | **简体中文**

本路线图区分已经交付的行为与技术假说。只有公开契约、失败行为、测试、文档和兼容性影响全部明确，一项能力才算完成。路线图不承诺日期：发布由研究有效性门槛决定，而不是由日历压力决定。

## 已交付基础

### v0.2 — Research Intelligence Core

状态：已实现，并继续作为兼容性契约维护。

- 严格的 `PaperRecord` 与 `EvidenceRef` 模型。
- 确定性的来源位置具体度评分。
- 证据与因果语言校验。
- JSON、Markdown、旧版 13 字段与安全 Excel 输出。
- CLI、Python API、公开 Schema、合成示例与 CI 门禁。

### v0.3 — Schema Separation & Migration

状态：已实现。

- 公开的 `PaperDocument`、`PaperDraft` 与 `PaperPackage` 模型。
- 分离来源约束记录与研究者或 AI 辅助分析。
- 使用规范化 `EvidenceSpan` ID 构建稳定证据图。
- 确定性 v0.2 → v0.3 迁移，并显式保留溯源局限。
- `.paperreading/` 下原子化且可检查的项目存储。
- 版本化 Schema 与向后兼容的 13 字段投影。

### v0.3.1 — Core Hardening

状态：已实现。

- 通过统一 `DocumentParser` Port 接收 UTF-8 文本、Markdown 与可选的带文本层 PDF。
- 明确 PDF 边界：不包含 OCR、版面几何、表格重建或图形提取。
- 分别记录来源二进制 SHA-256 与规范化提取文本 SHA-256。
- 可注入带时区的摄取、提取与定稿时间，支持可复现运行。
- Provider 中立的多阶段提取契约，以及确定性离线 JSON 适配器。
- 在 Draft → Review → Finalize 全流程保留 Candidate 与 Conflict。
- 定稿守卫会拒绝未解决 Draft、已变化文档、重叠字段与缺失证据。
- Evidence Verification v2 使用保守的局部窗口模糊引文对齐。
- 新增 `extract`、`review`、`finalize` 与高层 `read` 命令。
- 提供可通过严格来源核验的关联式合成端到端示例。

## v0.4 — Evidence Engine

状态：规划中，尚未实现。

发布门槛：

- 至少一个真实模型 Provider 适配器，具备结构化输出校验、重试策略、限流行为与不泄露密钥的运行元数据。
- 针对 Metadata、Question、Theory、Data、Variable、Design、Finding、Mechanism、Heterogeneity、Robustness 与 Limitation 的分阶段 Prompt 契约和样本。
- 将 PDF 几何适配器与 OCR 适配器作为不同能力实现，并明确记录溯源与弃权行为。
- 对表格、图形、方程、Bounding Box 与附录进行类型化核验；不支持的表面必须保持 `partial`，不得猜测。
- 发布可再分发的 PaperReading-Bench、版本化标注规范，以及 Unsupported Claim、位置解析、引文对齐、冲突与因果语言指标。
- 同时设置提取质量与弃权质量回归门禁；不得使用隐藏或受版权保护的来源文本调优公开 Benchmark。

## v0.5 — Research Library

状态：规划中，尚未实现。

发布门槛：

- 支持恢复、条目级失败隔离、幂等执行和可导出运行报告的批量摄取。
- 在既有 Repository Port 后加入 SQLite，并提供显式 Schema Migration 与备份说明。
- 按方法、变量、数据集、证据状态、来源和用户标签搜索筛选。
- 确定性 Literature Matrix，且每个单元格保留记录与证据溯源。
- 扩展实证方法 Schema，覆盖 Estimand、处理时点、对照组、识别假设、诊断与不确定性。
- 增量索引不得静默改变已经定稿的 PaperPackage。

## v0.6 — Research Intelligence

状态：规划中，尚未实现。

发布门槛：

- 只基于已复核记录识别跨论文共识与矛盾。
- 每项综合陈述绑定支持、反对以及被排除的论文 ID。
- 使用公开分类体系生成证据派生 Gap Candidate，并显示证据覆盖边界。
- 分别展示可行性、新颖性和证据覆盖，不提供不透明的“研究质量”总分。
- 首批 OLS、面板固定效应、DID、IV 与 RDD Auditor，包含方法专属弃权与误报测试。
- 从已复核 Gap 生成可执行研究设计，但将其存入 Analysis，而不是来源发现。

## v1.0 — Stable Ecosystem

状态：规划中，尚未实现。

发布门槛：

- 稳定 Schema、弃用、迁移与支持政策。
- 带签名溯源的 PyPI 发布和可复现构建说明。
- Provider、Parser、Repository、Verifier 与 Exporter 插件入口。
- MCP、Zotero、BibTeX 和更多 Agent Adapter。
- 公开 PaperReading-Bench 方法、基线、局限与治理机制。
- 适用于真实研究团队的安全、隐私、版权与数据保留说明。

## 跨版本不变量

以下不变量受规范性[《学术研究底层逻辑》](RESEARCH_PRINCIPLES.zh-CN.md)约束。

1. 来源主张、报告证据与研究者分析始终保持分离。
2. 每项跨论文派生陈述都标识支持、反对或被排除的记录。
3. 因果表述不得强于识别证据。
4. 可追溯性和核验分数不得伪装成真实性或研究质量。
5. Domain 始终独立于 Interface、Provider、Storage 与 Exporter。
6. 缺失、冲突和不支持的信息必须保持可见；系统可以弃权。
7. 可复现性记录来源身份、提取文本身份、配置、Provider、Model、Prompt 版本与时间。
8. 旧版 Excel 兼容持续由成功路径和失败路径测试覆盖。
9. 规划功能不得被文档描述为已经交付。
