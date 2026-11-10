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

PowerShell 示例：`$env:MODEL_API_KEY="..."`。不要提交真实密钥。此 API 入口尚未实测，真实模型结果随服务变化。

- 已登录 Codex CLI 的真实模型入口（本次实测使用 `codex-cli 0.166.0-alpha.6`、`gpt-6-sol`，不读取项目 API 密钥）：

```bash
codex login status
python -m src.cli "年假需要提前多久申请？" --mode codex
python examples/generate_codex.py
```

若本机通过代理访问模型，运行前设置 `HTTPS_PROXY`（以及需要时的 `HTTP_PROXY`）为本机实际代理地址。本次真实模型输入、输出和 Trace 见 `examples/codex-*.json`；模型输出可能因服务和时间变化，生成脚本会核对四个预期状态。`--mode live` 仍保留为兼容 Chat Completions 的 API 入口。

- 上下文追问：`python -m src.cli "还需要主管批准吗？" --history-file examples/history.json`
- 自定义资料：`--documents path/to/documents.json`
- 步数上限：`--max-steps 8`；耗尽时返回 `incomplete_step_limit`。

## 验证

```bash
python -m unittest discover -s tests -v
```

评审入口：`tests/` 覆盖六项必验、引用校验、步数限制和 Codex CLI 适配器；`examples/` 有实际 CLI 输出及每步 Trace；`data/documents.json` 为可替换的合成资料；`docs/` 记录需求、设计、评估、AI 使用及复盘。

原题说明归档于 `docs/assignment.md`。

目标 GitHub 仓库：[agent-campus-submission-Qu_yrn_3_exampleeee](https://github.com/yrn1234/agent-campus-submission-Qu_yrn_3_exampleeee)。最终 commit SHA 以实际推送后 `git rev-parse HEAD` 为准。
