# Contributing

感谢改进 Paper Reading Skill。提交变更前，请遵守以下约定。

## 变更范围

- 将 Codex 运行所需的指令、脚本和参考资料放在 `skills/papers-reading-skill/`。
- 将面向维护者的说明、测试、示例和 CI 配置保留在仓库层，避免增加 skill 的上下文负担。
- 不提交论文全文、未获授权的数据、个人工作簿、访问令牌、个人路径或其他敏感信息。
- 修改期刊等级资料时，注明来源、版本、生效边界和核验日期；不要把历史目录描述为当前目录。

## 本地检查

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_skill.py skills/papers-reading-skill
python -m unittest discover -s tests -v
```

新增或修改写入逻辑时，至少覆盖正常追加、重复跳过、表头不匹配不改源文件，以及显式路径或环境变量解析。

## Pull request

在说明中写清：

1. 要解决的问题；
2. 行为或字段契约是否变化；
3. 执行过的验证命令及结果；
4. 涉及外部资料时的来源与版本。
