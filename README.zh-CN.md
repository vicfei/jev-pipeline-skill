# Jev Pipeline Skill（中文说明）

> **v0.1 早期原型**：链路已可离线端到端运行，接口与默认值随时可能调整。

把 Jev 问题设计串成一条命令：

```
find ──► fit ──► draft ──► lint ──► （收集真实响应）──► spread ──► threshold ──► cascade
```

找出代码库里"本质是决策"的 LLM 调用 → 判断该不该交给 Jev → 从实战模式库起草问题 → 静态检查 → （拿到真实响应后）检验问题有没有区分度 → 在难例上校准阈值 → 输出"执行/放行/升级"的级联方案。

**这是编排器，不是又一份目录。** 它以"引用而非复制"的方式调用社区最好的工具（见 [ATTRIBUTION.md](ATTRIBUTION.md)），并补上各自缺的那层胶水：贯穿全流程的统一候选记录、基于 [awesome-jev-prompts](https://github.com/vicfei/awesome-jev-prompts)（43 条模式，CC0）的模式化起草、以及"中间带 = 显式升级分支"的级联策略——不确定的答案永远不被平均成一个决定。

## 快速开始

```bash
git clone https://github.com/vicfei/jev-pipeline-skill && cd jev-pipeline-skill
pip install -e .

python -m jev_pipeline tools-sync          # 首次：克隆两个上游工具仓库
python -m jev_pipeline run examples/demo-repo
python -m jev_pipeline cascade examples/scores.jsonl
```

Python ≥ 3.10，纯标准库，所有步骤都**不需要 API key**（真实的 Jev 调用发生在你的业务代码里，不在本流水线里）。

## 各步骤一句话

| 步骤 | 回答什么 | 来源 |
|---|---|---|
| `find` | 代码库里哪些 LLM 调用输出的是决策而非文本？ | 调用 [abhisheksharma001/jev-skill](https://github.com/abhisheksharma001/jev-skill) 的 `find_decision_calls.py` |
| `fit` | 这个候选该不该用 Jev？go / 带护栏 / 不适用 | 调用 `fit_check.py`，答案文件会生成供你修改后重跑 |
| `draft` | 第一版问题长什么样？ | 原创——从 awesome-jev-prompts 模式库匹配模板 |
| `lint` | 草稿是否违反已知的问题设计规则？ | 调用 [VBS2004/jev-questions-skill](https://github.com/VBS2004/jev-questions-skill) 的 `lint_questions.py` |
| `spread` | 这个问题能区分开不同情形，还是恒定输出？ | 调用 `spread.py` |
| `threshold` | 阈值定在哪（在难例上拟合）？ | 调用 `threshold.py` |
| `coverage` | 正确选项是否根本没出现在候选里？ | 调用 `coverage.py` |
| `cascade` | 哪些答案执行、哪些放行、哪些升级给 System Two？ | 原创——双阈值策略：中间带和低置信度走高置信分支，绝不取中 |

设计三原则：**只调用、不复制**上游脚本（`tools-sync` 克隆原仓库，许可证归属见 ATTRIBUTION）；**没有任何步骤调 API**（校准数据来自你收集的 JSONL，`examples/` 里有合成示例）；**中间带是分支不是分数**（Noul 0.5 的含义是"判断不了"）。

独立社区项目，与 TypeSafe AI 无隶属。代码 MIT，模式内容经 awesome-jev-prompts 以 CC0 提供。English: [README.md](README.md)。
