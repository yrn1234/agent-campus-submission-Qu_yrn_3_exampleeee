# 企业知识问答 Agent（项目 3）

面向员工的合成制度问答 CLI。Agent 每步选择 `search`、`read` 或 `finish`，读取工具结果后再决定下一步。输出包含状态、回答、可核对的原文引用、资料缺口和逐步 Trace。

## 环境与运行

- Python 3.7+，仅使用标准库，无需安装第三方依赖。
- 离线演示（**Mock 决策策略，只验证流程，不证明真实模型决策能力**）：

```bash
python -m src.cli "年假需要提前多久申请？" --mode mock
python -m src.cli "报销期限是多久？" --mode mock
python -m src.cli "年假需要提前多久申请？" --mode mock --fail-tool read
```

- 真实模型：设置 `MODEL_API_KEY`、`MODEL_NAME`，可选 `MODEL_BASE_URL`（兼容 Chat Completions JSON mode 的服务），再运行：

```bash
python -m src.cli "报销期限是多久？" --mode live
```

PowerShell 示例：`$env:MODEL_API_KEY="..."`。不要提交真实密钥。真实模型结果随服务变化，当前仓库未提供真实模型实测记录。

- 上下文追问：`python -m src.cli "还需要主管批准吗？" --history-file examples/history.json`
- 自定义资料：`--documents path/to/documents.json`
- 步数上限：`--max-steps 8`；耗尽时返回 `incomplete_step_limit`。

## 验证

```bash
python -m unittest discover -s tests -v
```

评审入口：`tests/test_agent.py` 覆盖六项必验、引用校验与步数限制；`examples/` 有实际 CLI 输出及每步 Trace；`data/documents.json` 为可替换的合成资料；`docs/` 记录需求、设计、评估、AI 使用及复盘。

原题说明归档于 `docs/assignment.md`。

目标 GitHub 仓库：[agent-campus-submission-Qu_yrn_3_exampleeee](https://github.com/yrn1234/agent-campus-submission-Qu_yrn_3_exampleeee)。最终 commit SHA 以实际推送后 `git rev-parse HEAD` 为准。
