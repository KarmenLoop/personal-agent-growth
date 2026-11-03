# 动态学习教程 · 0.6.1

[English](adaptive-learning.en.md) · [运行协议](../references/adaptive-learning.md) · [机制与反馈图](diagrams/adaptive-learning.zh-CN.svg)

本扩展增加跨领域候选经验检索和可恢复的学习动作闭环。Python 3.11+ 标准库即可运行。理解问题、提出候选、调用真实工具和审阅内容由宿主 Agent 完成；工具不内置模型、后台工作者或固定领域课程。

## 一个根目录，两类关联记录

明确选择实际共用的 Markdown 根。既有项目、日报、能力记录和旧经验保持原位。

```text
learning/
  projects/<project-id>/context.md
  projects/<project-id>/nodes/...
  experience/mechanism/<experience-id>/
    experience.md
    observations/000001.md
  learning-runs/<run-id>/
    request.md
    events/000001.md
  evidence/<task-id>/...
```

机制经验保留不可变的原知识与另行追加的使用反馈；学习运行记录当前任务怎样推进。它们承担不同职责，不是两套可编辑摘要。命令的 JSON 输出为派生结果。原始产物放在不可变日志之外；后续会修改的文件先留稳定副本再作为证据。

以下输入均使用 JSON 对象形式的 YAML 1.2 文首元数据，标准库读取器不支持任意 YAML。所有产物路径相对于学习根，与输入文档放在哪里无关。身份、发现、路径和哈希必须来自实际观察；哈希占位符故意不能直接通过。这些是模板，不是已完成的 Agent 实测。

在已安装 Skill 目录运行命令，替换 `/absolute/learning` 和文档路径。Windows 将 `python3 -B` 换为 `py -3 -B -X utf8` 并使用实际 D: 或 C: 路径；下列命令均为单行。

## 1. 加入机制经验

保存 `experience-input.md`，例如：
```markdown
---
{
  "id": "batch-setup",
  "type": "mechanism-experience",
  "source_task_id": "software-batch-01",
  "domain": "software",
  "problem_structure": [
    "repeated-setup",
    "independent-items"
  ],
  "mechanisms": [
    "setup-amortization"
  ],
  "required_conditions": {
    "setup-repeatable": true
  },
  "exceptions": [
    "Check quality, deadlines and resource contention before applying outside the source task."
  ],
  "intervention": "Group independent items when shared setup dominates the source task.",
  "explanation": "Grouping reduced repeated setup in the source task; usefulness elsewhere is a hypothesis.",
  "validation": "hypothesis",
  "executor": "replace-with-actual-host-session",
  "reviewer": null,
  "artifacts": [
    {
      "path": "evidence/source-result.md",
      "sha256": "replace-with-actual-64-character-sha256"
    }
  ]
}
---
## 原始范围
写明原任务、真实结果、其他可能解释和仍需验证之处。
```

```sh
python3 -B scripts/experience_transfer.py add --root /absolute/learning --experience /absolute/experience-input.md
python3 -B scripts/experience_transfer.py status --root /absolute/learning --id batch-setup
```

`validation` 可为 `hypothesis` 或 `supported`。supported 要求不同的声明审阅者及已校验产物，只表示原范围获得支持，不是普遍适用。程序校验声明和字节，不能证明内容或身份真实。修订经验时用新 ID，在正文回链原经验和反证，保留原件。

## 2. 为陌生领域检索

保存 `query.md`：
```markdown
---
{
  "id": "query-new-work",
  "type": "transfer-query",
  "task_id": "new-task-01",
  "domain": "unfamiliar-service",
  "problem_structure": [
    "repeated-setup"
  ],
  "mechanisms": [
    "setup-amortization"
  ],
  "facts": {
    "setup-repeatable": null
  },
  "keywords": [
    "setup"
  ]
}
---
## 待验证映射
说明这些关系标签为什么可能连接旧任务与新任务，以及类比会在哪里失效。
```

```sh
python3 -B scripts/experience_transfer.py retrieve --root /absolute/learning --query /absolute/query.md --limit 5
```

至少命中一个问题结构或机制标签；仅同领域或关键词相同不会进入候选。标签规范化 Unicode、大小写和空白；同义词及跨语言关系需宿主明确对齐。这是可解释的结构标签检索，不是向量模型或自动因果发现。

检查命中关系、未知/冲突条件、原文和相关反馈。例中的 `setup-repeatable` 未知，需真实确认后才可能成为可探针候选。可探针不意味着获得行动权限或证明旧方案有效。同领域有害反馈在条件匹配或核实所需事实未知时阻止复用。另一领域的有害反馈若条件不矛盾，仍显示为未经本领域验证的反例；不会自动扣分或阻止探针。

候选提供 `snapshot_ref`，含 `path`、`sha256`、`revision`、`head_sha256`。将完整对象放进学习计划的 `experience_refs`，同时绑定经验原件和反馈修订。`evidence_refs` 是产物路径/哈希对。不要猜修订号，也不要在反馈变化后只保留原经验哈希。

