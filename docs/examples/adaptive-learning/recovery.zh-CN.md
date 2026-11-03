# 恢复结果不确定的自适应运行

使用同一个显式 Markdown 根、任务 ID 和当前工具版本。读取任务上下文与最新节点，再检查实际运行。保存的 `start` 记录意图，效果由宿主执行；观察记录宿主的证据与判断。这些操作都不会认证身份或登记唤醒。

```sh
python3 -B "$SKILL/scripts/adaptive_learning.py" status --root "$ROOT" --id "$RUN_ID"
```

将 `SKILL` 设置为 skill 代码检出目录，`ROOT` 设置为已有的共享学习根，`RUN_ID` 设置为原运行 ID。保存 stdout、stderr、退出码、命令、UTC 时间及工具哈希。保留不可变日志事件和早先失败尝试。绝不可通过修改旧观察或删除待定事件来修复恢复流程。

| 当前状态 | 操作者决定 | 继续前需要的证据 |
| --- | --- | --- |
| `active`，`pending: null` | 没有待定动作。检查最新观察及当前修订；没有当前计划时提出新计划，仅在核对前置条件和剩余限额后才启动合格动作。 | 当前根与运行身份、保留的原结果、当前产物哈希及任何经验快照，以及重复外部效果是安全的证据。 |
| `awaiting_observation` | 已有启动。确认宿主是否执行了效果；不要只因为 stdout 或观察回执缺失就再次启动。 | 原 `pending.start_id`、`pending.action.id`、工具回执及实际效果。结果仍不确定时，对该准确启动记录 `unknown`。 |
| `needs_reconciliation` | 保留同一待定动作与启动 token，只读检查外部系统或文件，不创建新计划，也不重复效果。 | 将实际效果身份和内容与预期操作、原启动关联。只核实证据能够证明的部分。 |
| `delivered` | 阅读已记录的交付产物与审阅。该已交付运行不再执行动作；另一个获准新任务需有自己的运行。 | 已记录验收检查、独立审阅及实际可用产物。声明本身不等于内容验收。 |
| `budget_exhausted`、`action_limit`、`plan_limit`、`journal_limit` | 停止在本运行下启动工作，保留状态与交接。不要只为绕过上限而提高限额或创建新运行。 | 继续工作所需的新授权范围或预算。工具不提供原地扩展限额的命令。 |
| `paused_no_progress` | 连续三次终态 failed/no_progress 观察使有效接续停止。诊断障碍并交接证据。 | 已改变的条件及获准后续范围；给动作改名不算进展。 |

待定动作优先于普通限额：即使时间预算已经耗尽，仍可能显示 `awaiting_observation` 或 `needs_reconciliation`。核实记录的是已经启动工作的结果，不授权新效果。核实完成后，运行可能立即报告限额耗尽。工具为结果核实预留日志空间，但损坏或遭外部修改的历史仍可能阻止重放。

## 核实结果，避免重复执行

1. 读取状态。如果缺失的观察其实已经提交，当前状态或日志会显示它；检查该记录，不要再次提交旧观察。JSON stdout 是派生视图，Markdown 才是持久记录。
2. 保留原 unknown 事件、待定启动 token、动作 ID、命令和任何部分输出。通过只读来源检查效果，例如准确文件内容、供应商操作 ID 或其他权威回执。仅仅缺少本地回执不能证明效果从未发生。
3. 如果效果已完成且归属明确，用**同一待定 `start_id` 和动作 ID**、最新 `revision` 及绑定哈希的证据提交新观察。普通完成工作使用 `progress`；已知终态失败可使用 `failed`，并明确保留任何部分效果。unknown、failed 和 no_progress 不能解决问题。
4. 如果效果仍不明确，保留 `unknown`，不要把不确定性改为 `failed` 来清空槽位。操作者缺少读取权限、归属不明、重复执行可能产生后果，或恢复需要未经批准的外部变更时，需升级处理。向用户说明已知效果、缺失证据和具体选择。
5. 工具接受**已知终态**观察后，会清除待定动作与旧计划。再次读取状态；只有运行仍为 active，才可按新修订提出新计划，然后开始另一动作。终态失败不能证明重复其外部效果是安全的。

使用带 JSON front matter 的 Markdown 编写观察。复制实际启动及动作 ID，不要生成替代值。提供 `id`、`type: learning-observation`、`start_id`、`action_id`、`outcome`、`finding`、`hypothesis_change`、`resolved_questions`、`artifacts`、`executor`、`reviewer`、`cost` 和 `acceptance_checks`。非 unknown 结果需要存在的根相对路径产物及 SHA-256。未知的原生 token/USD 成本填写 `null`。演练生成的 `inputs/settle-original-start.md` 是具体示例，其中 token 与哈希只属于该次演练。

```sh
python3 -B "$SKILL/scripts/adaptive_learning.py" observe \
  --root "$ROOT" --id "$RUN_ID" \
  --observation "$OBSERVATION_MD" --expected-revision "$CURRENT_REVISION"
```

陈旧修订或不同启动必须被拒绝。保留拒绝回执并重读状态，不要盲目替换预期修订再重发。确认目标待定动作仍是同一个。如果哈希或日志绑定校验失败，保留文件并调查来源；绝不可悄悄重写历史，让工具接受它。

`delivered` 还要求待定动作为 deliver 类型、所有声明验收项均为 true、没有未解决阻断问题，并声明与执行者不同的审阅者。先取得实际独立审阅。工具检查声明与文件身份，不验证审阅是否真实。不要用虚构审阅者结束演练。

## 运行受控演练

需要 Python 3.11+ 和当前 skill 代码检出目录。脚本独立运行，仅写入代码目录之外的新工作目录。路径可以包含空格。不要使用 Python 的 `-O`，因为演练使用断言进行检查。

```sh
python3 -B ./recovery_drill.reviewed.py --skill /path/to/personal-agent-growth --work /path/to/new-recovery-drill
```

演练进行一次排他创建的真实文件写入，有意暂不记录结果观察。这是受控不确定性，不是真实崩溃或基础设施丢失。它记录 unknown，拒绝待定时重新规划，从另一个无效果样例取得真实启动，拒绝该外来 token，检查原文件，并核实原动作而不再次写入效果。主运行随后报告 `action_limit`，因为唯一获准动作已用完。外来 token 样例如实以 failed 关闭，因为其预期效果被有意保留为未尝试。没有虚构交付审阅者。

检查 `summary.json`、`effect-inspection.json`、`controlled-uncertainty.json`、`memory/effect.jsonl`、各编号回执目录及原始日志。`manifest.json` 为生成它之前的全部文件记录哈希。预期有两份退出 2 的回执：待定时重新规划，以及外来 token 拒绝。出现非预期行为时脚本非零退出，并保留 `failure.json` 与之前回执。已有工作目录会被拒绝，不会覆盖。

成功演练仅证明所记录工具哈希下的本地受控行为，不证明生产恢复、任意外部服务的恰好一次执行、自动调度、原生崩溃恢复、人类培训收益，或本经验指导方法更优。delivered 状态与损坏日志恢复根据已检查源码解释，本演练并未执行它们。

来源：所提供 skill 代码目录中的 `scripts/adaptive_learning.py`（`halted`、`apply`、`observation_check`、`append`、`report`）及 `references/adaptive-learning.md`。执行回执绑定准确的工具 SHA-256。本练习只读源码。

审阅修正：原稿重新规划探针使用了过时的计划修订，先触发陈旧计划检查。审阅后演练使用有效的修订 3 提案，并检查准确的待定状态错误；它也检查准确的外来 token 诊断。原脚本与回执继续保留。
