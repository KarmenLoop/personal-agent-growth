# 从学习计划到可核验的行动

Personal Agent Growth 0.6.0 贡献者的 15 分钟工作坊。

你将运行两个自适应学习工具，检查一次有意触发的陈旧修订拒绝，并解释哪些工作属于宿主 Agent。需要 Python 3.11+、包含两个工具的代码检出目录、终端，以及同目录下的 `practice.py`。工具仅使用 Python 标准库。请在工作坊前预留环境准备时间；15 分钟是组织活动的目标，不是实测完成时间。

## 完成后应能做到

- 通过匹配问题结构或机制标签检索候选，并检查其条件。
- 区分计划、已登记的启动、真实宿主动作和观察。
- 从预期的陈旧修订拒绝中恢复，同时保留失败记录。
- 解释为何受控样例通过既不等于经审阅的交付，也不证明有人学会了。

## 15 分钟安排

| 分钟 | 要做的事 | 可见结果 |
| --- | --- | --- |
| 0–2 | 阅读下面四项区别，预测 `start` 是否会写结果文件。 | 运行前保存一句预测。 |
| 2–4 | 检查 `practice.py`，特别是受控样例标记与 `reviewer: None`。设置三个路径。 | 有效的代码检出目录与一个新的输出路径。 |
| 4–8 | 运行一次练习，阅读陈旧修订失败与成功启动回执。 | 八次 CLI 调用，其中一次为预期拒绝。 |
| 8–11 | 追踪真实宿主写入及其在观察中的产物哈希，检查最终状态。 | 修订 3、`active`、没有待定动作、最新结果为 `progress`。 |
| 11–14 | 尝试下面的独立变式，解释一个不同领域的类比及其局限。 | 预测、新查询和已检查的输出。 |
| 14–15 | 完成退出检查，为失败或未完成工作保留下一步。 | 一份简短、有证据的交接。 |

## 始终区分四件事

`experience_transfer.py` 检索声明的标签并检查条件，不会推断任意同义词或证明因果机制。不同领域可以匹配；仅有相同领域不能使候选进入结果。复用前阅读候选的原范围、例外、反馈和完整 `snapshot_ref`。

`adaptive_learning.py plan` 保存提出的问题与动作。其分数采用声明的重要性、信息收益和耗时估计，只是建议，不是实测的学习速度分数。

`start` 保存意图与启动 token，动作仍由宿主执行。`observe` 把结果绑定到该 token 和真实产物。已知终态结果清除待定动作后，按当前修订提出下一动作，不要静默继续旧队列。`unknown` 结果保留同一待定动作及启动 token；提出新计划或重试前，先核实其实际效果。

`progress` 可在没有审阅者时记录。`delivered` 要求已经启动的交付动作、已解决的阻断问题、准确的验收检查、产物，以及实际独立审阅。不同的身份字符串本身不能证明独立性。

## 运行受控练习

以下是 POSIX shell 命令。将 `PYTHON` 设置为 Python 3.11+ 可执行文件，将 `SKILL_DIR` 设置为代码检出目录，将 `WORKSHOP_DIR` 设置为本讲义和 `practice.py` 所在文件夹。使用新的 `LAB_DIR`；脚本拒绝已有目录，以保留早先失败。Windows 用户可在 PowerShell 中使用自己的 Python 可执行文件和原生路径传入相同参数，但本讲义未测试该 shell 变式。

```sh
PYTHON="python3"
SKILL_DIR="/absolute/path/to/personal-agent-growth"
WORKSHOP_DIR="/absolute/path/to/workshop"
LAB_DIR="/absolute/path/to/new-workshop-lab"
"$PYTHON" --version
"$PYTHON" -B "$WORKSHOP_DIR/practice.py" --skill "$SKILL_DIR" --work "$LAB_DIR"
```

脚本使用明确标记的受控经验样例，不将它冒充真实历史经验。脚本通过子进程调用实际工具，并在编号回执目录中保留完整参数数组、原始 stdout/stderr、实际时间戳、退出码和哈希。它不模拟审阅者，也不声明交付。