## 3. 启动有预算的学习运行

保存 `request.md`：
```markdown
---
{
  "id": "request-new-work",
  "type": "learning-request",
  "goal": "Determine whether batching helps this new task without reducing quality.",
  "domain": "unfamiliar-service",
  "acceptance": [
    "Recommendation is supported by the supplied evidence.",
    "Quality and timing tradeoffs are stated."
  ],
  "budget_seconds": 1800,
  "max_actions": 6,
  "allowed_actions": [
    "retrieve",
    "research",
    "experiment",
    "reflect",
    "deliver"
  ]
}
---
## 上下文与授权
记录用户目标、当前约束、允许的输入与操作，以及本任务为什么值得做。
```

```sh
python3 -B scripts/adaptive_learning.py init --root /absolute/learning --id new-task --request /absolute/request.md
python3 -B scripts/adaptive_learning.py status --root /absolute/learning --id new-task
```

运行从 revision 0 开始。预算按 init 后实际经过的时间计算，包含本次运行内规划和等待，不包含 init 之前的准备。工具不能终止宿主工具或读取供应商账单；它阻止超限后开始新动作、记录超时，仍允许核实一个已经启动动作的实际结果。

可选 `max_plans` 限制规划次数，范围 1–400，默认是 `max_actions` 的四倍。`estimated_seconds` 范围为 0.001–604800；单条持久化 Markdown 不超过 1 MiB。一次运行最多 1000 个事件：revision 达到 998 后停止新计划与新启动，达到 999 后拒绝继续报告 unknown，并为待定动作的最终核实保留末槽。完成、动作/规划上限和连续无进展时冻结已记录耗时；待核实的 pending 动作仍继续计时。这些边界防止迭代过程无止境扩张。`allowed_actions` 支持 `research`、`retrieve`、`experiment`、`tool`、`reflect`、`deliver`、`ask`；它们是操作类别，不是学科限制。仅在任务可能确需用户取舍或操作时包含 ask，不为 Agent 能自行查明的普通未知打扰用户。

## 4. 提出并选择下一有效动作

保存 `plan.md`：
```markdown
---
{
  "id": "plan-inspect",
  "type": "learning-plan",
  "based_on_revision": 0,
  "unknowns": [
    {
      "id": "conditions",
      "question": "Can setup be shared without breaking the new task quality requirement?",
      "importance": 1.0,
      "blocking": true
    }
  ],
  "actions": [
    {
      "id": "inspect-evidence",
      "kind": "research",
      "question_ids": [
        "conditions"
      ],
      "description": "Inspect source evidence and identify the local setup and quality constraints.",
      "expected_information_gain": 0.8,
      "estimated_seconds": 120,
      "preconditions": []
    }
  ],
  "experience_refs": [],
  "artifacts": []
}
---
## 预测
写明不同观察会怎样改变行动。此模板没有绑定经验；若实际依赖候选，填入读取所得的完整 snapshot_ref。
```

```sh
python3 -B scripts/adaptive_learning.py plan --root /absolute/learning --id new-task --proposal /absolute/plan.md --expected-revision 0
python3 -B scripts/adaptive_learning.py start --root /absolute/learning --id new-task --action inspect-evidence --reason "先查清决定该类比能否使用的条件。" --expected-revision 1
```

成功 plan 推进到 revision 1，start 到 2，并返回 `pending.start_id`。保留实际 token，后续观察必须绑定它。start 只是登记意图，之后宿主必须真正执行获准动作并保存回执。

排序分数为：所回答问题的最高重要性 × 预计信息收益 ÷ 预计秒数。这些是声明估计，不是已测的智力或速度。宿主可选择其他合格候选并解释原因。非空 `preconditions` 表示尚未解决的阻断条件；取得证据后再写新计划，不能仅删掉麻烦条件。

未解决问题必须保留在后续计划中。问题默认 `blocking: true`；明确标为非阻断的探索不阻止交付。需要替换错误的问题时，先用证据解决或否定原问题，再引入新 ID，不能改名掩盖未决事项。

## 5. 写实际反馈，再规划

宿主动作完成后保存 `observation.md`：
```markdown
---
{
  "id": "observation-inspect",
  "type": "learning-observation",
  "start_id": "replace-with-returned-pending-start-id",
  "action_id": "inspect-evidence",
  "outcome": "progress",
  "finding": "Replace with the actual observation and its limits.",
  "hypothesis_change": "Replace with the reason for keeping, narrowing or rejecting the proposed mechanism.",
  "resolved_questions": [],
  "artifacts": [
    {
      "path": "evidence/new-task-result.md",
      "sha256": "replace-with-actual-64-character-sha256"
    }
  ],
  "executor": "replace-with-actual-host-session",
  "reviewer": null,
  "cost": {
    "tokens": null,
    "usd": null
  },
  "acceptance_checks": {}
}
---
## 实际执行
保留命令、输入、stdout/stderr、退出码、产物身份、获得的协助及判断依据。
```

