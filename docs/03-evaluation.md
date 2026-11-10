# 效果验证

运行命令：`python -m unittest discover -s tests -v`。测试覆盖：明确答案、冲突、资料外、改写问法、上下文追问、检索与读取工具失败、步数上限、不存在的引用、检索误命中回归和 Codex CLI 适配器。实际测试结果见 `examples/test-results.txt`。

实际 CLI 输入与完整输出（含工具参数、返回摘要、下一步动作、简短依据）：

| 场景 | 输入 | 实际输出 |
| --- | --- | --- |
| 正常、改写问法 | `examples/normal.input.json` | `examples/normal.output.json` |
| 文档冲突 | `examples/conflict.input.json` | `examples/conflict.output.json` |
| 资料不足 | `examples/missing.input.json` | `examples/missing.output.json` |
| 工具失败 | `examples/failure.input.json` | `examples/failure.output.json` |
| 上下文追问 | `examples/followup.input.json` | `examples/followup.output.json` |

真实模型运行：`codex-cli 0.166.0-alpha.6`，模型 `gpt-6-sol`，通过已登录的 Codex CLI 调用；脚本 `python examples/generate_codex.py`（本机需设置 `HTTPS_PROXY`）。输入和实际输出均在 `examples/`：

| 场景 | 输入 | 实际输出与动作 |
| --- | --- | --- |
| 正常 | `codex-normal.input.json` | `codex-normal.output.json`：`search → read D03 → answered` |
| 冲突 | `codex-conflict.input.json` | `codex-conflict.output.json`：`search → read D01 → read D02 → needs_clarification` |
| 资料不足 | `codex-missing.input.json` | `codex-missing.output.json`：`search（无命中）→ insufficient_information` |
| 工具失败 | `codex-failure.input.json` | `codex-failure.output.json`：`search → read（失败）→ tool_error` |

真实模型根据 D03 原文回答“至少提前 3 个工作日”；观察 D01 的 30 天和 D02 的 15 天后列出冲突并请求确认。工具读取失败后没有猜测答案。Trace 每步含动作、工具参数、结果和简短决策依据。离线 Mock 也保留正常、补查、冲突、失败和上下文追问路径，以便不登录时复现流程。

首次真实正常用例曾得到 `invalid_answer`（`examples/codex-initial-invalid.output.json`）：查询词含“提交”，旧检索词表误将 D01/D02 一并命中；模型正确只读 D03，但保护性校验要求读取所有命中，故拒绝答案。加入检索回归测试并改为领域锚词后，真实运行通过。这次失败说明小词表的召回与精度仍需改进。

限制：真实模型只在四份合成资料上运行四组样例，不能代表开放域准确率；调用结果可能随模型版本变化。兼容 Chat Completions 的 `--mode live` 入口未实测。主题词检索不具备开放域召回能力。Mock 的冲突判断只是文本差异，复杂制度需要识别适用范围、优先级和生效期。引用字符串校验不等于语义蕴含校验。
