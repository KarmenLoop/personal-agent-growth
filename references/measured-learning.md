# 未见任务、完整成本与因果经验迁移

[English](measured-learning.en.md)

在验证策略变更、经验能否帮助新任务，或声称提速/降成本时读取本协议。普通任务可复用已经适用的策略；新的收益主张需要比较证据。学习语义继续落在既有 Markdown 根，原始事件与 JSON 输出作为证据或派生视图。

## 固定策略，再发布目标

先说明比较的单位、候选、原任务质量标准、模型配置、重复次数、全程预算和停止条件。通用短板改法与领域改法各自成文；修改组合后另做实跑。策略作者应先冻结候选，再由独立任务作者从真实失败中组织未见任务；不向执行 Agent 提供参考答案、预期诊断或私有验收程序。

`scripts/blind_trials.py` 保存 Markdown 策略冻结记录、绑定随后发布的目标输入与验收哈希，并按任务/重复块生成带种子的运行顺序。每个块包含所有候选，各次使用新上下文。目标和策略发生变化会阻止继续沿用冻结记录。该程序不证明任务对模型的预训练是陌生的，也不提供系统级文件隔离；宿主负责工作区与只读验收边界，审阅实际访问轨迹。候选不能修改自己的验收标准。

已经用于排错的目标属于开发证据；保留该失败，以尚未暴露的保留任务验证修复。历史任务重放与新变式分别标记。一次任务里的许多断言、命令或多次自我赞同不是独立重复。

## 计量完整执行，保留缺失值

记录输入准备、实际 Agent 启动至交付、工具活动、失败重试、独立验收、审阅与发布的边界。比较窗口应包含对任务有用的预习、经验读取和修复；研究/审阅的语义标签是声明，不是仅凭进程时间就能独立测得的事实。整个学习研究的工具开发、来源准备和发布成本单独记账，不能隐藏或随意摊入某一路。

`scripts/task_costs.py` 从已绑定哈希的 Codex 原生事件、宿主逐事件单调时钟和完整执行窗口生成不可覆盖的 Markdown 记录。它能记录：

- 原生输入、缓存输入、输出及可取得的推理 token 明细；缓存输入已包含在输入中，推理明细已包含在输出中。
- 完整试次和 Agent 进程耗时，已观察工具区间的并集、重叠区间及未归因时间。
- 原生回合失败、重连、未返回的使用量、命令状态和未知费用。

未归因时间可能包含模型、网络和宿主开销，不写成已测得的推理耗时。父区间和其中的子区间不能相加当总耗时。无返回量时写未知，不填零；有错误/重连时保留已知使用量并标记覆盖不完整。没有提供账单时，原生 token 是资源消耗指标，不代表实收金额。账号整体额度变化也不等于单个任务费用。哈希证明内容身份，不认证提供者。

需要在已授权的本地 CLI 上执行时，可调用 `scripts/run_agent_trial.py`。它实际启动 Codex，逐条保存原生事件与时钟，限制期限和命令数，单独运行外部验收，并调用成本记录器。模型、权限、输入、策略和传输配置须在各路一致；使用现有 CLI 登录，不复制凭据或更改全局配置。受控调用可显式读取指定 skill，省去无关自动上下文。停止本地调用不保证远端推理已停止计费，也不等于撤销外部效果；有未知效果时先核实再重试。

## 迁移机制，验证成立条件

既有 `scripts/experience_transfer.py` 继续支持旧的标签检索；新增可选的 `causal_model` 描述变量角色、有方向的关系和可检验预测。目标查询可给出 `causal_context` 与针对来源经验的 `causal_mappings`。从现有旧经验推导模型时，应建立有来源的新候选经验，不覆盖原记录。

每次类比写清：

1. 来源经验解决什么问题，实际证据是什么。
2. 来源变量分别对应目标里的什么，关系方向与变量角色是否保留。
3. 哪些必要条件已经验证，哪些未知，最强反例是什么。
4. 在目标上采用该机制会出现什么可观察结果，什么结果将推翻它。
5. 实际采用、调整或拒绝后的产物和使用反馈。

显式映射可以召回没有共同标签的经验。反向关系、合并不同变量、角色不符或缺少来源模型时不能把映射当作成立；原有条件冲突与负反馈仍会阻止试用。结构相符仅提供一个待检验假设，不能证明真实因果、应用有效或获得新权限。文本里的预测也必须真正执行才算证据。

可选字段的精确结构如下；它们添加在既有 experience/query 元数据中。变量 ID 可以改名，角色与关系由宿主明确对齐，不由脚本自动猜测。以下只是格式示例，没有实际实验结论。

```json
{"causal_model":{"variables":{"state":"context","claim":"decision"},"relations":[{"from":"state","to":"claim","relation":"conditions"}],"predictions":[{"intervention":"Change a prerequisite","expected":"Recheck the dependent claim","falsifier":"The claim has independent support"}]}}
```

目标查询的 `causal_context` 使用同一图结构。`causal_mappings` 按来源经验 ID 索引：

```json
{"causal_context":{"variables":{"target-state":"context","target-claim":"decision"},"relations":[{"from":"target-state","to":"target-claim","relation":"conditions"}],"predictions":[{"intervention":"Describe a target check","expected":"Describe the observable prediction","falsifier":"Describe contrary evidence"}]},"causal_mappings":{"source-experience-id":{"variables":{"state":"target-state","claim":"target-claim"},"rationale":"Why this relationship could transfer","prediction":"What to check in this task","falsifier":"What would reject the analogy"}}}
```

使用原命令 `experience_transfer.py add --root <root> --experience <candidate.md>` 保存新候选，再用 `retrieve --root <root> --query <query.md>` 读取映射与阻塞条件。元数据首段可使用 JSON 对象作为 YAML front matter；源证据仍需真实路径与 SHA-256，不能把占位符当作已验证输入。

## 用结果决定采用范围

先独立核验任务产物和相关轨迹，再比较同一任务、所有重复的完整时间与已知资源。记录成功、失败、取消和无法比较项；不要挑最快一次或只比较通过次数。使用既有 PPC 门槛和回归要求，分别报告任务质量、原生 token、时间与费用覆盖。

两路都正确不证明新策略更好；节省 token 不自动证明节省金额；小规模组合不证明普遍精通。未达到预先规定的收益或成本/质量护栏，就保留原策略与候选，不自动全局启用。未来独立任务真正读取、使用或拒绝经验，并留存结果后，才获得进一步迁移证据。

<!-- Copyright (C) 2026 KARMENLOOP Official Team. SPDX-License-Identifier: AGPL-3.0-only -->