```sh
python3 -B scripts/adaptive_learning.py observe --root /absolute/learning --id new-task --observation /absolute/observation.md --expected-revision 2
python3 -B scripts/adaptive_learning.py status --root /absolute/learning --id new-task
```

终态观察推进到 revision 3 并清空旧计划。后继提案使用新修订和当前证据，不能静默执行旧队列。只解决本动作针对且实际得到证据的问题。failed/no_progress 不能标记问题已解决；若反证确实解答了问题，假设被推翻也可以是 progress，必须说明依据。

动作效果未知时用 `unknown`，保留同一 pending 动作和 start token，进入待核实状态，阻止盲目重试或新计划。此时可无产物，但 finding 必须明确。后来可对同一启动补实际观察，包括预算已耗尽时；不能捏造成功来解锁下一步。

token 与费用是声明的不重叠增量，不可得时保持 null。unknown 之后再核实同一动作时，不得重复计入整次费用。连续三次 failed/no_progress 后暂停新工作。完成、预算/次数上限、待核实是不同状态。

## 6. 把迁移反馈返回后续任务

旧经验确实用于另一个任务的应用或探针后，另存使用观察。以下 harmful 模板只适用于实际证据支持有害结果时：
```markdown
---
{
  "id": "use-new-work",
  "type": "transfer-observation",
  "task_id": "new-task-01",
  "domain": "unfamiliar-service",
  "conditions": {
    "setup-repeatable": true,
    "quality-sensitive-to-delay": true
  },
  "outcome": "harmful",
  "adaptation": "Replace with the actual adaptation and permitted test.",
  "finding": "Replace with evidence that applying the old intervention harmed the current acceptance criterion.",
  "executor": "replace-with-actual-host-session",
  "reviewer": null,
  "artifacts": [
    {
      "path": "evidence/new-task-result.md",
      "sha256": "replace-with-actual-64-character-sha256"
    }
  ]
}
---
## 新发现的边界
说明条件变化与下次检查。失败类比可以产生有用边界，不能据此删除原经验。
```

```sh
python3 -B scripts/experience_transfer.py observe --root /absolute/learning --id batch-setup --observation /absolute/use.md --expected-revision 0
```

相关反馈包含 `source_domain`、`target_domain`、`target_scope`（same-domain 或 cross-domain-unverified）及原 `adaptation`。存在这类跨领域有害反例的候选会设 `counterexample_review_required: true`，由宿主审视机制与条件是否适用；该标记本身不改变 `eligible_for_probe`。其他领域的 helpful/inconclusive 不自动作为当前领域的支持。

写前读取实际经验 revision。helpful 要求不同的声明审阅者；harmful/inconclusive 可保留 reviewer null。conditions 是观察到的布尔事实，不是猜测。负反馈的自动扣分与阻断只作用于记录的规范化领域及匹配或未决条件，不自动作用于其他范围。用新任务的实际事实再检索，读取反馈后选择。

学习运行观察不会自动写迁移观察。前者说明当前任务发生了什么，后者说明复用某条原经验的意义；适用时宿主分别落盘并核验。新增反馈使旧计划快照过期；依赖变化经验的新动作启动前，重新检索并制定计划。

## 7. 交付并保留下一有用问题

阻断问题解决后，提出 deliver 动作。delivered 观察必须含其真实 start token、实际产物、与执行者不同的审阅者，并在 `acceptance_checks` 中逐字使用请求中的全部验收字符串且值均为 true。程序的一致性检查不能判断产物有用，审阅者需要实际查看。其他结果可保留空 checks，或仅记录已有依据的项目。

回读状态，更新项目 context 和节点，回链候选经验及真实使用反馈。新宿主先读同一份文件再续；pending 动作需核实，不自动重做。无效、陈旧或漂移输入的 CLI 退出 2；检索也可能同时返回有效候选和错误、退出 2，不能丢弃错误后宣称完整覆盖。

## 连贯示例：新领域反过来修正旧经验

以下是设计示例，不是现场试验或已测提升。Agent 原先知道，将独立软件任务成组执行可能减少重复准备。现在要改善一个陌生服务流程，同时维持质量与等待要求。它召回准备开销机制，学习实际环节与资源限制，并验证分组假设是否成立。

如果观察发现，分组虽然减少准备，却让部分项目延迟到不能接受，就应拒绝在这些条件下采用旧方案。保留软件原证据，记录有害迁移情境，形成更窄的候选：只有延迟敏感质量和截止要求仍满足时，共享准备才可能有益。下一步查这些约束，而非默认继续增加并行工作者。

以后另一个软件任务有严格逐项截止要求时，可以同时召回旧收益和新边界。新领域因此改变了原领域里需要检查的条件；这种改变是否改善后续任务，仍需真正执行和审阅。

## 保留双层迭代约定

运行可以新增问题和候选，不能自行改写验收或预算。提示词、工具、检索和学习策略的变更仍进入 [PPC](../references/recursive-improvement.md)，包含原版/通用/领域真实对照与组合复验；[能力证据](capability-learning.zh-CN.md)继续单独限定范围。未来复习通过真实宿主调度登记，两工具均不提供后台执行。