运行后阅读这些文件：

```sh
cat "$LAB_DIR/05-stale-start/stderr.txt"
cat "$LAB_DIR/06-start/stdout.txt"
cat "$LAB_DIR/learning/host-action.json"
cat "$LAB_DIR/08-status/stdout.txt"
cat "$LAB_DIR/summary.json"
```

计划将运行推进至修订 1 后，失败调用等同于下面的命令。不要在后来的状态重跑它，再声称是同一次尝试。

```sh
"$PYTHON" -B "$SKILL_DIR/scripts/adaptive_learning.py" start --root "$LAB_DIR/learning" --id practice --action write-evidence --expected-revision 0
```

预期退出码为 2，并包含陈旧修订诊断。脚本保留这次拒绝，再使用已知的当前修订 1。实际工作中，选择下一命令前应检查状态及待定效果；未知效果必须先核实，不可盲目重复。

## 独立变式：把一个条件改为未知

查看答案前，先预测新查询中 `decision-can-be-revised` 从 `true` 变为 `null` 会发生什么。将 `learning/query.md` 复制到新文件，为它指定新 ID，只修改这一事实。保留原件。运行：

```sh
"$PYTHON" -B "$SKILL_DIR/scripts/experience_transfer.py" retrieve --root "$LAB_DIR/learning" --query "$LAB_DIR/learning/query-unknown.md"
```

解释候选是消失，还是仍然存在但探针被阻止。真实任务中，什么证据能确认这一条件？然后说出一个软件之外的领域，描述一项对应关系和一个可能使类比失效的差异。仅仅重命名领域不算迁移。

<details>
<summary>预测并运行之后再核对</summary>

匹配候选应当仍然存在，`unresolved_conditions` 中含有 `decision-can-be-revised`，且 `eligible_for_probe` 为 false。不要为了获得资格就把事实改回去，应先用实际证据确认。标签不匹配则可能返回零候选，因为这里采用明确标签检索。

</details>

## 退出检查与失败诊断

只有能指出已保存预测、预期失败回执、成功启动 token、宿主单独写入的文件及匹配的观察产物，才算练习通过。解释为何这里最终的 `active`/`progress` 是正确状态。声明教学成功前，请另一位贡献者检查独立变式和解释。

| 观察 | 含义与下一动作 |
| --- | --- |
| 陈旧修订启动退出 2 | 预期练习结果。读取当前修订，保留这次失败。 |
| 其他命令非零退出 | 计划外失败。保留 stdout/stderr，先诊断第一个失败操作，再开始新练习目录。 |
| 无匹配候选 | 检查问题结构与机制词汇，不要声称不存在相关知识。 |
| 候选存在未知或冲突条件 | 调查条件或拒绝类比；分数不是行动权限。 |
| 有回执，但产物丢失或改变 | 该证据不能支持对应声明。保留原尝试，重新检查实际对象。 |
| 脚本运行成功，但解释或变式失败 | CLI 执行成功，教学验收仍未完成。修复这一具体误解。 |

## 来源与范围

为本工作坊检查的项目来源：[自适应教程](https://github.com/KarmenLoop/personal-agent-growth/blob/main/docs/adaptive-learning.en.md)、[自适应协议](https://github.com/KarmenLoop/personal-agent-growth/blob/main/references/adaptive-learning.en.md)、[能力协议](https://github.com/KarmenLoop/personal-agent-growth/blob/main/references/capability-learning.en.md)，以及 `scripts/adaptive_learning.py` 和 `scripts/experience_transfer.py` 的实际 `--help` 与源码。证据包中的本地源码指纹标识受测候选；随提交变化的 `main` 链接可能与该候选不同。

工作坊采用项目中的预测、实践、反馈及限定声明范围的方法，不声称实测了人类学习、延迟记忆保持、冻结权重模型改进、普遍迁移或已采用的 PPC 策略。练习检查的是受控 CLI 契约，实际教学效果需要独立学习者的工作。

Copyright (C) 2026 KARMENLOOP Official Team. SPDX-License-Identifier: AGPL-3.0-only
