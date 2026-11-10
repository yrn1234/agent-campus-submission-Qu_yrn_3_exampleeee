# 效果验证

运行命令：`python -m unittest discover -s tests -v`。测试覆盖：明确答案、冲突、资料外、改写问法、上下文追问、读取工具失败、步数上限、不存在的引用。实际测试结果见 `examples/test-results.txt`。

实际 CLI 输入与完整输出（含工具参数、返回摘要、下一步动作、简短依据）：

| 场景 | 输入 | 实际输出 |
| --- | --- | --- |
| 正常、改写问法 | `examples/normal.input.json` | `examples/normal.output.json` |
| 文档冲突 | `examples/conflict.input.json` | `examples/conflict.output.json` |
| 资料不足 | `examples/missing.input.json` | `examples/missing.output.json` |
| 工具失败 | `examples/failure.input.json` | `examples/failure.output.json` |
| 上下文追问 | `examples/followup.input.json` | `examples/followup.output.json` |

两条不同决策路径：正常路径 `search → read → finish(answered)`；资料不足路径 `search → search → finish(insufficient_information)`；冲突路径读取两个原文后请求确认；工具错误路径观察错误后停止。

限制：本次仅运行离线 Mock；没有 API 凭证与真实模型质量数据。主题词检索覆盖合成资料，不具备开放域召回能力。Mock 的冲突判断只是文本差异，复杂制度需要识别适用范围、优先级和生效期。引用字符串校验不等于语义蕴含校验。
